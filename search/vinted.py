# search/vinted.py

from typing import List
from urllib.parse import quote_plus, urljoin

from database.models import Deal, Product
from search.compliance import build_compliant_offer, fetch_public_soup, parse_price_eur

class VintedSearch:
    BASE_URL = "https://www.vinted.de/catalog"

    def search(self, product: Product) -> List[Deal]:
        print(f"Suche nach {product.name} auf Vinted...")
        search_url = f"{self.BASE_URL}?search_text={quote_plus(product.name)}"
        soup = fetch_public_soup(search_url, timeout=12)
        if soup is None:
            return []

        results = []
        cards = soup.select("article")
        for card in cards[:10]:
            anchor = card.select_one("a[href]")
            if not anchor:
                continue
            title = anchor.get_text(" ", strip=True)
            href = anchor.get("href", "")
            link = urljoin("https://www.vinted.de", href)
            price = parse_price_eur(card.get_text(" ", strip=True))
            if price <= 0:
                continue

            mapped = build_compliant_offer(
                title=title,
                price=price,
                description=title,
                location="",
                link=link,
                condition=product.condition,
                accessories=product.accessories,
                source_platform="Vinted",
                resale_price=max(product.min_resale_price, price * 1.2),
                seller_rating=0,
                listing_age_days=None,
            )
            if mapped:
                results.append(mapped)
        return results
