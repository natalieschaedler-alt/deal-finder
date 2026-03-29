from typing import Dict, List
from urllib.parse import quote_plus

from database.models import Product
from search.compliance import fetch_public_soup, parse_price_eur


class AmazonWarehouseSearch:
    BASE_URL = "https://www.amazon.de/s"

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
        cards = soup.select("div[data-component-type='s-search-result']")
        for card in cards[:10]:
            text = card.get_text(" ", strip=True)
            price = parse_price_eur(text)
            if price > 0:
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
