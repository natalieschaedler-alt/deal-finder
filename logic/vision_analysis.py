import json
from typing import Dict, List, Optional

import requests

from logic.image_analysis import analyze_listing_images


def _extract_text(payload: Dict) -> str:
    choices = payload.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = [item.get("text", "") for item in content if isinstance(item, dict)]
        return "\n".join(part for part in text_parts if part)
    return ""


def _safe_json_loads(value: str) -> Optional[Dict]:
    if not value:
        return None
    text = value.strip()
    if text.startswith("```"):
        lines = [line for line in text.splitlines() if not line.startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def inspect_listing_images(
    image_urls: List[str],
    title: str,
    stated_condition: str,
    timeout_seconds: int = 10,
    max_images: int = 3,
    api_key: str = "",
    api_url: str = "https://api.openai.com/v1/chat/completions",
    model: str = "gpt-4.1-mini",
    provider_name: str = "OpenAI-kompatibel",
) -> Dict[str, object]:
    usable_urls = [url for url in image_urls if url][:max_images]
    if not usable_urls:
        fallback = analyze_listing_images([], timeout_seconds=timeout_seconds, max_images=max_images)
        fallback.update(
            {
                "source": "Keine Bilder",
                "damage_flags": [],
                "condition_assessment": stated_condition,
            }
        )
        return fallback

    if not api_key:
        fallback = analyze_listing_images(usable_urls, timeout_seconds=timeout_seconds, max_images=max_images)
        fallback.update(
            {
                "source": "Heuristik",
                "damage_flags": [],
                "condition_assessment": stated_condition,
            }
        )
        return fallback

    prompt = (
        "Analysiere die Produktbilder fur einen Reselling-Dealfinder. "
        "Bewerte sichtbare Schaden, Vollstandigkeit und Wiederverkaufbarkeit. "
        "Antworte nur als JSON mit den Feldern: "
        "score (0-10 Zahl), summary (kurzer deutscher Satz), "
        "damage_flags (Liste kurzer Strings), condition_assessment (deutscher Zustand)."
    )

    content = [{"type": "text", "text": f"Titel: {title}\nAngegebener Zustand: {stated_condition}\n{prompt}"}]
    for url in usable_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=timeout_seconds)
        response.raise_for_status()
        raw_text = _extract_text(response.json())
        parsed = _safe_json_loads(raw_text) or {}
        return {
            "score": parsed.get("score"),
            "summary": parsed.get("summary", "Vision-Analyse ohne Zusammenfassung"),
            "damage_flags": parsed.get("damage_flags", []),
            "condition_assessment": parsed.get("condition_assessment", stated_condition),
            "inspected_count": len(usable_urls),
            "source": provider_name,
        }
    except Exception:
        fallback = analyze_listing_images(usable_urls, timeout_seconds=timeout_seconds, max_images=max_images)
        fallback.update(
            {
                "source": "Heuristik-Fallback",
                "damage_flags": [],
                "condition_assessment": stated_condition,
            }
        )
        return fallback