from statistics import median
from typing import Dict, List, Optional


def _clean_prices(values: List[float]) -> List[float]:
    return [float(value) for value in values if isinstance(value, (int, float)) and value > 0]


def _safe_median(values: List[float], default: float = 0.0) -> float:
    clean = _clean_prices(values)
    if not clean:
        return float(default)
    return float(median(clean))


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _default_google_trends_score(product_name: str, category: str) -> float:
    text = f"{product_name} {category}".lower()
    if "iphone" in text or "galaxy" in text:
        return 0.78
    if "playstation" in text or "nintendo" in text or "xbox" in text:
        return 0.72
    if "sneaker" in text or "fashion" in text:
        return 0.66
    return 0.55


def _default_bsr_score(category: str) -> float:
    text = str(category or "").lower()
    if "smart" in text or "elektr" in text:
        return 0.68
    if "gaming" in text:
        return 0.7
    return 0.52


def aggregate_market_context(
    *,
    product_name: str,
    category: str,
    sold_prices: List[float],
    active_offer_prices: List[float],
    warehouse_prices: List[float],
    idealo_prices: List[float],
    geizhals_prices: List[float],
    sold_history: Optional[List[dict]] = None,
) -> Dict[str, float | int | None]:
    sold_prices = _clean_prices(sold_prices)
    active_offer_prices = _clean_prices(active_offer_prices)
    warehouse_prices = _clean_prices(warehouse_prices)
    idealo_prices = _clean_prices(idealo_prices)
    geizhals_prices = _clean_prices(geizhals_prices)
    sold_history = sold_history or []

    sold_market = _safe_median(sold_prices)
    active_market = _safe_median(active_offer_prices)
    warehouse_market = _safe_median(warehouse_prices)
    new_price_candidates = idealo_prices + geizhals_prices
    new_price_ceiling = min(new_price_candidates) if new_price_candidates else None

    market_components = [price for price in [sold_market, warehouse_market] if price > 0]
    blended_market_price = _safe_median(market_components, 0.0) if market_components else None
    if new_price_ceiling and blended_market_price > new_price_ceiling:
        blended_market_price = float(new_price_ceiling) * 0.93

    sold_count = len(sold_history) if sold_history else len(sold_prices)
    active_count = len(active_offer_prices)
    sold_active_ratio = (sold_count / active_count) if active_count > 0 else (1.0 if sold_count > 0 else 0.0)
    sold_active_score = _clamp(sold_active_ratio / 1.5, 0.0, 1.0)
    google_trends_score = _default_google_trends_score(product_name, category)
    amazon_bsr_score = _default_bsr_score(category)
    listing_velocity_score = _clamp((sold_count / 10.0), 0.0, 1.0)

    demand_score = round(
        (
            sold_active_score * 0.45
            + google_trends_score * 0.25
            + amazon_bsr_score * 0.20
            + listing_velocity_score * 0.10
        ),
        3,
    )

    return {
        "sold_market_price": round(sold_market, 2) if sold_market else None,
        "active_market_price": round(active_market, 2) if active_market else None,
        "warehouse_market_price": round(warehouse_market, 2) if warehouse_market else None,
        "new_price_ceiling": round(float(new_price_ceiling), 2) if new_price_ceiling else None,
        "market_price": round(float(blended_market_price), 2) if blended_market_price is not None else None,
        "sold_count": sold_count,
        "active_count": active_count,
        "sold_active_ratio": round(sold_active_ratio, 3),
        "google_trends_score": round(google_trends_score, 3),
        "amazon_bsr_score": round(amazon_bsr_score, 3),
        "demand_score": demand_score,
    }
