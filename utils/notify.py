# utils/notify.py

def send_email(subject: str, message: str, to: str):
    # TODO: Implementiere echten E-Mail-Versand
    print(f"[E-Mail] {subject} an {to}: {message}")

def send_telegram(message: str, chat_id: str):
    # TODO: Implementiere echten Telegram-Versand
    print(f"[Telegram] an {chat_id}: {message}")
