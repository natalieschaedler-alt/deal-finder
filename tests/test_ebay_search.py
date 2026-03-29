from database.models import Product
from search.ebay import EbaySearch


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


def test_ebay_search_returns_mapped_offers(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "findItemsByKeywordsResponse": [
                    {
                        "searchResult": [
                            {
                                "item": [
                                    {
                                        "title": ["iPhone 13 128GB"],
                                        "viewItemURL": ["https://www.ebay.de/itm/123"],
                                        "galleryURL": ["https://i.ebayimg.com/images/test.jpg"],
                                        "location": ["Berlin"],
                                        "sellingStatus": [
                                            {"currentPrice": [{"__value__": "390.0"}]}
                                        ],
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

    monkeypatch.setenv("EBAY_APP_ID", "demo-app-id")
    monkeypatch.setattr("search.ebay.requests.get", lambda *args, **kwargs: FakeResponse())

    search = EbaySearch()
    offers = search.search(make_product())

    assert len(offers) == 1
    assert offers[0]["offer_title"] == "iPhone 13 128GB"
    assert offers[0]["offer_price"] == 390.0
    assert offers[0]["image_urls"] == ["https://i.ebayimg.com/images/test.jpg"]
    assert offers[0]["resale_price"] >= 500


def test_ebay_search_returns_empty_without_api_key(monkeypatch):
    monkeypatch.delenv("EBAY_APP_ID", raising=False)

    search = EbaySearch()
    monkeypatch.setattr(search.config, "get", lambda *args, **kwargs: "")
    offers = search.search(make_product())

    assert offers == []


def test_ebay_market_metrics_include_sale_history(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "findCompletedItemsResponse": [
                    {
                        "searchResult": [
                            {
                                "item": [
                                    {
                                        "title": ["iPhone 13 verkauft"],
                                        "viewItemURL": ["https://www.ebay.de/itm/999"],
                                        "sellingStatus": [
                                            {"currentPrice": [{"__value__": "455.0"}]}
                                        ],
                                        "condition": [
                                            {"conditionDisplayName": ["Sehr gut"]}
                                        ],
                                        "listingInfo": [
                                            {"endTime": ["2026-03-01T10:20:30.000Z"]}
                                        ],
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

    monkeypatch.setenv("EBAY_APP_ID", "demo-app-id")
    monkeypatch.setattr("search.ebay.requests.get", lambda *args, **kwargs: FakeResponse())

    search = EbaySearch()
    metrics = search.get_market_metrics(make_product())

    assert metrics["sold_prices"] == [455.0]
    assert metrics["sold_by_condition"]["sehr gut"] == [455.0]
    assert len(metrics["sold_history"]) == 1
    assert metrics["sold_history"][0]["source"] == "eBay"
    assert metrics["sold_history"][0]["sold_date"] == "2026-03-01"
    assert metrics["sold_history"][0]["sold_price"] == 455.0


def test_ebay_market_metrics_empty_without_api_key(monkeypatch):
    monkeypatch.delenv("EBAY_APP_ID", raising=False)
    search = EbaySearch()
    monkeypatch.setattr(search.config, "get", lambda *args, **kwargs: "")

    metrics = search.get_market_metrics(make_product())

    assert metrics == {"sold_prices": [], "sold_by_condition": {}, "sold_history": []}
