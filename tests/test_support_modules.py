from logic.demand import estimate_demand
from logic.risk import estimate_risk
from scheduler.auto_search import AutoSearchScheduler
from utils.notify import send_email, send_telegram


def test_estimate_demand_for_iphone_and_default():
    assert estimate_demand("iPhone 13") == 1.3
    assert estimate_demand("Nintendo Switch") == 1.0


def test_estimate_risk_collects_expected_flags():
    low_risk = estimate_risk(
        {"location": "Berlin", "seller_rating": 5, "is_fake": False}
    )
    assert low_risk == {}

    high_risk = estimate_risk(
        {"location": "Unknown", "seller_rating": 1, "is_fake": True}
    )
    assert high_risk["Unbekannter Standort"] == 1
    assert high_risk["Schlechte Verkäuferbewertung"] == 2
    assert high_risk["Fake-Angebot"] == 2


def test_notify_functions_print_output(capsys):
    send_email("Neue Deals", "Es gibt 2 neue Deals", "a@example.com")
    send_telegram("Es gibt 2 neue Deals", "123")

    output = capsys.readouterr().out
    assert "[E-Mail] Neue Deals an a@example.com: Es gibt 2 neue Deals" in output
    assert "[Telegram] an 123: Es gibt 2 neue Deals" in output


def test_scheduler_start_is_idempotent(monkeypatch):
    calls = {"search": 0, "starts": 0}

    class FakeThread:
        def __init__(self, target, daemon=False):
            self.target = target
            self.daemon = daemon
            self._alive = False

        def start(self):
            calls["starts"] += 1
            self._alive = True

        def is_alive(self):
            return self._alive

        def join(self, timeout=None):
            self._alive = False

    monkeypatch.setattr("scheduler.auto_search.Thread", FakeThread)

    scheduler = AutoSearchScheduler(1, lambda: calls.__setitem__("search", calls["search"] + 1))
    scheduler.start()
    scheduler.start()

    assert calls["starts"] == 1


def test_scheduler_run_executes_once_and_stop_joins(monkeypatch):
    calls = {"search": 0, "wait_timeout": None, "joined": False}

    class OneShotEvent:
        def __init__(self):
            self.stop = False

        def is_set(self):
            return self.stop

        def wait(self, timeout):
            calls["wait_timeout"] = timeout
            self.stop = True

        def set(self):
            self.stop = True

    class DummyThread:
        def __init__(self):
            self.alive = True

        def is_alive(self):
            return self.alive

        def join(self, timeout=None):
            calls["joined"] = True
            self.alive = False

    scheduler = AutoSearchScheduler(2, lambda: calls.__setitem__("search", calls["search"] + 1))
    scheduler._stop_event = OneShotEvent()
    scheduler.run()

    assert calls["search"] == 1
    assert calls["wait_timeout"] == 120

    scheduler._thread = DummyThread()
    scheduler.stop()
    assert calls["joined"]
