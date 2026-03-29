# logic/evaluate.py

from database.models import Deal, Product
from typing import List

def evaluate_deal(product: Product, offer_price: float, resale_price: float, condition: str, accessories: List[str], location: str) -> dict:
    # Bewertungskriterien
    score = 0
    reasons = []

    # Preisbewertung
    if offer_price <= product.max_price:
        score += 2
        reasons.append("Preis unter Maximalpreis")
    else:
        reasons.append("Preis zu hoch")

    # Zustand
    if condition.lower() == product.condition.lower():
        score += 1
        reasons.append("Zustand passt")
    else:
        reasons.append("Zustand abweichend")

    # Zubehör
    if product.accessories:
        matched = set(product.accessories) & set(accessories)
        if matched == set(product.accessories):
            score += 1
            reasons.append("Alles Zubehör vorhanden")
        else:
            reasons.append("Zubehör unvollständig")

    # Gewinn
    profit = resale_price - offer_price
    if profit >= product.min_profit:
        score += 2
        reasons.append("Gewinn ausreichend")
    else:
        reasons.append("Gewinn zu gering")

    # Standort (optional, z.B. nur bestimmte Städte bevorzugen)
    # Hier kann weitere Logik ergänzt werden

    recommendation = "Deal" if score >= 5 else "Kein Deal"
    return {
        "score": score,
        "reasons": reasons,
        "profit": profit,
        "recommendation": recommendation
    }
