import json

import pytest

from database.manager import ProductManager
from database.models import Product


def write_products(path, products):
    path.write_text(json.dumps(products))


def make_product_payload(name="iPhone 13"):
    return {
        "name": name,
        "category": "Smartphone",
        "condition": "sehr gut",
        "accessories": ["Ladekabel"],
        "min_price": 300,
        "max_price": 450,
        "min_profit": 50,
        "min_resale_price": 500,
    }


def test_product_manager_loads_products_from_file(tmp_path):
    product_file = tmp_path / "products.json"
    write_products(product_file, [make_product_payload()])

    manager = ProductManager(str(product_file))

    assert len(manager.products) == 1
    assert manager.products[0].name == "iPhone 13"


def test_product_manager_add_and_remove_product(tmp_path):
    product_file = tmp_path / "products.json"
    write_products(product_file, [make_product_payload("iPhone 13")])
    manager = ProductManager(str(product_file))

    new_product = Product(
        name="Pixel 8",
        category="Smartphone",
        condition="gut",
        accessories=[],
        min_price=250,
        max_price=400,
        min_profit=40,
        min_resale_price=450,
    )

    manager.add_product(new_product)
    after_add = json.loads(product_file.read_text())
    assert len(after_add) == 2

    manager.remove_product("Pixel 8")
    after_remove = json.loads(product_file.read_text())
    assert len(after_remove) == 1
    assert after_remove[0]["name"] == "iPhone 13"


def test_product_manager_get_product_and_missing_error(tmp_path):
    product_file = tmp_path / "products.json"
    write_products(product_file, [make_product_payload("iPhone 13")])
    manager = ProductManager(str(product_file))

    found = manager.get_product("iPhone 13")
    assert found.name == "iPhone 13"

    with pytest.raises(ValueError):
        manager.get_product("Nicht vorhanden")
