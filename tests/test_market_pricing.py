from logic.market_pricing import build_trade_plan, normalize_condition


def test_normalize_condition_maps_common_labels():
    assert normalize_condition("Neu") == "neu"
    assert normalize_condition("Wie neu") == "wie neu"
    assert normalize_condition("Sehr gut") == "sehr gut"
    assert normalize_condition("Gebraucht gut") == "gut"


def test_build_trade_plan_calculates_target_sell_and_max_buy():
    result = build_trade_plan(
        offer_price=380,
        sold_prices=[560, 540, 550],
        fee_rate=0.10,
        fixed_cost_per_sale=5,
        min_net_profit=30,
        offer_condition="sehr gut",
        product_condition="sehr gut",
        fallback_sell_price=520,
    )

    assert result["target_sell_price"] > 0
    assert result["max_buy_price"] > 0
    assert result["expected_net_profit"] > 0
    assert result["roi_percent"] > 0


def test_build_trade_plan_uses_fallback_when_no_sold_prices():
    result = build_trade_plan(
        offer_price=300,
        sold_prices=[],
        fee_rate=0.1,
        fixed_cost_per_sale=5,
        min_net_profit=30,
        offer_condition="gut",
        product_condition="sehr gut",
        fallback_sell_price=450,
    )

    assert result["target_sell_price"] > 0
