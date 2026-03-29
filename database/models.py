# database/models.py

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Product:
    name: str
    category: str
    condition: str
    accessories: Optional[List[str]]
    min_price: float
    max_price: float
    min_profit: float
    min_resale_price: float

@dataclass
class Deal:
    product: Product
    offer_title: str
    offer_price: float
    offer_url: str
    location: str
    condition: str
    accessories: Optional[List[str]]
    resale_price: float
    profit: float
    recommendation: str  # "Deal" oder "Kein Deal"
    risk: Optional[str] = None
    target_sell_price: Optional[float] = None
    max_buy_price: Optional[float] = None
    net_profit: Optional[float] = None
    roi_percent: Optional[float] = None
    buy_decision: str = "WARTEN"
    price_data_quality: str = "Fallback"
    sold_count: int = 0
    sold_price_median: Optional[float] = None
    sold_source_summary: str = ""
    sold_history: Optional[List[dict]] = None
    image_score: Optional[float] = None
    image_summary: str = ""
    vision_score: Optional[float] = None
    vision_summary: str = ""
    vision_source: str = "Heuristik"
    opportunity_score: Optional[float] = None
    buy_price_gap: Optional[float] = None
    capital_efficiency: Optional[float] = None
    budget_priority: Optional[int] = None
    recommended_purchase: bool = False
    deal_id: str = ""
    source_platform: str = ""
    primary_image_url: str = ""
    seller_score: Optional[float] = None
