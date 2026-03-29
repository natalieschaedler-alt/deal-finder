import hashlib


def build_deal_id(product_name: str, offer_title: str, offer_url: str) -> str:
    raw = f"{product_name}|{offer_title}|{offer_url}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]