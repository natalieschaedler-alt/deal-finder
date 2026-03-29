from logic.demand import estimate_demand
from logic.market_intelligence import aggregate_market_context
from logic.market_pricing import build_trade_plan


def test_aggregate_market_context_combines_used_and_new_sources():
    context = aggregate_market_context(
        product_name="iPhone 13",
        category="Smartphone",
        sold_prices=[520, 540, 530],
        active_offer_prices=[400, 420, 410],
        warehouse_prices=[560, 550],
        idealo_prices=[699, 709],
        geizhals_prices=[689, 695],
        sold_history=[{"sold_price": 520}, {"sold_price": 540}],
    )

    assert context["market_price"] > 0
    assert context["new_price_ceiling"] == 689
    assert context["demand_score"] > 0
    assert context["sold_active_ratio"] > 0


def test_estimate_demand_uses_market_context_bonus():
    boosted = estimate_demand(
        "Nintendo Switch",
        market_context={
            "sold_active_ratio": 1.2,
            "google_trends_score": 0.8,
            "amazon_bsr_score": 0.75,
            "demand_score": 0.7,
        },
    )
    default = estimate_demand("Nintendo Switch")

    assert boosted > default


def test_build_trade_plan_respects_new_price_ceiling():
    result = build_trade_plan(
        offer_price=380,
        sold_prices=[700, 710, 720],
        fee_rate=0.1,
        fixed_cost_per_sale=5,
        min_net_profit=30,
        offer_condition="sehr gut",
        product_condition="sehr gut",
        fallback_sell_price=690,
        new_price_ceiling=600,
    )

    assert result["target_sell_price"] <= 558
