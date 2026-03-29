# database/manager.py
import json
from typing import List
from database.models import Product

class ProductManager:
    def __init__(self, filepath: str = "database/products.json"):
        self.filepath = filepath
        self.products = self.load_products()

    def load_products(self) -> List[Product]:
        with open(self.filepath, "r") as f:
            data = json.load(f)
        products = []
        for entry in data:
            products.append(Product(
                name=entry["name"],
                category=entry["category"],
                condition=entry["condition"],
                accessories=entry.get("accessories", []),
                min_price=entry["min_price"],
                max_price=entry["max_price"],
                min_profit=entry["min_profit"],
                min_resale_price=entry["min_resale_price"]
            ))
        return products

    def save_products(self):
        data = [product.__dict__ for product in self.products]
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def add_product(self, product: Product):
        self.products.append(product)
        self.save_products()

    def remove_product(self, name: str):
        self.products = [p for p in self.products if p.name != name]
        self.save_products()

    def get_product(self, name: str) -> Product:
        for p in self.products:
            if p.name == name:
                return p
        raise ValueError(f"Produkt '{name}' nicht gefunden.")
