# logic/risk.py

def estimate_risk(offer: dict) -> dict:
    """
    Platzhalter für Risiko-Analyse (Fake-Angebot, Verkäuferbewertung, Standort).
    Gibt ein dict mit Risikofaktoren und Werten zurück.
    """
    risk = {}
    if offer.get("location", "").lower() not in ["berlin", "münchen", "hamburg"]:
        risk["Unbekannter Standort"] = 1
    if offer.get("seller_rating", 5) < 3:
        risk["Schlechte Verkäuferbewertung"] = 2
    if offer.get("is_fake", False):
        risk["Fake-Angebot"] = 2
    return risk
