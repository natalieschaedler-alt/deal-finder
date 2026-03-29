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


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    p = max(0.0, min(1.0, float(p)))
    idx = p * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return float(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac)


def _robust_market_price(sold_prices: List[float], fallback: float) -> float:
    clean = sorted([float(v) for v in sold_prices if isinstance(v, (int, float)) and v > 0])
    if not clean:
        return float(fallback)
    if len(clean) < 4:
        return float(median(clean))

    q1 = _percentile(clean, 0.25)
    q3 = _percentile(clean, 0.75)
    iqr = max(0.0, q3 - q1)
    lower = q1 - (1.5 * iqr)
    upper = q3 + (1.5 * iqr)
    filtered = [v for v in clean if lower <= v <= upper]
    core = filtered if filtered else clean

    central = float(median(core))
    conservative_anchor = _percentile(core, 0.20)
    sample_adjusted = (central * 0.85) + (conservative_anchor * 0.15)
    return max(0.0, float(sample_adjusted))


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
    base_sell = _robust_market_price(sold_prices, fallback_sell_price)

    offer_cond_key = normalize_condition(offer_condition)
    target_cond_key = normalize_condition(product_condition)
    offer_factor = CONDITION_SCORE.get(offer_cond_key, 0.88)
    target_factor = CONDITION_SCORE.get(target_cond_key, 0.88)

    # Conservative sell estimate based on robust sold-price center and condition alignment.
    condition_adjustment = offer_factor / target_factor if target_factor else 1.0
    sample_size = len([v for v in sold_prices if isinstance(v, (int, float)) and v > 0])
    confidence_haircut = 0.98 if sample_size >= 8 else 0.965 if sample_size >= 4 else 0.95
    target_sell_price = max(0, base_sell * condition_adjustment * confidence_haircut)

    net_profit = (target_sell_price * (1 - fee_rate)) - offer_price - fixed_cost_per_sale
    max_buy_price = (target_sell_price * (1 - fee_rate)) - fixed_cost_per_sale - min_net_profit
    roi_percent = (net_profit / offer_price * 100) if offer_price > 0 else 0

    return {
        "target_sell_price": round(target_sell_price, 2),
        "max_buy_price": round(max_buy_price, 2),
        "expected_net_profit": round(net_profit, 2),
        "roi_percent": round(roi_percent, 1),
    }
