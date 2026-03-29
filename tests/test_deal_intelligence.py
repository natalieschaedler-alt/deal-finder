from logic.deal_intelligence import compute_deal_intelligence


def test_deal_intelligence_buy_signal_for_strong_profit_and_speed():
    result = compute_deal_intelligence(
        price=320,
        market_price=560,
        category="Smartphone",
        condition="neu",
        sold_history=[{"sold_price": 540}],
        listing_age_days=2,
        seller_rating=95,
        fees=0.10,
        shipping=5,
        image_score=8,
        has_live_market_data=True,
    )

    assert result["net_profit"] > 20
    assert result["score"] >= 75
    assert result["action"] == "KAUFEN"


def test_deal_intelligence_ignore_for_weak_profit_and_old_listing():
    result = compute_deal_intelligence(
        price=410,
        market_price=480,
        category="Elektronik",
        condition="gebraucht",
        sold_history=[],
        listing_age_days=35,
        seller_rating=60,
        fees=0.10,
        shipping=8,
        image_score=4,
        has_live_market_data=False,
    )

    assert result["score"] < 50
    assert result["action"] == "IGNORIEREN"
