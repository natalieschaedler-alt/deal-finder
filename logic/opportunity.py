def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


DEFAULT_WEIGHTS = {
    "price_advantage": 0.15,
    "safety_margin": 0.22,
    "profit": 0.25,
    "roi": 0.18,
    "demand": 0.08,
    "risk": 0.10,
    "image": 0.02,
}


CATEGORY_WEIGHT_OVERRIDES = {
    "smartphone": {
        "profit": 0.28,
        "roi": 0.20,
        "demand": 0.06,
    },
    "elektronik": {
        "profit": 0.27,
        "roi": 0.19,
        "demand": 0.06,
    },
    "fashion": {
        "profit": 0.21,
        "roi": 0.15,
        "demand": 0.16,
        "risk": 0.12,
    },
    "sneaker": {
        "profit": 0.22,
        "roi": 0.15,
        "demand": 0.17,
        "risk": 0.12,
    },
    "gaming": {
        "profit": 0.24,
        "roi": 0.19,
        "demand": 0.10,
        "image": 0.01,
    },
}


def _normalize_category(category: str | None) -> str:
    value = str(category or "").strip().lower()
    if "smart" in value:
        return "smartphone"
    if "elektr" in value or "tech" in value:
        return "elektronik"
    if "fashion" in value or "kleid" in value:
        return "fashion"
    if "sneaker" in value or "schuh" in value:
        return "sneaker"
    if "gaming" in value or "konsole" in value:
        return "gaming"
    return value


def _weights_for_category(category: str | None) -> dict:
    normalized = _normalize_category(category)
    weights = DEFAULT_WEIGHTS.copy()
    overrides = CATEGORY_WEIGHT_OVERRIDES.get(normalized, {})
    weights.update(overrides)

    total = sum(weights.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {key: value / total for key, value in weights.items()}


def calculate_opportunity_score(
    offer_price: float,
    product_max_price: float,
    net_profit: float,
    roi_percent: float,
    demand: float,
    risk_penalty: float,
    max_buy_price: float,
    image_score=None,
    category: str | None = None,
) -> float:
    if offer_price <= 0:
        return 0.0

    price_advantage = _clamp((product_max_price - offer_price) / product_max_price if product_max_price > 0 else 0, 0, 1)
    safety_margin = _clamp((max_buy_price - offer_price) / offer_price, 0, 1)
    profit_score = _clamp(net_profit / 120, 0, 1)
    roi_score = _clamp(roi_percent / 45, 0, 1)
    demand_score = _clamp(demand / 1.3, 0, 1)
    risk_score = _clamp(1 - (risk_penalty / 5), 0, 1)
    image_component = _clamp((image_score or 6) / 10, 0, 1)
    weights = _weights_for_category(category)

    total = (
        price_advantage * weights["price_advantage"]
        + safety_margin * weights["safety_margin"]
        + profit_score * weights["profit"]
        + roi_score * weights["roi"]
        + demand_score * weights["demand"]
        + risk_score * weights["risk"]
        + image_component * weights["image"]
    ) * 100
    return round(total, 1)