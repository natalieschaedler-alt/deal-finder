from database.models import Product
from logic.evaluate import evaluate_deal


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


def test_evaluate_deal_recommends_deal_when_criteria_match():
    product = make_product()

    result = evaluate_deal(
        product=product,
        offer_price=400,
        resale_price=520,
        condition="sehr gut",
        accessories=["Ladekabel", "OVP"],
        location="Berlin",
    )

    assert result["recommendation"] == "Deal"
    assert result["profit"] == 120
    assert result["score"] >= 5


def test_evaluate_deal_marks_no_deal_for_low_profit_and_bad_price():
    product = make_product()

    result = evaluate_deal(
        product=product,
        offer_price=500,
        resale_price=520,
        condition="stark gebraucht",
        accessories=["Ladekabel"],
        location="Berlin",
    )

    assert result["recommendation"] == "Kein Deal"
    assert result["profit"] == 20
    assert "Preis zu hoch" in result["reasons"]
