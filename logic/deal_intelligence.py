from typing import Dict, List, Optional


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _normalize_seller_rating(value: float) -> float:
    rating = float(value or 0)
    if rating <= 5:
        rating *= 20
    return _clamp(rating / 100.0, 0.0, 1.0)


def condition_score(condition: str) -> float:
    normalized = str(condition or "").strip().lower()
    if "neu" in normalized and "wie" not in normalized:
        return 1.0
    if "wie neu" in normalized:
        return 0.95
    if "sehr gut" in normalized:
        return 0.9
    if "gut" in normalized:
        return 0.7
    if "akzept" in normalized:
        return 0.55
    if "defekt" in normalized or "kaputt" in normalized:
        return 0.2
    if "gebraucht" in normalized:
        return 0.7
    return 0.7


def demand_speed_score(listing_age_days: Optional[float], sold_history: Optional[List[dict]] = None, category: str = "") -> float:
    age = listing_age_days
    if age is None:
        sold_count = len(sold_history or [])
        if sold_count >= 8:
            age = 5.0
        elif sold_count >= 4:
            age = 12.0
        elif sold_count >= 1:
            age = 20.0
        else:
            age = 30.0

    age = max(0.0, float(age))
    if age <= 5:
        base = 1.0
    elif age >= 30:
        base = 0.0
    else:
        base = 1.0 - ((age - 5.0) / 25.0)

    category_hint = str(category or "").lower()
    category_boost = 0.0
    if any(token in category_hint for token in ["fashion", "sneaker", "gaming", "trading card"]):
        category_boost = 0.04
    elif any(token in category_hint for token in ["smart", "elektr", "tech"]):
        category_boost = 0.02

    return _clamp(base + category_boost, 0.0, 1.0)


def normalized_profit(net_profit: float, cap_eur: float = 200.0) -> float:
    return _clamp(float(net_profit or 0) / float(cap_eur), 0.0, 1.0)


def listing_speed_label(demand_score_value: float) -> str:
    if demand_score_value >= 0.75:
        return "schnell"
    if demand_score_value >= 0.4:
        return "mittel"
    return "langsam"


def decision_from_score(score_0_100: float, net_profit: float) -> Dict[str, str]:
    score = float(score_0_100 or 0)
    profit = float(net_profit or 0)
    if score >= 75 and profit > 20:
        return {"action": "KAUFEN", "label": "Kaufen", "color": "gruen"}
    if score >= 50:
        return {"action": "BEOBACHTEN", "label": "Beobachten", "color": "gelb"}
    return {"action": "IGNORIEREN", "label": "Finger weg", "color": "rot"}


def compute_deal_intelligence(
    price: float,
    market_price: float,
    category: str,
    condition: str,
    sold_history: Optional[List[dict]],
    listing_age_days: Optional[float],
    seller_rating: float,
    fees: float,
    shipping: float,
    image_score: Optional[float],
    has_live_market_data: bool,
) -> Dict[str, float | str]:
    fee_rate = float(fees or 0)
    shipping_cost = float(shipping or 0)
    market = max(0.0, float(market_price or 0))
    offer = max(0.0, float(price or 0))

    net_profit = market - offer - (market * fee_rate) - shipping_cost
    profit_norm = normalized_profit(net_profit)
    demand_score_value = demand_speed_score(listing_age_days, sold_history=sold_history, category=category)
    cond_score = condition_score(condition)
    seller_score = _normalize_seller_rating(seller_rating)
    risk_score = (cond_score + seller_score) / 2.0

    score = (
        profit_norm * 0.4
        + demand_score_value * 0.3
        + cond_score * 0.2
        + seller_score * 0.1
    )

    if has_live_market_data:
        score += 0.03

    if image_score is not None:
        image_norm = _clamp(float(image_score) / 10.0, 0.0, 1.0)
        if image_norm < 0.5:
            score -= (0.5 - image_norm) * 0.15

    score = _clamp(score, 0.0, 1.0)
    score_100 = round(score * 100.0, 1)
    decision = decision_from_score(score_100, net_profit)

    return {
        "net_profit": round(net_profit, 2),
        "profit_norm": round(profit_norm, 3),
        "demand_score": round(demand_score_value, 3),
        "condition_score": round(cond_score, 3),
        "seller_score": round(seller_score, 3),
        "risk_score": round(risk_score, 3),
        "score": score_100,
        "speed": listing_speed_label(demand_score_value),
        "action": decision["action"],
        "action_label": decision["label"],
        "action_color": decision["color"],
    }
