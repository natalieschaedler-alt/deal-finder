from statistics import median
from typing import Dict, List


CONDITION_SCORE = {
    "neu": 1.0,
    "wie neu": 0.97,
    "sehr gut": 0.94,
    "gut": 0.88,
    "akzeptabel": 0.8,
    "defekt": 0.55,
}


def normalize_condition(value: str) -> str:
    if not value:
        return "gut"
    lower = value.strip().lower()
    if "neu" in lower and "wie" not in lower:
        return "neu"
    if "wie neu" in lower:
        return "wie neu"
    if "sehr" in lower and "gut" in lower:
        return "sehr gut"
    if "gut" in lower:
        return "gut"
    if "akzept" in lower:
        return "akzeptabel"
    if "defekt" in lower or "kaputt" in lower:
        return "defekt"
    return "gut"


def _safe_median(values: List[float], default: float) -> float:
    clean = [v for v in values if isinstance(v, (int, float)) and v > 0]
    if not clean:
        return default
    return float(median(clean))


def build_trade_plan(
    offer_price: float,
    sold_prices: List[float],
    fee_rate: float,
    fixed_cost_per_sale: float,
    min_net_profit: float,
    offer_condition: str,
    product_condition: str,
    fallback_sell_price: float,
) -> Dict[str, float]:
    offer_price = float(offer_price)
    base_sell = _safe_median(sold_prices, fallback_sell_price)

    offer_cond_key = normalize_condition(offer_condition)
    target_cond_key = normalize_condition(product_condition)
    offer_factor = CONDITION_SCORE.get(offer_cond_key, 0.88)
    target_factor = CONDITION_SCORE.get(target_cond_key, 0.88)

    # Conservative sell estimate based on market median and condition alignment.
    condition_adjustment = offer_factor / target_factor if target_factor else 1.0
    target_sell_price = max(0, base_sell * condition_adjustment * 0.97)

    net_profit = (target_sell_price * (1 - fee_rate)) - offer_price - fixed_cost_per_sale
    max_buy_price = (target_sell_price * (1 - fee_rate)) - fixed_cost_per_sale - min_net_profit
    roi_percent = (net_profit / offer_price * 100) if offer_price > 0 else 0

    return {
        "target_sell_price": round(target_sell_price, 2),
        "max_buy_price": round(max_buy_price, 2),
        "expected_net_profit": round(net_profit, 2),
        "roi_percent": round(roi_percent, 1),
    }
