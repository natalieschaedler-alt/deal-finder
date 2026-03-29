import json
import os
from datetime import UTC, datetime
from typing import Dict, List

DEFAULT_ARCHIVE_PATH = "database/live_runs.jsonl"


def append_search_snapshot(
    product_name: str,
    offers: List[Dict],
    market_metrics: Dict,
    filepath: str = DEFAULT_ARCHIVE_PATH,
) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    row = {
        "timestamp": datetime.now(UTC).isoformat(),
        "product": product_name,
        "offers_count": len(offers),
        "offers": offers,
        "market_metrics": {
            "sold_prices_count": len(market_metrics.get("sold_prices", [])),
            "sold_history_count": len(market_metrics.get("sold_history", [])),
            "sold_by_condition": {
                cond: len(values) for cond, values in market_metrics.get("sold_by_condition", {}).items()
            },
        },
    }
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_snapshots(filepath: str = DEFAULT_ARCHIVE_PATH, limit: int = 200) -> List[Dict]:
    if not os.path.exists(filepath):
        return []

    rows: List[Dict] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if limit > 0:
        rows = rows[-limit:]
    return rows


def summarize_snapshots(rows: List[Dict]) -> Dict:
    if not rows:
        return {
            "runs": 0,
            "total_offers": 0,
            "avg_offers_per_run": 0.0,
            "avg_sold_history_per_run": 0.0,
            "demo_ratio": 0.0,
            "last_run": "",
            "platform_counts": {},
        }

    total_offers = 0
    total_sold_history = 0
    total_demo_offers = 0
    platform_counts: Dict[str, int] = {}
    last_run = ""

    for row in rows:
        offers = row.get("offers", []) or []
        total_offers += len(offers)
        total_sold_history += int(row.get("market_metrics", {}).get("sold_history_count", 0))

        timestamp = str(row.get("timestamp", ""))
        if timestamp:
            last_run = max(last_run, timestamp)

        for offer in offers:
            platform = str(offer.get("source_platform", "Unbekannt"))
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            if platform == "DemoFallback":
                total_demo_offers += 1

    demo_ratio = (total_demo_offers / total_offers * 100.0) if total_offers else 0.0

    return {
        "runs": len(rows),
        "total_offers": total_offers,
        "avg_offers_per_run": round(total_offers / len(rows), 2),
        "avg_sold_history_per_run": round(total_sold_history / len(rows), 2),
        "demo_ratio": round(demo_ratio, 1),
        "last_run": last_run,
        "platform_counts": platform_counts,
    }
