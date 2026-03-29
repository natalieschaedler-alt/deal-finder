# dashboard/web.py
import json

import pandas as pd
import streamlit as st

from config.manager import ConfigManager
from database.deal_actions import load_deal_actions, save_deal_action
from database.live_data_archive import load_snapshots, summarize_snapshots
from database.manager import ProductManager
from database.models import Product
from logic.deal_identity import build_deal_id
from logic.workflow import run_search_workflow


APP_CSS = """
<style>
    :root {
        --bg-main: #0b0f14;
        --bg-alt: #121821;
        --surface-strong: rgba(16, 22, 30, 0.97);
        --surface-soft: rgba(18, 24, 33, 0.94);
        --surface-card: rgba(20, 27, 36, 0.96);
        --border-soft: rgba(255, 255, 255, 0.08);
        --text-main: #f5f7fb;
        --text-muted: #94a3b8;
        --green: #35d07f;
        --red: #ff6b6b;
        --yellow: #f4c84f;
        --blue: #68a7ff;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(53, 208, 127, 0.11), transparent 28%),
            radial-gradient(circle at top right, rgba(104, 167, 255, 0.10), transparent 24%),
            linear-gradient(180deg, #090d12 0%, #0f141b 100%);
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(53, 208, 127, 0.11), transparent 28%),
            radial-gradient(circle at top right, rgba(104, 167, 255, 0.10), transparent 24%),
            linear-gradient(180deg, #090d12 0%, #0f141b 100%) !important;
    }
    [data-testid="stHeader"] {
        background: rgba(9, 13, 18, 0.76) !important;
    }
    section[data-testid="stSidebar"] {
        background: rgba(9, 13, 18, 0.95) !important;
        border-right: 1px solid var(--border-soft);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-main) !important;
    }
    .block-container {
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .stApp, .block-container {
        color: var(--text-main);
    }
    p, li, label, .stMarkdown, .stText, .stCaption {
        font-size: 1.02rem;
        line-height: 1.55;
        color: var(--text-main);
    }
    h1, h2, h3 {
        font-family: Avenir Next, Futura, Segoe UI, sans-serif;
        letter-spacing: -0.02em;
        color: var(--text-main);
    }
    h1 { font-size: 2.1rem; }
    h2 { font-size: 1.55rem; }
    h3 { font-size: 1.2rem; }
    .hero-card {
        padding: 1.65rem 1.7rem;
        border-radius: 28px;
        background: var(--surface-strong);
        border: 1px solid var(--border-soft);
        box-shadow: 0 20px 52px rgba(0, 0, 0, 0.28);
        backdrop-filter: blur(10px);
    }
    .hero-card p {
        font-size: 1.06rem;
        color: var(--text-muted);
    }
    .eyebrow {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: var(--green);
        font-weight: 800;
        margin-bottom: 0.8rem;
    }
    .hero-grid {
        display: grid;
        grid-template-columns: 1.45fr 0.85fr;
        gap: 1rem;
    }
    .hero-stat {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 1rem;
    }
    .metric-card {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(20, 27, 36, 0.96) 0%, rgba(15, 21, 29, 0.98) 100%);
        border: 1px solid var(--border-soft);
        min-height: 112px;
    }
    .metric-label {
        font-size: 0.88rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 0.35rem;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-main);
    }
    .metric-sub {
        font-size: 0.93rem;
        color: var(--text-muted);
        margin-top: 0.2rem;
    }
    .section-card {
        padding: 1rem 1.1rem;
        border-radius: 20px;
        background: var(--surface-soft);
        border: 1px solid var(--border-soft);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.24);
    }
    .top-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.95rem;
        margin: 1rem 0 1.35rem;
    }
    .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 0.85rem;
        margin: 0.8rem 0 0.25rem;
    }
    .status-card {
        background: var(--surface-card);
        border: 1px solid var(--border-soft);
        border-radius: 18px;
        padding: 0.95rem 1rem;
    }
    .status-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .status-value {
        font-size: 1.08rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 0.22rem;
    }
    .status-note {
        font-size: 0.92rem;
        color: var(--text-muted);
    }
    .checklist-card {
        background: var(--surface-card);
        border: 1px solid var(--border-soft);
        border-radius: 20px;
        padding: 1rem 1.1rem;
    }
    .deal-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }
    .deal-card {
        background: linear-gradient(180deg, rgba(18, 24, 33, 0.98) 0%, rgba(13, 18, 25, 0.98) 100%);
        border: 1px solid var(--border-soft);
        border-radius: 24px;
        padding: 1rem;
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.25);
    }
    .deal-image-slot {
        width: 100%;
        height: 180px;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        overflow: hidden;
        background: linear-gradient(135deg, rgba(53, 208, 127, 0.08) 0%, rgba(255, 255, 255, 0.04) 45%, rgba(244, 200, 79, 0.06) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.9rem 0 0.4rem;
    }
    .deal-image-slot img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .deal-image-placeholder {
        color: var(--text-muted);
        font-size: 0.95rem;
        font-weight: 600;
    }
    .deal-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.8rem;
    }
    .deal-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 0.22rem;
    }
    .deal-subtitle {
        color: var(--text-muted);
        font-size: 0.92rem;
    }
    .score-pill, .signal-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.28rem 0.65rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 800;
        border: 1px solid transparent;
        white-space: nowrap;
    }
    .score-top { background: rgba(53, 208, 127, 0.14); color: var(--green); border-color: rgba(53, 208, 127, 0.26); }
    .score-good { background: rgba(244, 200, 79, 0.12); color: var(--yellow); border-color: rgba(244, 200, 79, 0.24); }
    .score-low { background: rgba(255, 107, 107, 0.12); color: var(--red); border-color: rgba(255, 107, 107, 0.24); }
    .signal-buy { background: rgba(53, 208, 127, 0.14); color: var(--green); border-color: rgba(53, 208, 127, 0.26); }
    .signal-watch { background: rgba(244, 200, 79, 0.12); color: var(--yellow); border-color: rgba(244, 200, 79, 0.24); }
    .signal-risk { background: rgba(255, 107, 107, 0.12); color: var(--red); border-color: rgba(255, 107, 107, 0.24); }
    .deal-metrics {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 1rem 0 0.8rem;
    }
    .deal-metric {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 0.8rem;
    }
    .deal-metric-label {
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.3rem;
    }
    .deal-metric-value {
        font-size: 1.08rem;
        font-weight: 700;
        color: var(--text-main);
    }
    .deal-insights {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-bottom: 0.85rem;
    }
    .insight-chip {
        padding: 0.32rem 0.6rem;
        border-radius: 999px;
        background: rgba(104, 167, 255, 0.10);
        color: #8ebfff;
        font-size: 0.84rem;
        border: 1px solid rgba(104, 167, 255, 0.18);
    }
    .score-breakdown {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.55rem;
        margin: 0.6rem 0 0.9rem;
    }
    .score-part {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 0.7rem;
    }
    .score-part strong {
        display: block;
        color: var(--text-main);
        font-size: 0.9rem;
    }
    .score-part span {
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    .premium-panel {
        background: linear-gradient(135deg, rgba(53, 208, 127, 0.08) 0%, rgba(104, 167, 255, 0.08) 100%), var(--surface-card);
        border: 1px solid var(--border-soft);
        border-radius: 24px;
        padding: 1rem 1.1rem;
    }
    .alert-banner {
        border: 1px solid rgba(53, 208, 127, 0.22);
        background: rgba(53, 208, 127, 0.08);
        color: #b7ffd5;
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin: 1rem 0 0.2rem;
        font-weight: 700;
    }
    .checklist-card ol {
        margin: 0.2rem 0 0;
        padding-left: 1.2rem;
    }
    .checklist-card li {
        margin-bottom: 0.45rem;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-soft);
        border-radius: 12px;
        background: #111720;
    }
    div[data-testid="stDataFrame"] * {
        font-size: 0.96rem !important;
        color: var(--text-main) !important;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 1.02rem;
        font-weight: 600;
        color: var(--text-main);
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: var(--green);
    }
    .stButton > button {
        font-size: 1rem;
        font-weight: 600;
        min-height: 2.65rem;
    }
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stCheckbox label {
        font-size: 0.98rem;
        font-weight: 600;
        color: var(--text-main);
    }
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input {
        background: #111720;
        color: var(--text-main);
        border: 1px solid var(--border-soft);
        font-size: 1rem;
    }
    div[data-baseweb="popover"] * {
        color: var(--text-main) !important;
    }
    div[data-baseweb="menu"] {
        background: #111720 !important;
        border: 1px solid var(--border-soft) !important;
    }
    div[data-baseweb="menu"] li {
        background: #111720 !important;
    }
    .stAlert {
        background: rgba(17, 23, 32, 0.95) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-soft) !important;
    }
    code {
        background: rgba(104, 167, 255, 0.12);
        color: #9cc6ff;
        padding: 0.08rem 0.3rem;
        border-radius: 6px;
    }
    a, a:visited {
        color: #8ebfff !important;
        font-weight: 600;
    }
    @media (max-width: 900px) {
        .block-container {
            padding-top: 1.15rem;
            padding-bottom: 1.8rem;
        }
        h1 { font-size: 1.55rem; }
        h2 { font-size: 1.25rem; }
        h3 { font-size: 1.08rem; }
        p, li, label, .stMarkdown, .stText, .stCaption {
            font-size: 0.98rem;
        }
        .metric-value {
            font-size: 1.55rem;
        }
        .top-strip,
        .deal-grid,
        .hero-grid,
        .deal-metrics {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


def _load_data(csv_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        return pd.DataFrame()


def _load_actions_dataframe(actions_path: str) -> pd.DataFrame:
    actions = load_deal_actions(actions_path)
    if not actions:
        return pd.DataFrame(columns=["deal_id", "product_name", "action", "note", "timestamp"])
    return pd.DataFrame(actions)


def _ensure_deal_ids(deals: pd.DataFrame) -> pd.DataFrame:
    if "Deal_ID" in deals.columns:
        return deals
    deals = deals.copy()
    deals["Deal_ID"] = deals.apply(
        lambda row: build_deal_id(
            str(row.get("Produkt", "")),
            str(row.get("Produkt", "")),
            str(row.get("Link", "")),
        ),
        axis=1,
    )
    return deals


def _load_shopping_plan(csv_path: str = "shopping_plan.csv") -> pd.DataFrame:
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def _load_data_cached(csv_path: str) -> pd.DataFrame:
    return _load_data(csv_path)


@st.cache_data(show_spinner=False)
def _load_actions_cached(actions_path: str) -> pd.DataFrame:
    return _load_actions_dataframe(actions_path)


@st.cache_data(show_spinner=False)
def _load_shopping_plan_cached(csv_path: str = "shopping_plan.csv") -> pd.DataFrame:
    return _load_shopping_plan(csv_path)


@st.cache_data(show_spinner=False)
def _load_snapshots_cached(limit: int = 300) -> list[dict]:
    return load_snapshots(limit=limit)


def _safe_float_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").fillna(0.0)


def _format_currency(value) -> str:
    try:
        return f"{float(value):,.0f} EUR".replace(",", ".")
    except Exception:
        return "-"


def _score_class(score: float) -> str:
    if score >= 90:
        return "score-top"
    if score >= 70:
        return "score-good"
    return "score-low"


def _score_label(score: float) -> str:
    if score >= 90:
        return "Top Deal"
    if score >= 70:
        return "Gut"
    return "Uninteressant"


def _signal_class(action: str) -> str:
    if action == "KAUFEN":
        return "signal-buy"
    if action == "BEOBACHTEN":
        return "signal-watch"
    return "signal-risk"


def _signal_label(row: pd.Series) -> str:
    action = str(row.get("Aktion", "WARTEN"))
    if action == "KAUFEN":
        return "Kaufen"
    if action == "BEOBACHTEN":
        return "Beobachten"
    if action == "IGNORIEREN":
        return "Riskant"
    return "Beobachten"


def _platform_from_link(link: str) -> str:
    link = str(link or "").lower()
    if "ebay" in link:
        return "eBay"
    if "kleinanzeigen" in link:
        return "Kleinanzeigen"
    if "facebook" in link:
        return "Facebook"
    if "vinted" in link:
        return "Vinted"
    if "willhaben" in link:
        return "Willhaben"
    if "shpock" in link:
        return "Shpock"
    return "Marketplace"


def _platform_label(row: pd.Series) -> str:
    explicit = str(row.get("Plattform", "") or "").strip()
    return explicit if explicit else _platform_from_link(str(row.get("Link", "")))


def _speed_label(row: pd.Series) -> str:
    sold_count = float(row.get("Verkauft_Anzahl", 0) or 0)
    score = float(row.get("Chance_Score", 0) or 0)
    if sold_count >= 5 or score >= 90:
        return "schnell"
    if sold_count >= 2 or score >= 70:
        return "mittel"
    return "langsam"


def _safety_label(row: pd.Series) -> str:
    quality = str(row.get("Datenbasis", "Fallback"))
    risk = str(row.get("Risiko", "")).lower()
    seller_score = float(row.get("Verkäufer_Score", row.get("seller_score", 0)) or 0)
    if seller_score >= 80:
        return "Verkäufer sicher"
    if quality == "Echt" and "ok" in risk:
        return "niedriges Risiko"
    if quality == "Echt":
        return "Risiko prüfen"
    return "Demo-Daten"


def _seller_label(row: pd.Series) -> str:
    seller_score = float(row.get("Verkäufer_Score", row.get("seller_score", 0)) or 0)
    if seller_score >= 80:
        return f"Verkäufer sicher ({seller_score:.0f})"
    if seller_score >= 60:
        return f"Verkäufer mittel ({seller_score:.0f})"
    return f"Verkäufer Risiko ({seller_score:.0f})"


def _score_breakdown_html(row: pd.Series) -> str:
    price_gap = float(row.get("Kaufpuffer", row.get("buy_price_gap", 0)) or 0)
    sold_count = float(row.get("Verkauft_Anzahl", 0) or 0)
    vision = str(row.get("Vision_Analyse", "") or "")
    demand_text = "hohe Nachfrage" if sold_count >= 5 else "solide Nachfrage" if sold_count >= 2 else "unsichere Nachfrage"
    image_text = "Bildprüfung positiv" if vision and vision.lower() not in {"-", "", "bildanalyse deaktiviert"} else "Bildprüfung neutral"
    return f"""
    <div class="score-breakdown">
        <div class="score-part"><strong>Preis</strong><span>{price_gap:.0f} EUR Puffer zum Max-Kaufpreis</span></div>
        <div class="score-part"><strong>Nachfrage</strong><span>{demand_text}</span></div>
        <div class="score-part"><strong>Zustand</strong><span>{image_text}</span></div>
    </div>
    """


def _deal_image_html(row: pd.Series) -> str:
    image_url = str(row.get("Bild_URL", row.get("primary_image_url", "")) or "").strip()
    if image_url:
        return f'<div class="deal-image-slot"><img src="{image_url}" alt="{row.get("Produkt", "Deal")}"></div>'
    return '<div class="deal-image-slot"><div class="deal-image-placeholder">Kein Produktbild verfügbar</div></div>'


def _render_arbitrage_panel(deals: pd.DataFrame) -> None:
    st.markdown("### Multi-Plattform-Arbitrage")
    if deals.empty:
        st.info("Noch keine Plattformvergleiche vorhanden.")
        return

    working = deals.copy()
    working["Plattform"] = working.apply(_platform_label, axis=1)
    working["Einkauf"] = _safe_float_series(working, "Einkauf")
    working["Ziel-Verkauf"] = _safe_float_series(working, "Ziel-Verkauf")
    working["Netto-Gewinn"] = _safe_float_series(working, "Netto-Gewinn")

    rows = []
    for product, frame in working.groupby("Produkt"):
        cheapest = frame.sort_values(by="Einkauf", ascending=True).iloc[0]
        highest_market = frame.sort_values(by="Ziel-Verkauf", ascending=False).iloc[0]
        rows.append(
            {
                "Produkt": product,
                "Günstigste Quelle": cheapest["Plattform"],
                "Bester Markt": highest_market["Plattform"],
                "Kauf": _format_currency(cheapest["Einkauf"]),
                "Markt": _format_currency(highest_market["Ziel-Verkauf"]),
                "Netto-Gewinn": f"+{float(cheapest['Netto-Gewinn']):.0f} EUR",
            }
        )

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _category_for_product(products: list[Product]) -> dict:
    return {product.name: product.category for product in products}


def _render_top_strip(deals: pd.DataFrame, products: list[Product]) -> None:
    if deals.empty:
        return

    category_map = _category_for_product(products)
    working = deals.copy()
    working["Netto-Gewinn"] = _safe_float_series(working, "Netto-Gewinn")
    working["Chance_Score"] = _safe_float_series(working, "Chance_Score")
    working["Kategorie"] = working["Produkt"].map(category_map).fillna("Allgemein")

    best_category = "-"
    if not working.empty:
        category_summary = working.groupby("Kategorie")["Netto-Gewinn"].sum().sort_values(ascending=False)
        if not category_summary.empty:
            best_category = str(category_summary.index[0])

    top_deals = int((working["Chance_Score"] >= 90).sum())
    total_profit = working["Netto-Gewinn"].max()
    best_score = int(working["Chance_Score"].max()) if not working.empty else 0

    st.markdown(
        f"""
        <div class="top-strip" style="grid-template-columns: repeat(3, minmax(0, 1fr));">
            <div class="metric-card"><div class="metric-label">Realistisch erzielbarer Gewinn heute</div><div class="metric-value">+{float(total_profit):.0f} EUR</div><div class="metric-sub">Staerkster Deal im Feed</div></div>
            <div class="metric-card"><div class="metric-label">Aktuell kaufbereit</div><div class="metric-value">{top_deals} Top Deal{'s' if top_deals != 1 else ''}</div><div class="metric-sub">Mit sehr starkem Score</div></div>
            <div class="metric-card"><div class="metric-label">Bester Deal Score</div><div class="metric-value">{best_score} / 100</div><div class="metric-sub">Direkte Entscheidungshilfe</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_best_deal_spotlight(deals: pd.DataFrame) -> None:
    if deals.empty:
        return

    working = deals.copy()
    working["Chance_Score"] = _safe_float_series(working, "Chance_Score")
    working["Netto-Gewinn"] = _safe_float_series(working, "Netto-Gewinn")
    working = working.sort_values(by=["Chance_Score", "Netto-Gewinn"], ascending=False)
    row = working.iloc[0]
    score = float(row.get("Chance_Score", 0) or 0)
    signal = _signal_label(row)
    signal_class = _signal_class(str(row.get("Aktion", signal)).upper())

    st.markdown("### Bester Deal jetzt")
    st.markdown(
        f"""
        <div class="deal-card" style="padding:1.35rem;border-radius:28px;">
            <div class="deal-top">
                <div>
                    <div class="deal-title">{row.get('Produkt', '-')}</div>
                    <div class="deal-subtitle">{_platform_label(row)} · Sehr starke Chance im aktuellen Feed</div>
                </div>
                <div class="score-pill {_score_class(score)}">Score {score:.0f}/100</div>
            </div>
            {_deal_image_html(row)}
            <div class="deal-metrics">
                <div class="deal-metric"><div class="deal-metric-label">Kaufpreis</div><div class="deal-metric-value">{_format_currency(row.get('Einkauf', 0))}</div></div>
                <div class="deal-metric"><div class="deal-metric-label">Marktpreis</div><div class="deal-metric-value">{_format_currency(row.get('Ziel-Verkauf', 0))}</div></div>
                <div class="deal-metric"><div class="deal-metric-label">Netto-Gewinn</div><div class="deal-metric-value">+{float(row.get('Netto-Gewinn', 0) or 0):.0f} EUR</div></div>
            </div>
            {_score_breakdown_html(row)}
            <div class="deal-insights">
                <span class="signal-pill {signal_class}">{signal}</span>
                <span class="insight-chip">{_speed_label(row)}</span>
                <span class="insight-chip">{_safety_label(row)}</span>
                <span class="insight-chip">{_seller_label(row)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if str(row.get("Link", "")).strip():
        st.link_button("Angebot öffnen", str(row.get("Link", "")), use_container_width=True)


def _render_alert_banner(deals: pd.DataFrame) -> None:
    if deals.empty:
        return
    top = deals.copy()
    top["Netto-Gewinn"] = _safe_float_series(top, "Netto-Gewinn")
    top["Chance_Score"] = _safe_float_series(top, "Chance_Score")
    top = top.sort_values(by=["Chance_Score", "Netto-Gewinn"], ascending=False)
    best = top.iloc[0]
    if float(best.get("Chance_Score", 0) or 0) >= 80:
        st.markdown(
            f"<div class='alert-banner'>Neuer Deal: +{float(best.get('Netto-Gewinn', 0) or 0):.0f} EUR Gewinn bei {best.get('Produkt', 'Top-Angebot')}</div>",
            unsafe_allow_html=True,
        )


def _render_market_analysis(deals: pd.DataFrame, products: list[Product]) -> None:
    st.markdown("### Marktanalyse")
    if deals.empty:
        st.info("Noch keine Marktsignale vorhanden.")
        return

    category_map = _category_for_product(products)
    working = deals.copy()
    working["Kategorie"] = working["Produkt"].map(category_map).fillna("Allgemein")
    working["Netto-Gewinn"] = _safe_float_series(working, "Netto-Gewinn")
    working["Chance_Score"] = _safe_float_series(working, "Chance_Score")

    summary = (
        working.groupby("Kategorie")
        .agg(Deals=("Produkt", "count"), Gewinn=("Netto-Gewinn", "sum"), Score=("Chance_Score", "mean"))
        .reset_index()
        .sort_values(by=["Gewinn", "Score"], ascending=False)
    )

    if summary.empty:
        st.info("Noch keine Kategorien ausgewertet.")
        return

    def trend_icon(row: pd.Series) -> str:
        if row["Score"] >= 80:
            return "↑"
        if row["Score"] >= 60:
            return "→"
        return "↓"

    summary["Trend"] = summary.apply(trend_icon, axis=1)
    summary["Gewinn"] = summary["Gewinn"].map(lambda value: _format_currency(value))
    summary["Score"] = summary["Score"].round(1)

    st.markdown("<div class='premium-panel'>", unsafe_allow_html=True)
    st.dataframe(summary[["Kategorie", "Trend", "Deals", "Gewinn", "Score"]], use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_deal_cards(filtered: pd.DataFrame) -> None:
    if filtered.empty:
        st.info("Mit diesen Filtern gibt es keine Deals.")
        return

    card_rows = []
    for _, row in filtered.head(12).iterrows():
        score = float(row.get("Chance_Score", 0) or 0)
        signal = _signal_label(row)
        score_class = _score_class(score)
        signal_class = _signal_class(str(row.get("Aktion", signal)).upper())
        platform = _platform_label(row)
        speed = _speed_label(row)
        speed_class = "signal-buy" if speed == "schnell" else "signal-watch" if speed == "mittel" else "signal-risk"
        card_rows.append(
            f"""
            <div class="deal-card">
                <div class="deal-top">
                    <div>
                        <div class="deal-title">{row.get('Produkt', '-')}</div>
                        <div class="deal-subtitle">{platform} · {row.get('Zustand', row.get('Vision_Quelle', 'Marktplatz'))}</div>
                    </div>
                    <div class="score-pill {score_class}">{_score_label(score)} · {score:.0f}/100</div>
                </div>
                {_deal_image_html(row)}
                <div class="deal-metrics">
                    <div class="deal-metric"><div class="deal-metric-label">Kaufpreis</div><div class="deal-metric-value">{_format_currency(row.get('Einkauf', 0))}</div></div>
                    <div class="deal-metric"><div class="deal-metric-label">Gewinn</div><div class="deal-metric-value">+{float(row.get('Netto-Gewinn', 0) or 0):.0f} EUR</div></div>
                    <div class="deal-metric"><div class="deal-metric-label">Score</div><div class="deal-metric-value">{score:.0f}/100</div></div>
                </div>
                {_score_breakdown_html(row)}
                <div class="deal-metrics">
                    <div class="deal-metric"><div class="deal-metric-label">Marktpreis</div><div class="deal-metric-value">{_format_currency(row.get('Ziel-Verkauf', 0))}</div></div>
                    <div class="deal-metric"><div class="deal-metric-label">Geschwindigkeit</div><div class="deal-metric-value">{speed}</div></div>
                    <div class="deal-metric"><div class="deal-metric-label">Verkäufer</div><div class="deal-metric-value">{_seller_label(row)}</div></div>
                </div>
                <div class="deal-insights">
                    <span class="signal-pill {signal_class}">{signal}</span>
                    <span class="signal-pill {speed_class}">{speed}</span>
                    <span class="insight-chip">{_safety_label(row)}</span>
                    <span class="insight-chip">{_seller_label(row)}</span>
                </div>
                <div style="margin-top:0.8rem;">
                    <a href="{row.get('Link', '#')}" target="_blank" style="display:inline-block;padding:0.7rem 0.95rem;border-radius:14px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);text-decoration:none;">Angebot öffnen</a>
                </div>
            </div>
            """
        )

    st.markdown("<div class='deal-grid'>" + "".join(card_rows) + "</div>", unsafe_allow_html=True)


def _build_deals_readable_table(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    table = frame.copy()
    numeric_cols = [
        "Einkauf",
        "Ziel-Verkauf",
        "Netto-Gewinn",
        "ROI_%",
        "Chance_Score",
        "Kapital_Effizienz",
        "Verkauft_Anzahl",
        "Verkauft_Median",
    ]
    for col in numeric_cols:
        if col in table.columns:
            table[col] = pd.to_numeric(table[col], errors="coerce").round(2)

    visible_cols = [
        "Produkt",
        "Plattform",
        "Einkauf",
        "Ziel-Verkauf",
        "Netto-Gewinn",
        "ROI_%",
        "Chance_Score",
        "Verkäufer_Score",
        "Aktion",
        "Empfohlener_Kauf",
        "Kapital_Effizienz",
        "Vision_Analyse",
        "Link",
    ]
    existing_cols = [col for col in visible_cols if col in table.columns]
    table = table[existing_cols]

    rename_map = {
        "ROI_%": "ROI %",
        "Chance_Score": "Chance",
        "Verkäufer_Score": "Verkäufer",
        "Empfohlener_Kauf": "Plan",
        "Kapital_Effizienz": "Effizienz",
        "Vision_Analyse": "Vision",
    }
    return table.rename(columns=rename_map)


def _parse_history(history_value: str) -> pd.DataFrame:
    if not history_value or history_value == "[]":
        return pd.DataFrame()
    try:
        rows = json.loads(history_value)
    except Exception:
        return pd.DataFrame()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def _metric_card(label: str, value: str, subtext: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hero(last_run_summary: str):
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-grid">
                <div>
                    <div class="eyebrow">Deal Intelligence</div>
                    <h1>Finde profitable Deals bevor andere reagieren.</h1>
                    <p>Live bewertet nach Gewinn, Risiko und Verkaufsgeschwindigkeit.</p>
                    <p><strong>Letzter Lauf:</strong> {last_run_summary}</p>
                </div>
                <div class="hero-stat">
                    <div class="metric-label">Status</div>
                    <div class="metric-value">Live bereit</div>
                    <div class="metric-sub">Scan starten, staerksten Deal sehen, schneller handeln.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _status_card(title: str, value: str, note: str) -> str:
    return f"""
    <div class="status-card">
        <div class="status-title">{title}</div>
        <div class="status-value">{value}</div>
        <div class="status-note">{note}</div>
    </div>
    """


def _render_system_status(config: ConfigManager, products_count: int, deals: pd.DataFrame) -> None:
    ebay_ready = bool(config.get("ebay_app_id", ""))
    vision_ready = bool(config.get("vision_api_key", ""))
    fallback_allowed = bool(config.get("allow_demo_fallback_offers", True))
    strict_live_mode = bool(config.get("require_real_market_data", False))
    real_ratio = 0.0
    if not deals.empty and "Datenbasis" in deals.columns:
        real_ratio = float((deals["Datenbasis"] == "Echt").mean() * 100)

    st.markdown("### Systemstatus")
    st.markdown(
        "<div class='status-grid'>"
        + _status_card(
            "Live-Marktdaten",
            "eBay verbunden" if ebay_ready else "Nicht verbunden",
            "Echte Preissignale aus einer Live-Quelle",
        )
        + _status_card(
            "Bildprüfung",
            "Aktivierbar" if vision_ready else "Optional",
            "Bilder koennen zusaetzlich geprueft werden",
        )
        + _status_card(
            "Demo-Daten",
            "Aktiv" if fallback_allowed else "Aus",
            "Zeigt weiterhin Chancen wenn Live-Daten fehlen",
        )
        + _status_card(
            "Echte Verkäufe geprüft",
            "Streng" if strict_live_mode else "Flexibel",
            "Bestimmt wie hart nur echte Marktvergleiche zaehlen",
        )
        + _status_card(
            "Produkte",
            str(products_count),
            "Aktive Zielprodukte fuer die Suche",
        )
        + _status_card(
            "Echt-Daten-Quote",
            f"{real_ratio:.0f}%",
            "Anteil echter Marktquellen in den aktuellen Deals",
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def _render_setup_guide(config: ConfigManager) -> None:
    ebay_ready = bool(config.get("ebay_app_id", ""))
    vision_ready = bool(config.get("vision_api_key", ""))
    strict_live_mode = bool(config.get("require_real_market_data", False))

    st.markdown("### So nutzt jemand das System sinnvoll")
    st.markdown(
        """
        <div class="checklist-card">
            <ol>
                <li>Im Tab <strong>Produkte</strong> Zielprodukte hinterlegen oder anpassen.</li>
                <li>Oben auf <strong>Jetzt scannen</strong> klicken.</li>
                <li>Im Tab <strong>Übersicht / Dashboard</strong> den Top-Deal prüfen.</li>
                <li>Im Tab <strong>Deals Feed</strong> filtern und Entscheidungen speichern.</li>
                <li>Im Tab <strong>Marktanalyse</strong> Trends und echte Verkäufe prüfen.</li>
                <li>Im Tab <strong>Einstellungen / API / Hilfe</strong> Produkte und API-Zugang verwalten.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not ebay_ready:
        st.info("Fuer echte Live-Daten sollte ein eBay App Key in den Streamlit-Secrets hinterlegt werden.")
    if not vision_ready:
        st.info("Vision ist optional. Ohne Key nutzt das System weiterhin die lokale Bild-Heuristik.")
    if strict_live_mode:
        st.warning("Strenger Live-Modus ist aktiv. Dadurch koennen deutlich weniger Deals erscheinen.")


def _render_data_quality_panel() -> None:
    rows = _load_snapshots_cached(limit=300)
    summary = summarize_snapshots(rows)

    st.markdown("### Datenqualitaet")
    if summary["runs"] == 0:
        st.info("Noch kein Suchverlauf vorhanden. Starte mindestens einen Lauf fuer Live-Statistiken.")
        return

    q_cols = st.columns(5)
    with q_cols[0]:
        _metric_card("Archiv-Laeufe", str(summary["runs"]), "Gespeicherte Suchlaeufe")
    with q_cols[1]:
        _metric_card("Angebote", str(summary["total_offers"]), "Im Verlauf gesammelt")
    with q_cols[2]:
        _metric_card("Ø Angebote/Lauf", str(summary["avg_offers_per_run"]), "Treffer pro Lauf")
    with q_cols[3]:
        _metric_card("Ø Marktvergleiche", str(summary["avg_sold_history_per_run"]), "Sold-History je Lauf")
    with q_cols[4]:
        _metric_card("Demo-Anteil", f"{summary['demo_ratio']:.1f}%", "Soll moeglichst niedrig sein")

    platform_counts = summary["platform_counts"]
    if platform_counts:
        sorted_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
        platform_df = pd.DataFrame(sorted_platforms, columns=["Quelle", "Treffer"])
        st.dataframe(platform_df, use_container_width=True, hide_index=True)


def _save_new_product():
    with st.form("new-product-form", clear_on_submit=True):
        name = st.text_input("Produktname")
        category = st.text_input("Kategorie", value="Elektronik")
        condition = st.selectbox("Zielzustand", options=["neu", "wie neu", "sehr gut", "gut", "akzeptabel"])
        accessories = st.text_input("Zubehör", value="Ladekabel")
        price_cols = st.columns(4)
        min_price = price_cols[0].number_input("Min Einkauf", min_value=0.0, value=200.0, step=10.0)
        max_price = price_cols[1].number_input("Max Einkauf", min_value=0.0, value=400.0, step=10.0)
        min_profit = price_cols[2].number_input("Min Gewinn", min_value=0.0, value=50.0, step=10.0)
        min_resale_price = price_cols[3].number_input("Min Verkauf", min_value=0.0, value=500.0, step=10.0)
        submitted = st.form_submit_button("Produkt speichern", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Bitte einen Produktnamen eingeben.")
            return
        manager = ProductManager()
        manager.add_product(
            Product(
                name=name.strip(),
                category=category.strip() or "Elektronik",
                condition=condition,
                accessories=[item.strip() for item in accessories.split(",") if item.strip()],
                min_price=min_price,
                max_price=max_price,
                min_profit=min_profit,
                min_resale_price=min_resale_price,
            )
        )
        st.success("Produkt gespeichert. Du kannst jetzt direkt den One-Click-Lauf starten.")


def start_web_dashboard(csv_path: str = "deals_export.csv", actions_path: str = "database/deal_actions.json"):
    st.set_page_config(page_title="Deal Finder", page_icon=":moneybag:", layout="wide")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    config = ConfigManager()

    if "last_run_summary" not in st.session_state:
        st.session_state["last_run_summary"] = "Noch kein Lauf gestartet"

    _render_hero(st.session_state["last_run_summary"])

    control_cols = st.columns([1.5, 1, 1])
    if control_cols[0].button("Jetzt scannen", use_container_width=True, type="primary"):
        with st.spinner("Suche laeuft, Deals werden neu berechnet..."):
            result = run_search_workflow(show_console=False, enable_notifications=False, export_files=True)
        st.cache_data.clear()
        st.session_state["last_run_summary"] = (
            f"{len(result['deals'])} Deals, {len(result['selected_deals'])} Budget-Käufe, "
            f"Budgetverbrauch {result['budget_plan']['total_spend']:.2f} EUR"
        )
        st.rerun()
    if control_cols[1].button("Daten neu laden", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    if control_cols[2].button("Top-Deals fokussieren", use_container_width=True):
        st.session_state["only_recommended"] = True
        st.rerun()

    deals = _ensure_deal_ids(_load_data_cached(csv_path))
    actions_df = _load_actions_cached(actions_path)
    shopping_plan = _load_shopping_plan_cached()
    current_products = ProductManager().products

    st.caption("Drücke 'Jetzt scannen', um neue Deals mit potenziellem Gewinn zu finden. Danach entscheide in Sekunden: kaufbar, beobachten oder Risiko.")

    if not deals.empty and "Datenbasis" in deals.columns:
        real_ratio = float((deals["Datenbasis"] == "Echt").mean() * 100)
        if real_ratio < 50:
            st.warning(
                "Viele Deals nutzen aktuell Demo-Daten. Fuer maximale Genauigkeit eBay Live-Marktdaten aktivieren."
            )

    _render_alert_banner(deals)

    with st.sidebar:
        st.markdown("## Deal Flow")
        st.markdown("TradingView fuer Gebrauchtwaren: wenige Entscheidungen, klare Signale, hoher Fokus auf Gewinn.")
        st.markdown("### System")
        st.markdown("- Dunkler Premium-Modus")
        st.markdown("- Deal Scores statt Datensalat")
        st.markdown("- Aktionen fuer Kaufen / Beobachten / Risiko")
        st.markdown("### Wichtig")
        st.markdown("Echte Live-Daten werden am besten mit eBay API-Key.")

    tabs = st.tabs(["Übersicht / Dashboard", "Deals Feed", "Marktanalyse", "Einstellungen / API / Hilfe"])

    with tabs[0]:
        _render_top_strip(deals, current_products)
        if deals.empty:
            st.warning("Noch keine Deals vorhanden. Klicke oben auf 'Jetzt scannen'.")
        else:
            _render_best_deal_spotlight(deals)

            plan_left, plan_right = st.columns([1.2, 1])
            with plan_left:
                st.markdown("### Kaufbare Deals")
                if shopping_plan.empty:
                    st.info("Noch keine priorisierte Einkaufsliste vorhanden. Starte zuerst den Scan.")
                else:
                    st.dataframe(shopping_plan, use_container_width=True, hide_index=True)
            with plan_right:
                st.markdown("### Entscheidung zuerst")
                st.markdown("- Kaufbar")
                st.markdown("- Beobachten")
                st.markdown("- Risiko")
                st.markdown("- Geschwindigkeit direkt sichtbar")

    with tabs[1]:
        if deals.empty:
            st.info("Noch keine Deals vorhanden.")
        else:
            st.markdown("### Deal Feed")
            layout_cols = st.columns([0.34, 0.66])
            with layout_cols[0]:
                st.markdown("### Filter")
                products = sorted([value for value in deals.get("Produkt", pd.Series(dtype=str)).dropna().unique().tolist()])
                selected_product = st.selectbox("Kategorie", options=["Alle"] + products)
                min_netto = st.number_input("Mindestgewinn", value=0.0, step=10.0)
                max_price = st.number_input("Preisbereich", value=float(_safe_float_series(deals, 'Einkauf').max() or 0.0), step=25.0)
                platform_options = ["Alle", "eBay", "Kleinanzeigen", "Facebook", "Vinted", "Willhaben", "Shpock", "Marketplace"]
                selected_platform = st.selectbox("Plattform", options=platform_options)
                conditions = sorted([value for value in deals.get("Zustand", pd.Series(dtype=str)).dropna().unique().tolist()])
                selected_condition = st.selectbox("Zustand", options=["Alle"] + conditions)
                has_distance = "Entfernung_km" in deals.columns
                max_distance = st.slider("Entfernung (km)", min_value=0, max_value=500, value=250, step=10, disabled=not has_distance)
                if not has_distance:
                    st.caption("Entfernung wird aktiv, sobald Distanzdaten verfügbar sind.")
                only_buy = st.checkbox("Nur kaufbar", value=True)
                only_recommended = st.checkbox("Nur Top-Angebote", value=st.session_state.get("only_recommended", False))
                st.session_state["only_recommended"] = only_recommended

            filtered = deals.copy()
            filtered["Netto-Gewinn"] = _safe_float_series(filtered, "Netto-Gewinn")
            filtered["Einkauf"] = _safe_float_series(filtered, "Einkauf")
            filtered["Chance_Score"] = _safe_float_series(filtered, "Chance_Score")
            filtered["Plattform"] = filtered.get("Link", pd.Series(dtype=str)).apply(_platform_from_link)
            filtered["Zustand"] = filtered.get("Zustand", pd.Series(dtype=str)).fillna("-")
            filtered = filtered[filtered["Netto-Gewinn"] >= min_netto]
            filtered = filtered[filtered["Einkauf"] <= max_price]
            if only_buy and "Aktion" in filtered.columns:
                filtered = filtered[filtered["Aktion"] == "KAUFEN"]
            if only_recommended and "Empfohlener_Kauf" in filtered.columns:
                filtered = filtered[filtered["Empfohlener_Kauf"] == "ja"]
            if selected_product != "Alle":
                filtered = filtered[filtered["Produkt"] == selected_product]
            if selected_platform != "Alle":
                filtered = filtered[filtered["Plattform"] == selected_platform]
            if selected_condition != "Alle" and "Zustand" in filtered.columns:
                filtered = filtered[filtered["Zustand"] == selected_condition]
            if has_distance and "Entfernung_km" in filtered.columns:
                filtered = filtered[_safe_float_series(filtered, "Entfernung_km") <= float(max_distance)]

            with layout_cols[1]:
                _render_deal_cards(filtered)
                st.markdown("### Tabellenansicht")
                readable = _build_deals_readable_table(filtered)
                st.dataframe(readable, use_container_width=True, hide_index=True)
            if filtered.empty:
                pass
            else:
                selection_options = {
                    f"{row['Produkt']} | {row.get('Einkauf', '-')} EUR | Chance {row.get('Chance_Score', '-')}": row["Deal_ID"]
                    for _, row in filtered.iterrows()
                }
                selected_label = st.selectbox("Deal auswahlen", options=list(selection_options.keys()))
                selected_deal_id = selection_options[selected_label]
                selected_row = filtered[filtered["Deal_ID"] == selected_deal_id].iloc[0]

                detail_cols = st.columns([1.1, 0.9])
                with detail_cols[0]:
                    st.markdown("### Deal-Details")
                    st.markdown(f"**Produkt:** {selected_row.get('Produkt', '-')}")
                    st.markdown(f"**Einkauf:** {selected_row.get('Einkauf', '-')} EUR")
                    st.markdown(f"**Ziel-Verkauf:** {selected_row.get('Ziel-Verkauf', '-')} EUR")
                    st.markdown(f"**Netto-Gewinn:** {selected_row.get('Netto-Gewinn', '-')} EUR")
                    st.markdown(f"**Chance:** {selected_row.get('Chance_Score', '-')} / 100")
                    st.markdown(f"**Kapital-Effizienz:** {selected_row.get('Kapital_Effizienz', '-')} ")
                    st.markdown(f"**Vision:** {selected_row.get('Vision_Quelle', '-')} | {selected_row.get('Vision_Analyse', '-')}")
                    st.markdown(f"**Link:** {selected_row.get('Link', '-')} ")

                with detail_cols[1]:
                    st.markdown("### Aktion")
                    note = st.text_area("Notiz", value="", key=f"note_{selected_deal_id}")
                    action_cols = st.columns(3)
                    if action_cols[0].button("Kaufen", use_container_width=True):
                        save_deal_action(selected_deal_id, selected_row.get("Produkt", ""), "KAUFEN", note, actions_path)
                        st.success("Aktion KAUFEN gespeichert.")
                    if action_cols[1].button("Beobachten", use_container_width=True):
                        save_deal_action(selected_deal_id, selected_row.get("Produkt", ""), "BEOBACHTEN", note, actions_path)
                        st.success("Aktion BEOBACHTEN gespeichert.")
                    if action_cols[2].button("Ignorieren", use_container_width=True):
                        save_deal_action(selected_deal_id, selected_row.get("Produkt", ""), "IGNORIEREN", note, actions_path)
                        st.success("Aktion IGNORIEREN gespeichert.")

                st.markdown("### Verkaufshistorie")
                history = _parse_history(selected_row.get("Verkaufsverlauf", "[]"))
                if history.empty:
                    st.info("Keine dokumentierte Verkaufshistorie vorhanden.")
                else:
                    st.dataframe(history, use_container_width=True, hide_index=True)

    with tabs[2]:
        _render_market_analysis(deals, current_products)
        _render_arbitrage_panel(deals)
        snapshots = _load_snapshots_cached(limit=120)
        st.markdown("### Echte Verkäufe geprüft")
        if not snapshots:
            st.info("Noch keine Markthistorie vorhanden.")
        else:
            runs_df = pd.DataFrame(
                [
                    {
                        "Zeit": row.get("timestamp", ""),
                        "Produkt": row.get("product", ""),
                        "Angebote": row.get("offers_count", 0),
                        "Verkäufe": row.get("market_metrics", {}).get("sold_history_count", 0),
                    }
                    for row in snapshots
                ]
            )
            st.dataframe(runs_df.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)

    with tabs[3]:
        _render_setup_guide(config)
        st.markdown("### Produkte")
        product_frame = pd.DataFrame([
            {
                "Name": product.name,
                "Kategorie": product.category,
                "Zustand": product.condition,
                "Min Einkauf": product.min_price,
                "Max Einkauf": product.max_price,
                "Min Gewinn": product.min_profit,
                "Min Verkauf": product.min_resale_price,
            }
            for product in current_products
        ])
        st.dataframe(product_frame, use_container_width=True, hide_index=True)
        _save_new_product()

        st.markdown("### Gespeicherte Aktionen")
        if actions_df.empty:
            st.info("Noch keine Aktionen gespeichert.")
        else:
            st.dataframe(actions_df.sort_values(by="timestamp", ascending=False), use_container_width=True, hide_index=True)

        st.markdown("### Empfohlene Betriebsmodi")
        modes = pd.DataFrame(
            [
                {
                    "Modus": "Einfach fuer Nutzer",
                    "Live-Daten": "Optional",
                    "Fallback": "An",
                    "Nutzen": "Es erscheinen stabil Deals, auch ohne API",
                },
                {
                    "Modus": "Qualitaetsmodus",
                    "Live-Daten": "eBay API aktiv",
                    "Fallback": "An",
                    "Nutzen": "Gute Mischung aus vielen Deals und echten Marktsignalen",
                },
                {
                    "Modus": "Strenger Live-Modus",
                    "Live-Daten": "Pflicht",
                    "Fallback": "Aus oder ignoriert",
                    "Nutzen": "Nur harte, echte Marktvergleiche zaehlen",
                },
            ]
        )
        st.dataframe(modes, use_container_width=True, hide_index=True)
        st.markdown("### Was verbessert den Nutzen fuer andere am meisten?")
        st.markdown("1. Klare Produktliste mit realistischen Preisgrenzen")
        st.markdown("2. eBay API-Key fuer echte Live-Daten")
        st.markdown("3. Regelmaessiger Suchlauf und gepflegter Aktivitaetsverlauf")
        st.markdown("4. Einfache Kaufregeln statt zu strenger Filter")

        with st.expander("Systemstatus anzeigen", expanded=False):
            _render_system_status(config, len(current_products), deals)

        with st.expander("Technische Datenqualität anzeigen", expanded=False):
            _render_data_quality_panel()


if __name__ == "__main__":
    start_web_dashboard()
