# dashboard/filters.py
from database.models import Deal
from typing import List

def filter_deals(deals: List[Deal], min_profit: float = 0, location: str = None) -> List[Deal]:
    filtered = [d for d in deals if d.profit >= min_profit]
    if location:
        filtered = [d for d in filtered if d.location.lower() == location.lower()]
    return filtered

def sort_deals(deals: List[Deal], by: str = "profit", reverse: bool = True) -> List[Deal]:
    return sorted(deals, key=lambda d: getattr(d, by), reverse=reverse)
