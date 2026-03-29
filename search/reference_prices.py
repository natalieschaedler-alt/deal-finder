from typing import Dict, List
from urllib.parse import quote_plus

from database.models import Product
from search.compliance import fetch_public_soup, parse_price_eur


class ReferencePriceSearch:
    IDEALO_URL = "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html"
    GEIZHALS_URL = "https://geizhals.de/"

    def _collect_prices(self, url: str, product_name: str) -> List[float]:
        soup = fetch_public_soup(url, params={"q": product_name}, timeout=12)
        if soup is None:
            return []
        prices: List[float] = []
        for text in soup.stripped_strings:
            price = parse_price_eur(text)
            if price > 0:
                prices.append(price)
            if len(prices) >= 12:
                break
        return prices

    def get_market_context(self, product: Product) -> Dict:
        idealo_prices = self._collect_prices(self.IDEALO_URL, product.name)
        geizhals_prices = self._collect_prices(f"{self.GEIZHALS_URL}?fs={quote_plus(product.name)}", product.name)
        all_new_prices = idealo_prices + geizhals_prices

        return {
            "idealo_prices": idealo_prices,
            "geizhals_prices": geizhals_prices,
            "new_price_ceiling": min(all_new_prices) if all_new_prices else None,
            "source": "Idealo/Geizhals",
        }
