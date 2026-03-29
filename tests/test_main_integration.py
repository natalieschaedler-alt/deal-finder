import main as app_main
from database.models import Product


def make_product() -> Product:
    return Product(
        name="iPhone 13",
        category="Smartphone",
        condition="sehr gut",
        accessories=["Ladekabel", "OVP"],
        min_price=300,
        max_price=450,
        min_profit=50,
        min_resale_price=620,
    )


def test_main_flow_notifies_when_deal_found(monkeypatch):
    events = {
        "shown": None,
        "exported": None,
        "budget_exported": None,
        "emails": [],
        "telegrams": [],
    }

    class DummyConfigManager:
        def get(self, key, default=None):
            values = {
                "search_interval_minutes": 10,
                "default_location": "Berlin",
                "notify_email": "mail@example.com",
                "notify_telegram": "123",
                "min_opportunity_score": 0,
            }
            return values.get(key, default)

    class DummyProductManager:
        def __init__(self):
            self.products = [make_product()]

    class DummySearchManager:
        def search_all(self, product):
            return []

    class FakeScheduler:
        last_instance = None

        def __init__(self, interval_minutes, search_func):
            self.interval_minutes = interval_minutes
            self.search_func = search_func
            self.started = False
            self.stopped = False
            FakeScheduler.last_instance = self

        def start(self):
            self.started = True
            self.search_func()

        def stop(self):
            self.stopped = True

    def fake_show_deals(deals):
        events["shown"] = deals

    def fake_export_deals_csv(deals):
        events["exported"] = deals

    def fake_export_budget_plan_csv(deals):
        events["budget_exported"] = deals

    def fake_filter_deals(deals, min_profit=0, location=None):
        return deals

    def fake_sort_deals(deals, by="profit", reverse=True):
        return deals

    def fake_send_email(subject, message, to):
        events["emails"].append((subject, message, to))

    def fake_send_telegram(message, chat_id):
        events["telegrams"].append((message, chat_id))

    def fake_estimate_demand(_product_name):
        return 1.2

    def fake_estimate_risk(_offer):
        return {}

    def fake_advanced_evaluate_deal(
        product,
        offer_price,
        resale_price,
        condition,
        accessories,
        location,
        demand,
        risk_factors,
    ):
        return {
            "score": 9,
            "reasons": ["ok"],
            "profit": resale_price - offer_price,
            "recommendation": "Deal",
        }

    monkeypatch.setattr("config.manager.ConfigManager", DummyConfigManager)
    monkeypatch.setattr("database.manager.ProductManager", DummyProductManager)
    monkeypatch.setattr("search.manager.SearchManager", DummySearchManager)
    monkeypatch.setattr("dashboard.display.show_deals", fake_show_deals)
    monkeypatch.setattr("dashboard.export.export_deals_csv", fake_export_deals_csv)
    monkeypatch.setattr("dashboard.export.export_budget_plan_csv", fake_export_budget_plan_csv)
    monkeypatch.setattr("dashboard.filters.filter_deals", fake_filter_deals)
    monkeypatch.setattr("dashboard.filters.sort_deals", fake_sort_deals)
    monkeypatch.setattr("utils.notify.send_email", fake_send_email)
    monkeypatch.setattr("utils.notify.send_telegram", fake_send_telegram)
    monkeypatch.setattr("logic.demand.estimate_demand", fake_estimate_demand)
    monkeypatch.setattr("logic.risk.estimate_risk", fake_estimate_risk)
    monkeypatch.setattr(
        "logic.advanced_evaluate.advanced_evaluate_deal",
        fake_advanced_evaluate_deal,
    )
    monkeypatch.setattr("scheduler.auto_search.AutoSearchScheduler", FakeScheduler)
    monkeypatch.setattr("builtins.input", lambda _msg: "")

    app_main.main()

    assert FakeScheduler.last_instance is not None
    assert FakeScheduler.last_instance.started
    assert FakeScheduler.last_instance.stopped
    assert events["shown"] is not None
    assert len(events["shown"]) == 1
    assert events["exported"] is not None
    assert len(events["exported"]) == 1
    assert events["budget_exported"] is not None
    assert len(events["budget_exported"]) == 1
    assert len(events["emails"]) == 1
    assert len(events["telegrams"]) == 1


def test_main_flow_skips_notifications_when_no_deal(monkeypatch):
    events = {
        "shown": None,
        "exported": None,
        "budget_exported": None,
        "emails": [],
        "telegrams": [],
    }

    class DummyConfigManager:
        def get(self, key, default=None):
            values = {
                "search_interval_minutes": 10,
                "default_location": "Berlin",
                "notify_email": "mail@example.com",
                "notify_telegram": "123",
            }
            return values.get(key, default)

    class DummyProductManager:
        def __init__(self):
            self.products = [make_product()]

    class DummySearchManager:
        def search_all(self, product):
            return []

    class FakeScheduler:
        last_instance = None

        def __init__(self, interval_minutes, search_func):
            self.interval_minutes = interval_minutes
            self.search_func = search_func
            self.started = False
            self.stopped = False
            FakeScheduler.last_instance = self

        def start(self):
            self.started = True
            self.search_func()

        def stop(self):
            self.stopped = True

    def fake_show_deals(deals):
        events["shown"] = deals

    def fake_export_deals_csv(deals):
        events["exported"] = deals

    def fake_export_budget_plan_csv(deals):
        events["budget_exported"] = deals

    def fake_filter_deals(deals, min_profit=0, location=None):
        return deals

    def fake_sort_deals(deals, by="profit", reverse=True):
        return deals

    def fake_send_email(subject, message, to):
        events["emails"].append((subject, message, to))

    def fake_send_telegram(message, chat_id):
        events["telegrams"].append((message, chat_id))

    def fake_estimate_demand(_product_name):
        return 1.2

    def fake_estimate_risk(_offer):
        return {}

    def fake_advanced_evaluate_deal(
        product,
        offer_price,
        resale_price,
        condition,
        accessories,
        location,
        demand,
        risk_factors,
    ):
        return {
            "score": 3,
            "reasons": ["kein deal"],
            "profit": resale_price - offer_price,
            "recommendation": "Kein Deal",
        }

    monkeypatch.setattr("config.manager.ConfigManager", DummyConfigManager)
    monkeypatch.setattr("database.manager.ProductManager", DummyProductManager)
    monkeypatch.setattr("search.manager.SearchManager", DummySearchManager)
    monkeypatch.setattr("dashboard.display.show_deals", fake_show_deals)
    monkeypatch.setattr("dashboard.export.export_deals_csv", fake_export_deals_csv)
    monkeypatch.setattr("dashboard.export.export_budget_plan_csv", fake_export_budget_plan_csv)
    monkeypatch.setattr("dashboard.filters.filter_deals", fake_filter_deals)
    monkeypatch.setattr("dashboard.filters.sort_deals", fake_sort_deals)
    monkeypatch.setattr("utils.notify.send_email", fake_send_email)
    monkeypatch.setattr("utils.notify.send_telegram", fake_send_telegram)
    monkeypatch.setattr("logic.demand.estimate_demand", fake_estimate_demand)
    monkeypatch.setattr("logic.risk.estimate_risk", fake_estimate_risk)
    monkeypatch.setattr(
        "logic.advanced_evaluate.advanced_evaluate_deal",
        fake_advanced_evaluate_deal,
    )
    monkeypatch.setattr("scheduler.auto_search.AutoSearchScheduler", FakeScheduler)
    monkeypatch.setattr("builtins.input", lambda _msg: "")

    app_main.main()

    assert FakeScheduler.last_instance is not None
    assert FakeScheduler.last_instance.started
    assert FakeScheduler.last_instance.stopped
    assert events["shown"] is not None
    assert len(events["shown"]) == 1
    assert events["shown"][0].buy_decision != "KAUFEN"
    assert events["exported"] is not None
    assert len(events["exported"]) == 1
    assert events["budget_exported"] == []
    assert len(events["emails"]) == 0
    assert len(events["telegrams"]) == 0
