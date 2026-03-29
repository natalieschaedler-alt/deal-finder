import json
from typing import List

from database.models import Product
from logic.market_pricing import build_trade_plan


def discover_best_products(
    search_manager,
    config,
    candidate_file: str = "database/candidate_products.json",
) -> List[Product]:
    try:
        with open(candidate_file, "r") as f:
            candidates = json.load(f)
    except Exception:
        return []

    fee_percent_config = float(config.get("marketplace_fee_percent", 10))
    fee_rate = fee_percent_config / 100 if fee_percent_config > 1 else fee_percent_config
    fixed_cost_per_sale = float(config.get("fixed_cost_per_sale", 5))
    min_profit = float(config.get("discovery_min_profit", 30))
    max_products = int(config.get("discovery_top_n", 5))
    default_condition = config.get("discovery_default_condition", "sehr gut")

    scored = []
    for entry in candidates:
        product = Product(
            name=entry["name"],
            category=entry.get("category", "Sonstiges"),
            condition=entry.get("condition", default_condition),
            accessories=entry.get("accessories", []),
            min_price=float(entry.get("min_price", 0)),
            max_price=float(entry.get("max_price", 100000)),
            min_profit=float(entry.get("min_profit", min_profit)),
            min_resale_price=float(entry.get("min_resale_price", 0)),
        )

        offers = search_manager.search_all(product)
        if not offers:
            continue

        offer_prices = [o.get("offer_price", 0) for o in offers if o.get("offer_price", 0) > 0]
        if not offer_prices:
            continue

        market_metrics = search_manager.get_market_metrics(product)
        sold_prices = market_metrics.get("sold_prices", [])
        market_buy = sum(offer_prices) / len(offer_prices)
        pricing = build_trade_plan(
            offer_price=market_buy,
            sold_prices=sold_prices,
            fee_rate=fee_rate,
            fixed_cost_per_sale=fixed_cost_per_sale,
            min_net_profit=min_profit,
            offer_condition=product.condition,
            product_condition=product.condition,
            fallback_sell_price=max(product.min_resale_price, market_buy * 1.2),
        )
        expected_net = pricing["expected_net_profit"]
        if expected_net < min_profit:
            continue

        product.max_price = round(market_buy, 2)
        product.min_resale_price = pricing["target_sell_price"]
        product.min_profit = round(min_profit, 2)
        scored.append((expected_net, product))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:max_products]]
