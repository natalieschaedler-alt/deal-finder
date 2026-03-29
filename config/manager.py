# config/manager.py
import json
import os

# Keys that can be overridden via Streamlit Cloud secrets
_SECRETS_KEYS = {
    "ebay_app_id", "vision_api_key", "notify_telegram", "notify_email",
    "max_purchase_budget", "max_budget_items",
}


def _load_streamlit_secrets() -> dict:
    """Load secrets from Streamlit Cloud if available, silently ignore otherwise."""
    try:
        import streamlit as st
        overrides = {}
        for key in _SECRETS_KEYS:
            try:
                val = st.secrets[key]
                if val not in (None, ""):
                    overrides[key] = val
            except KeyError:
                pass
        return overrides
    except Exception:
        return {}


class ConfigManager:
    def __init__(self, filepath: str = "config.json"):
        self.filepath = filepath
        self.config = self.load_config()

    def load_config(self) -> dict:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Konfigurationsdatei '{self.filepath}' nicht gefunden.")
        with open(self.filepath, "r") as f:
            config = json.load(f)
        self.validate_config(config)
        # Streamlit Cloud secrets override local config (never stored in Git)
        config.update(_load_streamlit_secrets())
        return config

    def validate_config(self, config: dict):
        required = ["search_interval_minutes", "default_location"]
        for key in required:
            if key not in config:
                raise ValueError(f"Pflichtfeld '{key}' fehlt in der Konfiguration.")
        if not isinstance(config["search_interval_minutes"], int) or config["search_interval_minutes"] <= 0:
            raise ValueError("'search_interval_minutes' muss eine positive Ganzzahl sein.")

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value
        self.save_config()

    def save_config(self):
        with open(self.filepath, "w") as f:
            json.dump(self.config, f, indent=2)
