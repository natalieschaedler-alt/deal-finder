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
