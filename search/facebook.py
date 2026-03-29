# search/facebook.py

from typing import List
from database.models import Deal, Product

class FacebookMarketplaceSearch:
    def search(self, product: Product) -> List[Deal]:
        print(f"Suche nach {product.name} auf Facebook Marketplace...")
        # Public-only compliance mode: Marketplace is commonly behind login,
        # therefore this connector returns no data unless a public endpoint is available.
        return []
