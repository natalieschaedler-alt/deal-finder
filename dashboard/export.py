# dashboard/export.py
import csv
import json
from database.models import Deal
from typing import List

def export_deals_csv(deals: List[Deal], filename: str = "deals_export.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Deal_ID",
            "Produkt",
            "Plattform",
            "Einkauf",
            "Max_Einkauf",
            "Ziel-Verkauf",
            "Aktiver_Marktwert",
            "Warehouse_Marktwert",
            "Neupreis_Deckel",
            "Netto-Gewinn",
            "ROI_%",
            "Kapital_Effizienz",
            "Chance_Score",
            "Nachfrage_Score",
            "Verkauft_Aktiv_Ratio",
            "Google_Trends_Score",
            "Amazon_BSR_Score",
            "Risiko_Score",
            "Zustand_Score",
            "Verkäufer_Score",
            "Listing_Alter_Tage",
            "Handlung_Farbe",
            "Kaufpuffer",
            "Bild_URL",
            "Bildscore",
            "Bildanalyse",
            "Vision_Score",
            "Vision_Analyse",
            "Vision_Quelle",
            "Verkauft_Anzahl",
            "Verkauft_Median",
            "Verkaufsquellen",
            "Verkaufsverlauf",
            "Datenbasis",
            "Aktion",
            "Empfohlener_Kauf",
            "Budget_Prioritaet",
            "Link",
            "Empfehlung",
            "Risiko",
        ])
        for deal in deals:
            writer.writerow([
                deal.deal_id,
                deal.product.name,
                deal.source_platform,
                f"{deal.offer_price:.2f}",
                f"{(deal.max_buy_price if deal.max_buy_price is not None else deal.offer_price):.2f}",
                f"{(deal.target_sell_price or deal.resale_price):.2f}",
                f"{(deal.active_market_price if deal.active_market_price is not None else 0):.2f}",
                f"{(deal.warehouse_market_price if deal.warehouse_market_price is not None else 0):.2f}",
                f"{(deal.new_price_ceiling if deal.new_price_ceiling is not None else 0):.2f}",
                f"{(deal.net_profit if deal.net_profit is not None else deal.profit):.2f}",
                f"{(deal.roi_percent if deal.roi_percent is not None else 0):.1f}",
                f"{(deal.capital_efficiency if deal.capital_efficiency is not None else 0):.3f}",
                f"{(deal.opportunity_score if deal.opportunity_score is not None else 0):.1f}",
                f"{(deal.demand_score if deal.demand_score is not None else 0):.3f}",
                f"{(deal.sold_active_ratio if deal.sold_active_ratio is not None else 0):.3f}",
                f"{(deal.google_trends_score if deal.google_trends_score is not None else 0):.3f}",
                f"{(deal.amazon_bsr_score if deal.amazon_bsr_score is not None else 0):.3f}",
                f"{(deal.risk_score if deal.risk_score is not None else 0):.3f}",
                f"{(deal.condition_score if deal.condition_score is not None else 0):.3f}",
                f"{(deal.seller_score if deal.seller_score is not None else 0):.1f}",
                f"{(deal.listing_age_days if deal.listing_age_days is not None else 0):.1f}",
                deal.action_color,
                f"{(deal.buy_price_gap if deal.buy_price_gap is not None else 0):.2f}",
                deal.primary_image_url,
                f"{(deal.image_score if deal.image_score is not None else 0):.1f}",
                deal.image_summary,
                f"{(deal.vision_score if deal.vision_score is not None else 0):.1f}",
                deal.vision_summary,
                deal.vision_source,
                str(deal.sold_count),
                f"{(deal.sold_price_median if deal.sold_price_median is not None else 0):.2f}",
                deal.sold_source_summary,
                json.dumps(deal.sold_history or [], ensure_ascii=False),
                deal.price_data_quality,
                deal.buy_decision,
                "ja" if deal.recommended_purchase else "nein",
                deal.budget_priority if deal.budget_priority is not None else "",
                deal.offer_url,
                deal.recommendation,
                deal.risk or "-"
            ])


def export_budget_plan_csv(deals: List[Deal], filename: str = "shopping_plan.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Budget_Prioritaet",
            "Deal_ID",
            "Produkt",
            "Einkauf",
            "Netto-Gewinn",
            "ROI_%",
            "Chance_Score",
            "Kapital_Effizienz",
            "Max_Einkauf",
            "Link",
        ])
        for deal in deals:
            writer.writerow([
                deal.budget_priority if deal.budget_priority is not None else "",
                deal.deal_id,
                deal.product.name,
                f"{deal.offer_price:.2f}",
                f"{(deal.net_profit if deal.net_profit is not None else deal.profit):.2f}",
                f"{(deal.roi_percent if deal.roi_percent is not None else 0):.1f}",
                f"{(deal.opportunity_score if deal.opportunity_score is not None else 0):.1f}",
                f"{(deal.capital_efficiency if deal.capital_efficiency is not None else 0):.3f}",
                f"{(deal.max_buy_price if deal.max_buy_price is not None else deal.offer_price):.2f}",
                deal.offer_url,
            ])
