# logic/demand.py

def estimate_demand(product_name: str) -> float:
    """
    Platzhalter für Nachfrage-Analyse (z.B. Google Trends, Verkaufszahlen).
    Gibt einen Wert zwischen 0.5 (niedrig) und 1.5 (hoch) zurück.
    """
    # TODO: Echte Nachfrage-Analyse implementieren
    if "iPhone" in product_name:
        return 1.3
    return 1.0
