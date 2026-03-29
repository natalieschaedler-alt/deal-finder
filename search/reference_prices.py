from typing import Dict, List
from urllib.parse import quote_plus

from database.models import Product
from search.compliance import fetch_public_soup, parse_price_eur


class ReferencePriceSearch:
    IDEALO_URL = "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html"
    GEIZHALS_URL = "https://geizhals.de/"

    @staticmethod
    def _price_bounds(product: Product) -> tuple[float, float]:
        minimum = max(30.0, float(product.min_price) * 0.8)
        maximum = max(float(product.min_resale_price) * 2.0, float(product.max_price) * 3.0, minimum)
        return minimum, maximum

    def _collect_prices(self, url: str, product: Product, params: dict | None = None) -> List[float]:
        soup = fetch_public_soup(url, params=params, timeout=12)
        if soup is None:
            return []

        minimum, maximum = self._price_bounds(product)
        prices: List[float] = []

        preferred_selectors = [
            ".oopStage-price .oopStage-price-text",
            ".sr-detailedPricingInfo__price",
            ".gh_price",
            ".offer__price",
            "[data-testid='price']",
        ]
        for selector in preferred_selectors:
            for node in soup.select(selector):
                price = parse_price_eur(node.get_text(" ", strip=True))
                if minimum <= price <= maximum:
                    prices.append(price)
                if len(prices) >= 12:
                    break
            if len(prices) >= 12:
                break

        if prices:
            return prices[:12]

        for text in soup.stripped_strings:
            price = parse_price_eur(text)
            if minimum <= price <= maximum:
                prices.append(price)
            if len(prices) >= 12:
                break
        return prices

    def get_market_context(self, product: Product) -> Dict:
        idealo_prices = self._collect_prices(self.IDEALO_URL, product, params={"q": product.name})
        geizhals_prices = self._collect_prices(f"{self.GEIZHALS_URL}?fs={quote_plus(product.name)}", product)
        all_new_prices = idealo_prices + geizhals_prices

        return {
            "idealo_prices": idealo_prices,
            "geizhals_prices": geizhals_prices,
            "new_price_ceiling": min(all_new_prices) if all_new_prices else None,
            "source": "Idealo/Geizhals",
        }
