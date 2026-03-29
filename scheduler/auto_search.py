# scheduler/auto_search.py
import time
from threading import Event, Thread

class AutoSearchScheduler:
    def __init__(self, interval_minutes: int, search_func):
        self.interval = interval_minutes * 60
        self.search_func = search_func
        self._stop_event = Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self.run, daemon=False)
        self._thread.start()

    def run(self):
        while not self._stop_event.is_set():
            print("[AutoSearch] Starte automatische Suche...")
            self.search_func()
            # Wait allows immediate shutdown instead of sleeping blindly.
            self._stop_event.wait(self.interval)

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
