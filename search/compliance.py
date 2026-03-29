import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?:\+?\d[\d\s()./-]{6,}\d)")
_ADDRESS_RE = re.compile(
    r"\b([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){0,3})\s+(?:str\.?|straße|weg|allee|platz|gasse)\s*\d+[a-zA-Z]?\b",
    flags=re.IGNORECASE,
)
_ADDRESS_SIMPLE_RE = re.compile(
    r"\b[A-ZÄÖÜ][A-Za-zÄÖÜäöüß-]*(?:straße|str\.?|weg|allee|platz|gasse)\s*\d+[a-zA-Z]?\b",
    flags=re.IGNORECASE,
)
_PRICE_RE = re.compile(r"(\d{1,3}(?:[.\s]\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?)")

DEFAULT_HEADERS = {
    "User-Agent": "DealFinderBot/1.0 (+private analysis; respectful rate limits)",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}


def sanitize_text(text: str) -> str:
    value = str(text or "")
    value = _EMAIL_RE.sub("[redacted-email]", value)
    value = _PHONE_RE.sub("[redacted-phone]", value)
    value = _ADDRESS_RE.sub("[redacted-address]", value)
    value = _ADDRESS_SIMPLE_RE.sub("[redacted-address]", value)
    return " ".join(value.split())


def extract_city_region(raw_location: str) -> str:
    location = sanitize_text(raw_location)
    if not location:
        return ""
    parts = [part.strip() for part in location.split(",") if part.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]}, {parts[1]}"


def is_public_listing_url(url: str) -> bool:
    parsed = urlparse(str(url or "").strip())
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.netloc or "").lower()
    if not host:
        return False
    blocked_fragments = ["login", "signin", "captcha", "auth", "account"]
    path = (parsed.path or "").lower()
    query = (parsed.query or "").lower()
    text = f"{path} {query}"
    return not any(fragment in text for fragment in blocked_fragments)


def parse_price_eur(text: str) -> float:
    value = str(text or "")
    match = _PRICE_RE.search(value.replace("EUR", "").replace("€", ""))
    if not match:
        return 0.0
    raw = match.group(1).replace(".", "").replace(" ", "").replace(",", ".")
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 0.0


def fetch_public_soup(url: str, params: Optional[dict] = None, timeout: int = 12) -> Optional[BeautifulSoup]:
    if not is_public_listing_url(url):
        return None
    try:
        response = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)
        response.raise_for_status()
    except Exception:
        return None
    return BeautifulSoup(response.text, "html.parser")


def infer_condition_and_accessories(
    text: str,
    fallback_condition: str,
    expected_accessories: Optional[List[str]],
) -> Dict[str, object]:
    source = str(text or "").lower()
    condition = fallback_condition

    if "wie neu" in source:
        condition = "wie neu"
    elif "neu" in source:
        condition = "neu"
    elif "sehr gut" in source:
        condition = "sehr gut"
    elif "gut" in source or "gebraucht" in source:
        condition = "gut"
    elif "akzeptabel" in source:
        condition = "akzeptabel"
    elif "defekt" in source or "kaputt" in source:
        condition = "defekt"

    accessories = []
    for item in expected_accessories or []:
        if str(item).strip().lower() in source:
            accessories.append(item)

    return {"condition": condition, "accessories": accessories}


def build_compliant_offer(
    *,
    title: str,
    price: float,
    description: str,
    location: str,
    link: str,
    condition: str,
    accessories: Optional[List[str]],
    source_platform: str,
    resale_price: float,
    seller_rating: float,
    listing_age_days: Optional[float],
    image_urls: Optional[List[str]] = None,
) -> Optional[Dict]:
    if not is_public_listing_url(link):
        return None

    clean_title = sanitize_text(title)
    clean_description = sanitize_text(description)
    clean_location = extract_city_region(location)

    inferred = infer_condition_and_accessories(
        text=f"{clean_title} {clean_description}",
        fallback_condition=condition,
        expected_accessories=accessories,
    )

    return {
        "offer_title": clean_title,
        "offer_price": float(price or 0),
        "offer_description": clean_description,
        "offer_url": link,
        "location": clean_location,
        "condition": inferred["condition"],
        "accessories": inferred["accessories"],
        "source_platform": source_platform,
        "resale_price": float(resale_price or 0),
        "seller_rating": float(seller_rating or 0),
        "listing_age_days": listing_age_days,
        "is_fake": False,
        "image_urls": image_urls or [],
    }
