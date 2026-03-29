from dashboard.filters import filter_deals, sort_deals
from database.models import Deal, Product


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


def make_deal(profit: float, location: str, title: str) -> Deal:
    product = make_product()
    return Deal(
        product=product,
        offer_title=title,
        offer_price=400,
        offer_url="https://example.com",
        location=location,
        condition="sehr gut",
        accessories=["Ladekabel", "OVP"],
        resale_price=400 + profit,
        profit=profit,
        recommendation="Deal" if profit >= 50 else "Kein Deal",
        risk=None,
    )


def test_filter_deals_by_profit_and_location():
    deals = [
        make_deal(100, "Berlin", "A"),
        make_deal(40, "Berlin", "B"),
        make_deal(90, "Hamburg", "C"),
    ]

    filtered = filter_deals(deals, min_profit=50, location="Berlin")

    assert len(filtered) == 1
    assert filtered[0].offer_title == "A"


def test_sort_deals_by_profit_descending():
    deals = [
        make_deal(100, "Berlin", "A"),
        make_deal(60, "Berlin", "B"),
        make_deal(90, "Berlin", "C"),
    ]

    sorted_deals = sort_deals(deals, by="profit", reverse=True)

    assert [d.offer_title for d in sorted_deals] == ["A", "C", "B"]
