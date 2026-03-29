# logic/advanced_evaluate.py
from database.models import Product
from typing import List, Dict
import math

def advanced_evaluate_deal(product: Product, offer_price: float, resale_price: float, condition: str, accessories: List[str], location: str, demand: float = 1.0, risk_factors: Dict[str, float] = None) -> dict:
    """
    Bewertet ein Angebot mit gewichteten Kriterien:
    - Preis, Zustand, Zubehör, Gewinn, Nachfrage, Risiko, Standort
    """
    score = 0
    reasons = []
    weights = {
        "price": 0.25,
        "condition": 0.15,
        "accessories": 0.10,
        "profit": 0.25,
        "demand": 0.15,
        "risk": 0.10
    }

    # Preisbewertung
    if offer_price <= product.max_price:
        score += weights["price"] * 10
        reasons.append("Preis unter Maximalpreis")
    else:
        reasons.append("Preis zu hoch")

    # Zustand
    if condition.lower() == product.condition.lower():
        score += weights["condition"] * 10
        reasons.append("Zustand passt")
    else:
        reasons.append("Zustand abweichend")

    # Zubehör
    if product.accessories:
        matched = set(product.accessories) & set(accessories)
        if matched == set(product.accessories):
            score += weights["accessories"] * 10
            reasons.append("Alles Zubehör vorhanden")
        else:
            reasons.append("Zubehör unvollständig")

    # Gewinn
    profit = resale_price - offer_price
    if profit >= product.min_profit:
        score += weights["profit"] * 10
        reasons.append("Gewinn ausreichend")
    else:
        reasons.append("Gewinn zu gering")

    # Nachfrage (z.B. von externen Tools/Statistiken)
    if demand >= 1.0:
        score += weights["demand"] * 10
        reasons.append("Nachfrage hoch")
    else:
        reasons.append("Nachfrage gering")

    # Risikoanalyse (z.B. Fake-Angebot, Standort, Verkäuferbewertung)
    risk_penalty = 0
    if risk_factors:
        for k, v in risk_factors.items():
            risk_penalty += v
            reasons.append(f"Risiko: {k} ({v})")
    score -= weights["risk"] * risk_penalty

    # Standort (optional, z.B. bevorzugte Städte)
    # Hier kann weitere Logik ergänzt werden

    # Score normalisieren
    score = max(0, min(10, score))
    recommendation = "Deal" if score >= 7 else "Kein Deal"
    return {
        "score": round(score, 2),
        "reasons": reasons,
        "profit": profit,
        "recommendation": recommendation
    }
