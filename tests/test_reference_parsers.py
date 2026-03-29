from database.models import Product
from search.amazon_warehouse import AmazonWarehouseSearch
from search.reference_prices import ReferencePriceSearch


def make_product() -> Product:
    return Product(
        name="iPhone 13",
        category="Smartphone",
        condition="sehr gut",
        accessories=["Ladekabel"],
        min_price=300,
        max_price=450,
        min_profit=50,
        min_resale_price=500,
    )


def test_amazon_warehouse_extract_card_price_prefers_real_price():
    from bs4 import BeautifulSoup

    html = """
    <div data-component-type='s-search-result'>
      <span class='a-price'><span class='a-offscreen'>549,99 EUR</span></span>
      <span>13,00 EUR Versand</span>
    </div>
    """
    card = BeautifulSoup(html, "html.parser").select_one("div")

    assert AmazonWarehouseSearch._extract_card_price(card) == 549.99


def test_reference_price_bounds_filter_unrealistic_values():
    search = ReferencePriceSearch()
    product = make_product()

    prices = [10.0, 25.0, 699.0, 719.0, 5000.0]
    minimum, maximum = search._price_bounds(product)
    filtered = [price for price in prices if minimum <= price <= maximum]

    assert filtered == [699.0, 719.0]
