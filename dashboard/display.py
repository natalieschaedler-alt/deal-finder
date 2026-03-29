# dashboard/display.py

from database.models import Deal
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


def _format_optional_score(value, suffix: str = "") -> str:
    if value is None:
        return "-"
    return f"{value}{suffix}"

def show_deals(deals: List[Deal]):
    console = Console()
    if not deals:
        console.print(Panel("[bold red]Keine profitablen Deals gefunden![/bold red]", title="Ergebnis"))
        return

    best_deal = max(deals, key=lambda d: d.net_profit if d.net_profit is not None else d.profit)
    console.print(
        Panel(
            (
                f"[bold green]Top Deal:[/bold green] {best_deal.product.name}\n"
                f"Einkauf: {best_deal.offer_price:.2f} EUR\n"
                f"Max. Einkauf: {(best_deal.max_buy_price if best_deal.max_buy_price is not None else best_deal.offer_price):.2f} EUR\n"
                f"Ziel-Verkauf: {(best_deal.target_sell_price or best_deal.resale_price):.2f} EUR\n"
                f"Netto-Gewinn: {(best_deal.net_profit if best_deal.net_profit is not None else best_deal.profit):.2f} EUR\n"
                f"ROI: {(best_deal.roi_percent if best_deal.roi_percent is not None else 0):.1f}%\n"
                f"Chance: {(best_deal.opportunity_score if best_deal.opportunity_score is not None else 0):.1f}/100\n"
                f"Kaufpuffer: {(best_deal.buy_price_gap if best_deal.buy_price_gap is not None else 0):.2f} EUR\n"
                f"Kapital-Effizienz: {(best_deal.capital_efficiency if best_deal.capital_efficiency is not None else 0):.3f}\n"
                f"Bildscore: {_format_optional_score(round(best_deal.image_score, 1) if best_deal.image_score is not None else None, '/10')}\n"
                f"Aktion: {best_deal.buy_decision}\n"
                f"Datenbasis: {best_deal.price_data_quality}\n"
                f"Verkaufe (Historie): {best_deal.sold_count}x | Median: {(best_deal.sold_price_median if best_deal.sold_price_median is not None else 0):.2f} EUR\n"
                f"Quelle: {best_deal.sold_source_summary or '-'}\n"
                f"Vision: {best_deal.vision_source} | {best_deal.vision_summary or '-'}\n"
                f"Budget-Prioritat: {best_deal.budget_priority if best_deal.budget_priority is not None else '-'}\n"
                f"Bildanalyse: {best_deal.image_summary or '-'}"
            ),
            title="Bester Deal"
        )
    )

    table = Table(title="[bold green]Profitable Deals[/bold green]", show_lines=True)
    table.add_column("Produkt", style="cyan", no_wrap=True)
    table.add_column("Einkauf", style="magenta")
    table.add_column("Max. Einkauf", style="yellow")
    table.add_column("Verkauf", style="green")
    table.add_column("Netto", style="green")
    table.add_column("ROI", style="cyan")
    table.add_column("Chance", style="bold green")
    table.add_column("Puffer", style="yellow")
    table.add_column("Effizienz", style="cyan")
    table.add_column("Bild", style="cyan")
    table.add_column("Vision", style="white")
    table.add_column("Budget", style="yellow")
    table.add_column("Sold x", style="cyan")
    table.add_column("Sold Median", style="cyan")
    table.add_column("Quelle", style="white")
    table.add_column("Daten", style="white")
    table.add_column("Aktion", style="bold yellow")
    table.add_column("Link", style="blue")
    table.add_column("Empfehlung", style="bold")
    table.add_column("Risiko", style="yellow")

    for deal in deals:
        table.add_row(
            deal.product.name,
            f"{deal.offer_price:.2f} €",
            f"{(deal.max_buy_price if deal.max_buy_price is not None else deal.offer_price):.2f} €",
            f"{(deal.target_sell_price or deal.resale_price):.2f} €",
            f"{(deal.net_profit if deal.net_profit is not None else deal.profit):.2f} €",
            f"{(deal.roi_percent if deal.roi_percent is not None else 0):.1f}%",
            f"{(deal.opportunity_score if deal.opportunity_score is not None else 0):.1f}",
            f"{(deal.buy_price_gap if deal.buy_price_gap is not None else 0):.2f} €",
            f"{(deal.capital_efficiency if deal.capital_efficiency is not None else 0):.3f}",
            _format_optional_score(round(deal.image_score, 1) if deal.image_score is not None else None),
            deal.vision_source,
            str(deal.budget_priority) if deal.budget_priority is not None else "-",
            str(deal.sold_count),
            f"{(deal.sold_price_median if deal.sold_price_median is not None else 0):.2f} €",
            deal.sold_source_summary or "-",
            deal.price_data_quality,
            deal.buy_decision,
            f"[link={deal.offer_url}]Angebot[/link]",
            deal.recommendation,
            deal.risk or "-"
        )
    console.print(table)
