# search/willhaben.py

from typing import List
from database.models import Deal, Product

class WillhabenSearch:
    def search(self, product: Product) -> List[Deal]:
        print(f"Suche nach {product.name} auf Willhaben...")
        # TODO: Implementiere die echte Suche und das Parsen der Ergebnisse
        return []
