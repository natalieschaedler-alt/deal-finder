from io import BytesIO
from typing import Dict, List

import requests

try:
    from PIL import Image, ImageFilter, ImageStat
except ImportError:  # pragma: no cover - optional dependency fallback
    Image = None
    ImageFilter = None
    ImageStat = None


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _summarize(score: float) -> str:
    if score >= 8:
        return "Bilder wirken hochwertig und klar"
    if score >= 6:
        return "Bilder sind brauchbar"
    if score >= 4:
        return "Bilder sind mittelmassig"
    return "Bilder deuten auf hoheres Risiko hin"


def _score_image_bytes(content: bytes) -> float:
    if Image is None or ImageStat is None or ImageFilter is None:
        return 5.0

    with Image.open(BytesIO(content)) as image:
        rgb_image = image.convert("RGB")
        grayscale = rgb_image.convert("L")
        width, height = rgb_image.size
        pixel_count = width * height

        brightness = ImageStat.Stat(grayscale).mean[0]
        contrast = ImageStat.Stat(grayscale).stddev[0]
        edges = grayscale.filter(ImageFilter.FIND_EDGES)
        sharpness = ImageStat.Stat(edges).mean[0]

    resolution_score = _clamp(pixel_count / 250000, 0, 4)
    brightness_score = max(0, 2 - abs(brightness - 135) / 55)
    contrast_score = _clamp(contrast / 32, 0, 2)
    sharpness_score = _clamp(sharpness / 24, 0, 2)
    return round(resolution_score + brightness_score + contrast_score + sharpness_score, 2)


def analyze_listing_images(image_urls: List[str], timeout_seconds: int = 5, max_images: int = 3) -> Dict[str, object]:
    usable_urls = [url for url in image_urls if url][:max_images]
    if not usable_urls:
        return {
            "score": None,
            "summary": "Keine Bilder vorhanden",
            "inspected_count": 0,
        }

    scores = []
    for url in usable_urls:
        try:
            response = requests.get(url, timeout=timeout_seconds)
            response.raise_for_status()
            scores.append(_score_image_bytes(response.content))
        except Exception:
            continue

    if not scores:
        return {
            "score": None,
            "summary": "Bilder konnten nicht ausgewertet werden",
            "inspected_count": 0,
        }

    final_score = round(sum(scores) / len(scores), 2)
    return {
        "score": final_score,
        "summary": _summarize(final_score),
        "inspected_count": len(scores),
    }