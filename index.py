import json
import os
import requests
import hashlib
import hmac

# Загрузка файла с данными о вложениях
with open("attached_files.json", "r", encoding="utf-8") as f:
    ATTACHED_FILES = json.load(f)

API_BASE_URL = "https://api.pachca.com/api/shared/v1"
PACHKA_API_TOKEN = os.environ.get("PACHKA_API_TOKEN", "")
BOT_HEADERS = {
    "Authorization": f"Bearer {PACHKA_API_TOKEN}",
    "Content-Type": "application/json"
}

START_MESSAGE = ("Привет! Я **Bnovo-bot** — помогу найти нужную тебе информацию\n"
            "Просто пиши мне команды — и я с радостью помогу или подскажу к кому обратиться ✨\n\n"
            "/help — список всех доступных команд\n\n")

HELP_MESSAGE = ("/welcome — наша велком-презентация\n\n"
            "/services — сервисы для работы"
            "/documents — документы"
            "/office — информация об офисе"
            "/benefits — разные приятности и бонусы"
            "/contacts — к кому можешь обратиться")

MAIN_MENU_BUTTONS = [
    [   {"text": "Велком-презентация", "data": "/welcome"},
        {"text": "Сервисы для работы", "data": "/services"}],
    [   {"text": "Документы", "data": "/documents"},
        {"text": "Офис", "data": "/office"}],
    [   {"text": "Бенефиты", "data": "/benefits"},
        {"text": "К кому обратиться?", "data": "/contacts"}]
]

DOCUMENTS_BUTTONS = [
    [{"text": "Больничный", "data": "doc_sick"}],
    [{"text": "Отпуск", "data": "doc_vacation"}],
    [{"text": "Командировка", "data": "doc_trip"}],
]

LEGAL_ENTITY_BUTTONS = [
    [{"text": "Биново", "data": "binovo"}, {"text": "Отель продакт", "data": "otel_product"}]
]

OFFICE_BUTTONS = [
    [{"text": "Wi-Fi", "data": "/wifi"}],
    [{"text": "Бронирование переговорной", "data": "/meeting"}],
    [{"text": "Правила офиса", "data": "/rules"}],
]

BENEFITS_BUTTONS = [
    [{"text": "BestBenefits", "data": "benefit_bestbenefits"},
    {"text": "MyBook", "data": "benefit_mybook"}],
    [{"text": "ДМС Ренессанс", "data": "benefit_dms"},
    {"text": "Спортзал", "data": "benefit_gym"}],
    [{"text": "Парковка", "data": "benefit_parking"},
    {"text": "Что ещё есть?", "data": "benefit_other"}]
]

MAP_FLOOR_BUTTONS = [
    [{"text": "6 этаж", "data": "floor_6"}, {"text": "7 этаж", "data": "floor_7"}]
]


def send_message(chat_id, text, buttons=None):
    payload = {
        "message": {
            "entity_id": chat_id,
            "content": text
        }
    }
    if buttons:
        payload["message"]["buttons"] = buttons

    try:
        response = requests.post(f"{API_BASE_URL}/messages", headers=BOT_HEADERS, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Ошибка отправки сообщения:", e)
        print("Payload:", payload)


def send_file_attachment(chat_id, key, name, file_type, caption=None):
    payload = {
        "message": {
            "entity_id": chat_id,
            "content": caption or "",
            "files": [{
                "key": key,
                "name": name,
                "file_type": file_type
            }]
        }
    }

    try:
        response = requests.post(f"{API_BASE_URL}/messages", headers=BOT_HEADERS, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Ошибка отправки вложения:", e)
        print("Payload:", payload)


def process_payload(chat_id, payload_data):
    if payload_data in ATTACHED_FILES:
        file_info = ATTACHED_FILES[payload_data]
        send_file_attachment(chat_id, **file_info, caption="Карта этажа" if "floor" in payload_data else "Файл")
    elif payload_data == "/start":
        send_message(chat_id, START_MESSAGE, buttons=MAIN_MENU_BUTTONS)
    #elif payload_data == "/help":
    #    send_message(chat_id, HELP_MESSAGE, buttons=MAIN_MENU_BUTTONS)
    elif payload_data == "/welcome":
        file_info = ATTACHED_FILES.get("welcome")
        if file_info:
            send_file_attachment(chat_id, **file_info, caption="Отправляю файл с велком-презентацией, здесь ты найдешь всю информацию, которая может понадобиться тебе в первое время")
        else:
            send_message(chat_id, "Файл приветствия не найден.")
    elif payload_data == "/services":
        send_message(chat_id,
            "Отправляю тебе ссылку на базу знаний WIKI — [ссылка](https://wiki.yandex.ru/servises/).\n"
            "Здесь ты найдешь информацию о базовых сервисах для работы, которые используют все сотрудники.\n\n"
            "Важно! В каждом отделе есть и другие сервисы для работы, подробнее о них расскажет твой наставник или руководитель."
        )
    elif payload_data == "/documents":
        send_message(chat_id, "Выбери нужный тебе раздел:", buttons=DOCUMENTS_BUTTONS)
    elif payload_data in ["doc_sick", "doc_vacation", "doc_trip"]:
        send_message(chat_id, "Выбери юридическое лицо, в которое ты трудоустроен(а):", buttons=LEGAL_ENTITY_BUTTONS)
    elif payload_data == "/office":
        send_message(chat_id, "Выбери пункт меню:", buttons=OFFICE_BUTTONS)
    elif payload_data == "/meeting":
        send_message(chat_id, "Бронирование переговорной: [ссылка](https://wiki.yandex.ru/meeting/)")
    elif payload_data == "/rules":
        send_message(chat_id, "Правила офиса: [ссылка](https://wiki.yandex.ru/offrules/)")
    elif payload_data == "/benefits":
        send_message(chat_id, "Выбери интересующий бенефит:", buttons=BENEFITS_BUTTONS)
    elif payload_data.startswith("benefit_"):
        benefit_info = {
            "benefit_bestbenefits": "BestBenefits — [ссылка](https://bestbenefits.example.com)",
            "benefit_mybook": "MyBook — бесплатный доступ к книгам: [ссылка](https://wiki.yandex.ru/mybook/)",
            "benefit_dms": "ДМС от Ренессанс: подробнее на [ссылка](https://wiki.yandex.ru/dms/)",
            "benefit_gym": "Абонемент в спортзал: [ссылка](https://wiki.yandex.ru/sport/)",
            "benefit_parking": "Как получить парковку: [ссылка](https://wiki.yandex.ru/parking/)",
            "benefit_other": "Дополнительно: [ссылка](https://wiki.yandex.ru/benef/)"
        }
        send_message(chat_id, benefit_info.get(payload_data, "Информация недоступна."))
    elif payload_data == "/contacts":
        send_message(chat_id, "По всем вопросам можешь обратиться к своему наставнику или HR-менеджеру")
    elif payload_data == "/wifi":
        send_message(chat_id, "Wi-Fi: BnovoNet | Пароль: bnovo_senator_17")
    else:
        send_message(chat_id, "Неизвестная кнопка. Пожалуйста, попробуй ещё раз.")


def handler(event, context):
    print("Headers:", event.get("headers"))
    print("Body:", event.get("body"))

    headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
    signature = headers.get("pachca-signature")
    secret = os.environ.get("WEBHOOK_SECRET", "")
    if not signature or not secret:
        print("Подпись или секрет отсутствуют — отклоняем.")
        return {"statusCode": 403, "body": "Forbidden"}

    body = event["body"]
    computed_sig = hmac.new(secret.encode(), msg=body.encode(), digestmod=hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_sig, signature):
        print("Подпись не совпадает — отклоняем.")
        return {"statusCode": 403, "body": "Forbidden"}

    request = json.loads(body)
    chat_id = request.get("chat_id")
    sender_id = request.get("user_id")
    BOT_USER_ID = int(os.environ.get("BOT_USER_ID", "0"))
    if sender_id == BOT_USER_ID:
        return {"statusCode": 200, "body": "ok"}

    text = request.get("content", "").lower()
    payload_data = request.get("data", "")

    if payload_data:
        process_payload(chat_id, payload_data)
        return {"statusCode": 200, "body": "ok"}

    if text == "/start":
        send_message(chat_id, START_MESSAGE, buttons=MAIN_MENU_BUTTONS)
    elif text == "/help":
        send_message(chat_id, "Выбери команду:", buttons=MAIN_MENU_BUTTONS)
    elif text == "/wifi":
        send_message(chat_id, "Wi-Fi: BnovoNet | Пароль: bnovo_senator_17")
    elif text == "/itsupport":
        send_message(chat_id, "Заявка в IT-поддержку: [ссылка](https://wiki.yandex.ru/sozdanie-obrashhenija/)")
    elif text == "/pcsetup":
        send_message(chat_id, "Гайд по настройке ПК: [ссылка](https://wiki.yandex.ru/pc-setup-guide/)")
    elif text == "/kitchen":
        send_message(chat_id, "Кухня на 7 этаже — печеньки и чай ждут!")
    elif text == "/map":
        send_message(chat_id, "Выбери этаж:", buttons=MAP_FLOOR_BUTTONS)
    elif text == "/welcome":
        file_info = ATTACHED_FILES.get("welcome")
        if file_info:
            send_file_attachment(chat_id, **file_info, caption="Отправляю файл с велком-презентацией, здесь ты найдешь всю информацию, которая может понадобиться тебе в первое время")
        else:
            send_message(chat_id, "Файл приветствия не найден.")
    else:
        send_message(chat_id, "Для начала напиши /start", buttons=[
            [{"text": "/start", "data": "/start"}]
        ])

    return {"statusCode": 200, "body": "ok"}