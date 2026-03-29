from typing import Dict, List

from database.models import Product
from search.compliance import fetch_public_soup, parse_price_eur


class AmazonWarehouseSearch:
    BASE_URL = "https://www.amazon.de/s"

    @staticmethod
    def _price_bounds(product: Product) -> tuple[float, float]:
        minimum = max(20.0, float(product.min_price) * 0.6)
        maximum = max(float(product.min_resale_price) * 1.25, float(product.max_price) * 2.0, minimum)
        return minimum, maximum

    @staticmethod
    def _extract_card_price(card) -> float:
        whole = card.select_one(".a-price .a-offscreen")
        if whole:
            return parse_price_eur(whole.get_text(" ", strip=True))

        for selector in [".a-price-whole", ".a-color-price", "span.a-price"]:
            node = card.select_one(selector)
            if node:
                price = parse_price_eur(node.get_text(" ", strip=True))
                if price > 0:
                    return price
        return 0.0

    def get_market_context(self, product: Product) -> Dict:
        soup = fetch_public_soup(
            self.BASE_URL,
            params={"k": f"{product.name} gebraucht"},
            timeout=12,
        )
        if soup is None:
            return {"warehouse_prices": [], "condition_labels": [], "source": "Amazon Warehouse"}

        prices: List[float] = []
        conditions: List[str] = []
        minimum, maximum = self._price_bounds(product)
        cards = soup.select("div[data-component-type='s-search-result']")
        for card in cards[:10]:
            text = card.get_text(" ", strip=True)
            price = self._extract_card_price(card)
            if minimum <= price <= maximum:
                prices.append(price)

            lowered = text.lower()
            if "wie neu" in lowered:
                conditions.append("wie neu")
            elif "sehr gut" in lowered:
                conditions.append("sehr gut")
            elif "gut" in lowered:
                conditions.append("gut")
            elif "akzeptabel" in lowered:
                conditions.append("akzeptabel")

        return {
            "warehouse_prices": prices,
            "condition_labels": conditions,
            "source": "Amazon Warehouse",
        }
