# search/ebay.py

import os
from datetime import datetime
from typing import Dict, List

import requests

from config.manager import ConfigManager
from database.models import Product
from search.compliance import build_compliant_offer

class EbaySearch:
    FINDING_API_URL = "https://svcs.ebay.com/services/search/FindingService/v1"

    def __init__(self):
        self.config = ConfigManager()

    @staticmethod
    def _listing_age_days(value: str) -> float | None:
        if not value:
            return None
        try:
            dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return None
        age_seconds = (datetime.utcnow() - dt).total_seconds()
        if age_seconds < 0:
            return 0.0
        return round(age_seconds / 86400.0, 1)

    @staticmethod
    def _to_offer(item: Dict, product: Product) -> Dict:
        selling_status = item.get("sellingStatus", [{}])[0]
        current_price = selling_status.get("currentPrice", [{}])[0]
        offer_price = float(current_price.get("__value__", 0))
        target_resale = max(product.min_resale_price, offer_price * 1.2)
        item_condition = (
            item.get("condition", [{}])[0].get("conditionDisplayName", [product.condition])[0]
            if item.get("condition")
            else product.condition
        )
        listing_start = (
            item.get("listingInfo", [{}])[0].get("startTime", [""])[0]
            if item.get("listingInfo")
            else ""
        )

        return build_compliant_offer(
            title=item.get("title", [product.name])[0],
            price=offer_price,
            description=item.get("subtitle", [""])[0] if item.get("subtitle") else "",
            location=item.get("location", [""])[0],
            link=item.get("viewItemURL", [""])[0],
            condition=item_condition,
            accessories=product.accessories,
            source_platform="eBay",
            resale_price=round(target_resale, 2),
            seller_rating=5,
            listing_age_days=EbaySearch._listing_age_days(listing_start),
            image_urls=[item.get("galleryURL", [""])[0]] if item.get("galleryURL") else [],
        )

    def _request(self, operation_name: str, product_name: str) -> Dict:
        app_id = os.getenv("EBAY_APP_ID") or self.config.get("ebay_app_id", "")
        if not app_id:
            return {}

        global_id = self.config.get("ebay_global_id", "EBAY-DE")
        entries_per_page = int(self.config.get("ebay_result_limit", 10))
        timeout = int(self.config.get("ebay_timeout_seconds", 10))

        params = {
            "OPERATION-NAME": operation_name,
            "SERVICE-VERSION": "1.13.0",
            "SECURITY-APPNAME": app_id,
            "RESPONSE-DATA-FORMAT": "JSON",
            "REST-PAYLOAD": "true",
            "GLOBAL-ID": global_id,
            "keywords": product_name,
            "paginationInput.entriesPerPage": entries_per_page,
        }
        if operation_name == "findCompletedItems":
            params["itemFilter(0).name"] = "SoldItemsOnly"
            params["itemFilter(0).value"] = "true"

        response = requests.get(self.FINDING_API_URL, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def _extract_items(self, payload: Dict, root_key: str) -> List[Dict]:
        return (
            payload
            .get(root_key, [{}])[0]
            .get("searchResult", [{}])[0]
            .get("item", [])
        )

    @staticmethod
    def _to_date(value: str) -> str:
        if not value:
            return ""
        try:
            dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return value[:10]

    def search(self, product: Product) -> List[Dict]:
        print(f"Suche nach {product.name} auf eBay...")

        app_id = os.getenv("EBAY_APP_ID") or self.config.get("ebay_app_id", "")
        if not app_id:
            print("eBay API nicht aktiv: bitte EBAY_APP_ID oder config.json: ebay_app_id setzen.")
            return []

        try:
            payload = self._request("findItemsByKeywords", product.name)
        except Exception as exc:
            print(f"eBay API Fehler: {exc}")
            return []

        raw_items = self._extract_items(payload, "findItemsByKeywordsResponse")

        offers = []
        for item in raw_items:
            try:
                mapped = self._to_offer(item, product)
                if mapped:
                    offers.append(mapped)
            except Exception:
                continue
        return offers

    def get_market_metrics(self, product: Product) -> Dict:
        app_id = os.getenv("EBAY_APP_ID") or self.config.get("ebay_app_id", "")
        if not app_id:
            return {"sold_prices": [], "sold_by_condition": {}, "sold_history": []}

        sold_prices = []
        sold_by_condition = {}
        sold_history = []
        try:
            payload = self._request("findCompletedItems", product.name)
            items = self._extract_items(payload, "findCompletedItemsResponse")
            for item in items:
                selling_status = item.get("sellingStatus", [{}])[0]
                current_price = selling_status.get("currentPrice", [{}])[0]
                price = float(current_price.get("__value__", 0))
                if price <= 0:
                    continue
                sold_prices.append(price)

                raw_cond = (
                    item.get("condition", [{}])[0].get("conditionDisplayName", ["gut"])[0]
                    if item.get("condition")
                    else "gut"
                )
                cond_key = raw_cond.strip().lower()
                sold_by_condition.setdefault(cond_key, []).append(price)

                end_time = (
                    item.get("listingInfo", [{}])[0].get("endTime", [""])[0]
                    if item.get("listingInfo")
                    else ""
                )
                sold_history.append(
                    {
                        "source": "eBay",
                        "sold_date": self._to_date(end_time),
                        "sold_price": round(price, 2),
                        "condition": raw_cond,
                        "title": item.get("title", [product.name])[0],
                        "url": item.get("viewItemURL", [""])[0],
                    }
                )
        except Exception:
            pass

        return {
            "sold_prices": sold_prices,
            "sold_by_condition": sold_by_condition,
            "sold_history": sold_history,
        }
