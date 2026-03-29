import json

import pytest

from config.manager import ConfigManager


def test_config_manager_loads_and_gets_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "search_interval_minutes": 10,
                "default_location": "Berlin",
                "notify_email": "test@example.com",
            }
        )
    )

    manager = ConfigManager(str(config_path))

    assert manager.get("default_location") == "Berlin"
    assert manager.get("missing", "fallback") == "fallback"


def test_config_manager_set_persists_to_file(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "search_interval_minutes": 5,
                "default_location": "Hamburg",
            }
        )
    )

    manager = ConfigManager(str(config_path))
    manager.set("notify_telegram", "123")

    saved = json.loads(config_path.read_text())
    assert saved["notify_telegram"] == "123"


def test_config_manager_raises_for_missing_file(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        ConfigManager(str(missing))


def test_config_manager_raises_for_invalid_config(tmp_path):
    missing_key_path = tmp_path / "missing_key.json"
    missing_key_path.write_text(json.dumps({"search_interval_minutes": 10}))

    with pytest.raises(ValueError):
        ConfigManager(str(missing_key_path))

    invalid_interval_path = tmp_path / "invalid_interval.json"
    invalid_interval_path.write_text(
        json.dumps(
            {
                "search_interval_minutes": 0,
                "default_location": "Berlin",
            }
        )
    )

    with pytest.raises(ValueError):
        ConfigManager(str(invalid_interval_path))
