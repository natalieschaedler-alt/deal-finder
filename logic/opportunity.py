def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def calculate_opportunity_score(
    offer_price: float,
    product_max_price: float,
    net_profit: float,
    roi_percent: float,
    demand: float,
    risk_penalty: float,
    max_buy_price: float,
    image_score=None,
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

    total = (
        price_advantage * 0.15
        + safety_margin * 0.22
        + profit_score * 0.25
        + roi_score * 0.18
        + demand_score * 0.08
        + risk_score * 0.10
        + image_component * 0.02
    ) * 100
    return round(total, 1)