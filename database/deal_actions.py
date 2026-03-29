import json
import os
from datetime import UTC, datetime
from typing import Dict, List


DEFAULT_ACTIONS_PATH = "database/deal_actions.json"


def load_deal_actions(filepath: str = DEFAULT_ACTIONS_PATH) -> List[Dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as file:
        return json.load(file)


def save_deal_action(deal_id: str, product_name: str, action: str, note: str = "", filepath: str = DEFAULT_ACTIONS_PATH) -> Dict:
    actions = load_deal_actions(filepath)
    entry = {
        "deal_id": deal_id,
        "product_name": product_name,
        "action": action,
        "note": note,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    actions.append(entry)
    with open(filepath, "w") as file:
        json.dump(actions, file, indent=2, ensure_ascii=False)
    return entry