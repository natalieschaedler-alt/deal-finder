# main.py


def main():
    from config.manager import ConfigManager
    from logic.workflow import run_search_workflow

    config = ConfigManager()

    def run_full_search():
        run_search_workflow(
            config=config,
            show_console=True,
            enable_notifications=True,
            export_files=True,
        )

    from scheduler.auto_search import AutoSearchScheduler

    scheduler = AutoSearchScheduler(config.get("search_interval_minutes", 10), run_full_search)
    scheduler.start()
    try:
        input("Automatische Suche läuft. Drücke Enter zum Beenden...\n")
    finally:
        scheduler.stop()


if __name__ == "__main__":
    main()
