# Deal-Suchmaschine für Gebrauchtwaren

Dieses Python-Projekt durchsucht automatisch verschiedene Plattformen (z.B. eBay Kleinanzeigen, eBay, Willhaben, Facebook Marketplace, Shpock, Vinted) nach gebrauchten Artikeln, bewertet die Angebote und zeigt nur profitable Deals an.

## Projektstruktur
- `database/` – Produktdatenbank, Preislimits, Varianten, Zubehör
- `search/` – Module für die Suche auf verschiedenen Plattformen
- `logic/` – Deal-Bewertung, Preisvergleich, Gewinnberechnung
- `dashboard/` – Ausgabe und Visualisierung der Deals
- `main.py` – Einstiegspunkt

## Features
- Automatisierte Suche nach neuen Angeboten
- Bewertung nach Preis, Zustand, Zubehör, Standort, Vergleichspreisen und Nachfrage
- Gewinnberechnung und Empfehlung
- Übersichtliche Darstellung der besten Deals

## Installation
1. Python 3.9+ installieren
2. Virtuelle Umgebung anlegen:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Nutzung
```bash
python main.py
```

Beim Start sucht der Dealfinder automatisch nach Angeboten, bewertet sie und zeigt:
- empfohlenen Einkaufspreis (Angebot)
- Ziel-Verkaufspreis
- erwarteten Netto-Gewinn (nach Gebühren/Kosten)
- ROI in Prozent
- Chancen-Score fur den besten Mix aus billig einkaufen, Sicherheitsmarge und Gewinn
- Bildscore fur Angebotsfotos als zusatzliche Zustands-Heuristik
- optionale Vision-Analyse fur sichtbare Schaden, Vollstandigkeit und Wiederverkaufbarkeit
- budgetoptimierte Einkaufsliste fur maximalen Gewinn bei begrenztem Kapital
- Aktion: `KAUFEN` oder `WARTEN`
- Verkaufsquellen mit Historie: wann verkauft, zu welchem Preis, wie oft (wenn Live-Marktdaten vorhanden)

Zusätzliche Steuerung über `config.json`:
- `marketplace_fee_percent`: Gebühren in Prozent (z.B. 10)
- `fixed_cost_per_sale`: Fixkosten pro Verkauf (z.B. 5)
- `min_net_profit`: Mindest-Netto-Gewinn für Aktion `KAUFEN`
- `min_opportunity_score`: Mindest-Chancen-Score fur Kaufempfehlung (Startwert: 30)
- `enable_image_analysis`: aktiviert einfache Bildanalyse fur Listings
- `enable_vision_analysis`: nutzt ein Vision-Modell, wenn API-Key gesetzt ist
- `image_analysis_timeout_seconds`: Timeout pro Bilddownload
- `image_analysis_max_images`: wie viele Bilder pro Listing gepruft werden
- `vision_timeout_seconds`: Timeout fur Vision-Anfragen
- `vision_api_key`: API-Key fur das Vision-Modell
- `vision_api_url`: kompatibler Chat-Completions-Endpunkt
- `vision_model`: Modellname fur Vision-Analyse
- `vision_provider_name`: Anzeigename des Vision-Anbieters
- `max_purchase_budget`: maximales Einkaufsbudget fur die Einkaufsliste
- `max_budget_items`: maximale Anzahl gleichzeitig empfohlener Ankaufe

Automatische Produktfindung (optional):
- `auto_discover_products`: `true` aktiviert automatische Produktauswahl
- `discovery_top_n`: wie viele Top-Produkte verwendet werden
- `discovery_min_profit`: Mindest-Netto-Gewinn für Produktaufnahme
- `discovery_default_condition`: Standardzustand fur Kandidaten

Kandidaten für die automatische Produktauswahl liegen in:
- `database/candidate_products.json`

Hinweis:
- Wenn `auto_discover_products` auf `false` steht, nutzt der Dealfinder nur `database/products.json`.
- Wenn `auto_discover_products` auf `true` steht, werden die besten Kandidaten automatisch gewählt.

Wie "beste Produkte" und Preise berechnet werden:
- Aktive Angebote liefern potenzielle Einkaufspreise.
- Abgeschlossene eBay-Angebote (Sold Items) liefern Markt-Verkaufspreise.
- Der Ziel-Verkaufspreis wird konservativ aus dem Markt-Median und dem Zustand geschätzt.
- Der maximale Einkaufspreis wird aus Ziel-Verkaufspreis, Gebühren, Fixkosten und Mindest-Netto-Gewinn berechnet.
- Eine Bildanalyse bewertet Fotoqualitat als Zusatzsignal fur Zustand und Risiko.
- Wenn ein Vision-API-Key gesetzt ist, werden Bilder zusatzlich mit einem Vision-Modell auf Schaden und Vollstandigkeit gepruft.
- Ein Chancen-Score priorisiert gunstige Einkaufe mit hoher Marge, gutem ROI und Sicherheitsabstand zum Maximalpreis.
- Eine Budgetoptimierung erstellt eine Einkaufsliste, die aus allen Kaufkandidaten die beste Kombination fur dein Kapital auswählt.
- Ein Deal wird nur als `KAUFEN` markiert, wenn der Angebotspreis <= max. Einkaufspreis ist und der Chancen-Score hoch genug ist.

eBay API (legaler Live-Connector):
- `ebay_app_id`: eigener eBay Developer App Key
- `ebay_global_id`: Markt, z.B. `EBAY-DE`
- `ebay_result_limit`: maximale Treffer pro Suche
- `ebay_timeout_seconds`: HTTP-Timeout

Alternativ kann der Key über Umgebungsvariable gesetzt werden:
```bash
export EBAY_APP_ID="DEIN_EBAY_APP_ID"
```

## Web-App für einfache Nutzung
Für andere Nutzer ist die Web-App jetzt der einfachste Einstieg:

```bash
streamlit run dashboard/web.py
```

Die App enthält einen One-Click-Workflow:
1. `Deals jetzt aktualisieren` starten
2. Deals automatisch neu suchen, bewerten und exportieren lassen
3. beste Einkaufsliste im Tab `Uebersicht` prüfen
4. im Tab `Deals` Details ansehen und `Kaufen`, `Beobachten` oder `Ignorieren` speichern
5. im Tab `Produkte` neue Zielprodukte anlegen

Im Dashboard siehst du neben Einkauf/Verkauf auch:
- `Verkauft_Anzahl`: wie oft vergleichbare Artikel verkauft wurden
- `Verkauft_Median`: Median der dokumentierten Verkaufspreise
- `Verkaufsquellen`: z.B. eBay
- `Verkaufsverlauf`: Quelle + Datum + Preis je Vergleichsverkauf
- gespeicherte Aktionen wie `KAUFEN`, `BEOBACHTEN`, `IGNORIEREN`
- eine budgetoptimierte Einkaufsliste aus `shopping_plan.csv`
- Vision-Analyse und Bildbewertung pro Deal

Zum direkten Ausprobieren:
1. `streamlit run dashboard/web.py` ausführen
2. die im Terminal angezeigte lokale URL im Browser öffnen
3. oben auf `Deals jetzt aktualisieren` klicken

## Tests
```bash
pytest -q
```

## Test-Coverage
```bash
pytest --cov=. --cov-report=term-missing -q
```

## Schnell-Check und Voll-Check
```bash
sh scripts/check_quick.sh
sh scripts/check_full.sh
```

- `check-quick`: schneller Kern-Check (wichtige Logik + main-Flow)
- `check-full`: kompletter Testlauf mit Coverage-Report
- Optional: `make check-quick` und `make check-full` (falls `make` installiert ist)

## Hinweis
Die Software kauft nicht automatisch, sondern gibt nur Empfehlungen aus.
