# logic/demand.py

def estimate_demand(product_name: str, market_context: dict | None = None) -> float:
    """
    Schaetzt Nachfrage aus Produktname und optionalem Markt-Kontext.
    Rueckgabe bleibt im Bereich 0.5 bis 1.5 fuer Kompatibilitaet.
    """
    market_context = market_context or {}

    base = 1.0
    if "iPhone" in product_name:
        base = 1.3

    sold_active_ratio = float(market_context.get("sold_active_ratio", 0) or 0)
    google_trends_score = float(market_context.get("google_trends_score", 0) or 0)
    amazon_bsr_score = float(market_context.get("amazon_bsr_score", 0) or 0)
    listing_velocity_score = float(market_context.get("demand_score", 0) or 0)

    bonus = 0.0
    bonus += min(0.2, sold_active_ratio * 0.15)
    bonus += google_trends_score * 0.08
    bonus += amazon_bsr_score * 0.07
    bonus += listing_velocity_score * 0.1

    return max(0.5, min(1.5, round(base + bonus, 2)))
