# dashboard/web.py
import json

import pandas as pd
import streamlit as st

from database.deal_actions import load_deal_actions, save_deal_action
from database.manager import ProductManager
from database.models import Product
from logic.deal_identity import build_deal_id
from logic.workflow import run_search_workflow


APP_CSS = """
<style>
    :root {
        --text-main: #18222c;
        --text-muted: #3b4c5a;
        --surface-strong: rgba(255, 255, 255, 0.95);
        --surface-soft: rgba(255, 255, 255, 0.9);
        --border-soft: rgba(22, 32, 44, 0.14);
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 213, 128, 0.35), transparent 28%),
            radial-gradient(circle at top right, rgba(94, 197, 255, 0.28), transparent 24%),
            linear-gradient(180deg, #f6f1e8 0%, #eef3f7 100%);
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(255, 213, 128, 0.35), transparent 28%),
            radial-gradient(circle at top right, rgba(94, 197, 255, 0.28), transparent 24%),
            linear-gradient(180deg, #f6f1e8 0%, #eef3f7 100%) !important;
    }
    [data-testid="stHeader"] {
        background: rgba(246, 241, 232, 0.82) !important;
    }
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.92) !important;
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
        padding: 1.4rem 1.5rem;
        border-radius: 24px;
        background: var(--surface-strong);
        border: 1px solid var(--border-soft);
        box-shadow: 0 18px 48px rgba(25, 42, 70, 0.08);
        backdrop-filter: blur(10px);
    }
    .hero-card p {
        font-size: 1.06rem;
        color: var(--text-main);
    }
    .metric-card {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: var(--surface-soft);
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
        box-shadow: 0 14px 36px rgba(25, 42, 70, 0.06);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-soft);
        border-radius: 12px;
        background: #ffffff;
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
        color: #0f5a9a;
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
        background: #ffffff;
        color: var(--text-main);
        border: 1px solid var(--border-soft);
        font-size: 1rem;
    }
    div[data-baseweb="popover"] * {
        color: var(--text-main) !important;
    }
    div[data-baseweb="menu"] {
        background: #ffffff !important;
        border: 1px solid var(--border-soft) !important;
    }
    div[data-baseweb="menu"] li {
        background: #ffffff !important;
    }
    .stAlert {
        background: rgba(255, 255, 255, 0.93) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-soft) !important;
    }
    code {
        background: rgba(15, 90, 154, 0.08);
        color: #0b4678;
        padding: 0.08rem 0.3rem;
        border-radius: 6px;
    }
    a {
        color: #0f5a9a !important;
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


def _safe_float_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").fillna(0.0)


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
        "Einkauf",
        "Ziel-Verkauf",
        "Netto-Gewinn",
        "ROI_%",
        "Chance_Score",
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
            <h1>Deal Finder Control Room</h1>
            <p>Ein Klick startet Suche, Preislogik, Bildbewertung, Budgetplan und Export. Danach kannst du Deals sofort kaufen, beobachten oder ignorieren.</p>
            <p><strong>Letzter Lauf:</strong> {last_run_summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    if "last_run_summary" not in st.session_state:
        st.session_state["last_run_summary"] = "Noch kein Lauf gestartet"

    _render_hero(st.session_state["last_run_summary"])

    control_cols = st.columns([1.2, 1, 1])
    if control_cols[0].button("Deals jetzt aktualisieren", use_container_width=True, type="primary"):
        with st.spinner("Suche laeuft, Deals werden neu berechnet..."):
            result = run_search_workflow(show_console=False, enable_notifications=False, export_files=True)
        st.session_state["last_run_summary"] = (
            f"{len(result['deals'])} Deals, {len(result['selected_deals'])} Budget-Käufe, "
            f"Budgetverbrauch {result['budget_plan']['total_spend']:.2f} EUR"
        )
        st.rerun()
    if control_cols[1].button("Daten neu laden", use_container_width=True):
        st.rerun()
    if control_cols[2].button("Shopping-Plan fokussieren", use_container_width=True):
        st.session_state["only_recommended"] = True
        st.rerun()

    deals = _ensure_deal_ids(_load_data(csv_path))
    actions_df = _load_actions_dataframe(actions_path)
    shopping_plan = _load_shopping_plan()

    if not deals.empty and "Datenbasis" in deals.columns:
        real_ratio = float((deals["Datenbasis"] == "Echt").mean() * 100)
        if real_ratio < 50:
            st.warning(
                "Viele Deals basieren noch auf Fallback-Daten. Fuer echte Marktdaten bitte ebay_app_id setzen."
            )

    tabs = st.tabs(["Uebersicht", "Deals", "Produkte", "Aktivitaeten"])

    with tabs[0]:
        if deals.empty:
            st.warning("Noch keine Deals vorhanden. Klicke oben auf 'Deals jetzt aktualisieren'.")
        else:
            metric_cols = st.columns(5)
            with metric_cols[0]:
                _metric_card("Deals", str(len(deals)), "Aktuell geladene Kaufkandidaten")
            with metric_cols[1]:
                _metric_card("Durchschnitt Netto", f"{_safe_float_series(deals, 'Netto-Gewinn').mean():.2f} EUR", "Pro angezeigtem Deal")
            with metric_cols[2]:
                _metric_card("Kapitalbedarf", f"{_safe_float_series(deals, 'Einkauf').sum():.2f} EUR", "Wenn du alles kaufen würdest")
            with metric_cols[3]:
                real_ratio = ((deals.get("Datenbasis", pd.Series(dtype=str)) == "Echt").mean() * 100) if not deals.empty else 0
                _metric_card("Echt-Daten", f"{real_ratio:.0f}%", "Live-Marktquellen statt Fallback")
            with metric_cols[4]:
                _metric_card("Historische Sales", str(int(_safe_float_series(deals, 'Verkauft_Anzahl').sum())), "Vergleichsverkäufe in den Daten")

            plan_left, plan_right = st.columns([1.2, 1])
            with plan_left:
                st.markdown("### Beste Einkaufsliste")
                if shopping_plan.empty:
                    st.info("Noch keine Einkaufsliste vorhanden. Starte zuerst den One-Click-Lauf.")
                else:
                    st.dataframe(shopping_plan, use_container_width=True, hide_index=True)
            with plan_right:
                st.markdown("### Schnellstart")
                st.markdown("- Klick auf 'Deals jetzt aktualisieren' startet den kompletten Workflow")
                st.markdown("- In 'Deals' kannst du Details prüfen und Aktionen speichern")
                st.markdown("- In 'Produkte' kannst du neue Zielprodukte hinzufügen")
                st.markdown("- In 'Aktivitaeten' siehst du deinen Verlauf")

    with tabs[1]:
        if deals.empty:
            st.info("Noch keine Deals vorhanden.")
        else:
            st.markdown("### Deals im Klartext")
            filter_cols = st.columns(4)
            min_netto = filter_cols[0].number_input("Mindest Netto-Gewinn", value=0.0, step=10.0)
            max_price = filter_cols[1].number_input("Maximaler Einkauf", value=float(_safe_float_series(deals, 'Einkauf').max() or 0.0), step=25.0)
            only_buy = filter_cols[2].checkbox("Nur KAUFEN", value=True)
            only_recommended = filter_cols[3].checkbox("Nur Shopping-Plan", value=st.session_state.get("only_recommended", False))
            st.session_state["only_recommended"] = only_recommended

            products = sorted([value for value in deals.get("Produkt", pd.Series(dtype=str)).dropna().unique().tolist()])
            selected_product = st.selectbox("Produkt filtern", options=["Alle"] + products)

            filtered = deals.copy()
            filtered["Netto-Gewinn"] = _safe_float_series(filtered, "Netto-Gewinn")
            filtered["Einkauf"] = _safe_float_series(filtered, "Einkauf")
            filtered = filtered[filtered["Netto-Gewinn"] >= min_netto]
            filtered = filtered[filtered["Einkauf"] <= max_price]
            if only_buy and "Aktion" in filtered.columns:
                filtered = filtered[filtered["Aktion"] == "KAUFEN"]
            if only_recommended and "Empfohlener_Kauf" in filtered.columns:
                filtered = filtered[filtered["Empfohlener_Kauf"] == "ja"]
            if selected_product != "Alle":
                filtered = filtered[filtered["Produkt"] == selected_product]

            readable = _build_deals_readable_table(filtered)
            st.dataframe(readable, use_container_width=True, hide_index=True)
            if filtered.empty:
                st.info("Mit diesen Filtern gibt es keine Deals.")
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
        current_products = ProductManager().products
        st.markdown("### Aktuelle Produkte")
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
        st.markdown("### Neues Produkt hinzufügen")
        _save_new_product()

    with tabs[3]:
        st.markdown("### Gespeicherte Aktionen")
        if actions_df.empty:
            st.info("Noch keine Aktionen gespeichert.")
        else:
            st.dataframe(actions_df.sort_values(by="timestamp", ascending=False), use_container_width=True, hide_index=True)
        st.markdown("### App ausprobieren")
        st.markdown("1. Klicke oben auf 'Deals jetzt aktualisieren'.")
        st.markdown("2. Wechsle in den Tab 'Deals'.")
        st.markdown("3. Wähle einen Deal und speichere eine Aktion.")
        st.markdown("4. Prüfe danach den Tab 'Aktivitaeten' oder die Einkaufsliste in 'Uebersicht'.")


if __name__ == "__main__":
    start_web_dashboard()
