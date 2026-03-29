# search/kleinanzeigen.py

from typing import List
from urllib.parse import urljoin

from database.models import Deal, Product
from search.compliance import build_compliant_offer, fetch_public_soup, parse_price_eur

class KleinanzeigenSearch:
    BASE_URL = "https://www.kleinanzeigen.de/s-suchanfrage.html"

    def search(self, product: Product) -> List[Deal]:
        print(f"Suche nach {product.name} auf eBay Kleinanzeigen...")
        soup = fetch_public_soup(
            self.BASE_URL,
            params={"keywords": product.name},
            timeout=12,
        )
        if soup is None:
            return []

        results = []
        cards = soup.select("article.aditem")
        for card in cards[:8]:
            title_anchor = card.select_one("a.ellipsis") or card.select_one("a")
            price_node = card.select_one("p.aditem-main--middle--price-shipping--price")
            location_node = card.select_one("div.aditem-main--top--left")
            if not title_anchor:
                continue

            title = title_anchor.get_text(" ", strip=True)
            href = title_anchor.get("href", "")
            link = urljoin("https://www.kleinanzeigen.de", href)
            price = parse_price_eur(price_node.get_text(" ", strip=True) if price_node else "")
            if price <= 0:
                continue

            location = location_node.get_text(" ", strip=True) if location_node else ""
            mapped = build_compliant_offer(
                title=title,
                price=price,
                description=title,
                location=location,
                link=link,
                condition=product.condition,
                accessories=product.accessories,
                source_platform="Kleinanzeigen",
                resale_price=max(product.min_resale_price, price * 1.2),
                seller_rating=0,
                listing_age_days=None,
            )
            if mapped:
                results.append(mapped)
        return results
