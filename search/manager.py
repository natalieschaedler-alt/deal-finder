# search/manager.py
from typing import List
from database.models import Product, Deal
from search.kleinanzeigen import KleinanzeigenSearch
from search.ebay import EbaySearch
from search.willhaben import WillhabenSearch
from search.facebook import FacebookMarketplaceSearch
from search.shpock import ShpockSearch
from search.vinted import VintedSearch
from search.landleanzeiger import LandleanzeigerSearch

class SearchManager:
    def __init__(self):
        self.platforms = [
            KleinanzeigenSearch(),
            EbaySearch(),
            WillhabenSearch(),
            FacebookMarketplaceSearch(),
            ShpockSearch(),
            VintedSearch(),
            LandleanzeigerSearch()
        ]

    def search_all(self, product: Product) -> List[Deal]:
        deals = []
        for platform in self.platforms:
            try:
                results = platform.search(product)
                deals.extend(results)
            except Exception as e:
                print(f"Fehler bei {platform.__class__.__name__}: {e}")
        return deals

    def get_market_metrics(self, product: Product) -> dict:
        merged = {"sold_prices": [], "sold_by_condition": {}, "sold_history": []}
        for platform in self.platforms:
            if not hasattr(platform, "get_market_metrics"):
                continue
            try:
                metrics = platform.get_market_metrics(product)
            except Exception:
                continue

            prices = metrics.get("sold_prices", [])
            merged["sold_prices"].extend(prices)

            by_condition = metrics.get("sold_by_condition", {})
            for cond, values in by_condition.items():
                merged["sold_by_condition"].setdefault(cond, []).extend(values)

            history = metrics.get("sold_history", [])
            merged["sold_history"].extend(history)
        return merged
