from database.models import Product
from logic.advanced_evaluate import advanced_evaluate_deal


def make_product() -> Product:
    return Product(
        name="iPhone 13",
        category="Smartphone",
        condition="sehr gut",
        accessories=["Ladekabel", "OVP"],
        min_price=300,
        max_price=450,
        min_profit=50,
        min_resale_price=500,
    )


def test_advanced_evaluate_returns_deal_for_strong_offer():
    product = make_product()

    result = advanced_evaluate_deal(
        product=product,
        offer_price=380,
        resale_price=560,
        condition="sehr gut",
        accessories=["Ladekabel", "OVP"],
        location="Berlin",
        demand=1.3,
        risk_factors={"seller": 2},
    )

    assert result["recommendation"] == "Deal"
    assert 7 <= result["score"] <= 10


def test_advanced_evaluate_applies_risk_penalty():
    product = make_product()

    low_risk = advanced_evaluate_deal(
        product=product,
        offer_price=380,
        resale_price=560,
        condition="sehr gut",
        accessories=["Ladekabel", "OVP"],
        location="Berlin",
        demand=1.3,
        risk_factors={"seller": 0},
    )

    high_risk = advanced_evaluate_deal(
        product=product,
        offer_price=380,
        resale_price=560,
        condition="sehr gut",
        accessories=["Ladekabel", "OVP"],
        location="Berlin",
        demand=1.3,
        risk_factors={"seller": 20, "fake": 10},
    )

    assert high_risk["score"] < low_risk["score"]
