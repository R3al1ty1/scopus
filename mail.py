import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from database.models import Chat
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB-USER')}:{os.getenv('DB-PASSWORD')}@{os.getenv('DB-HOST')}:{os.getenv('DB-PORT')}/{os.getenv('DB-NAME')}"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Ваш токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Сообщение, которое нужно отправить
MESSAGE = """🎉 Поздравляем всех с наступившим 2025 годом! 

⚙️ Важная информация: Scopus изменил порядок авторизации, из-за чего бот может выдавать неверные результаты. В связи с этим мы полностью переписываем техническую логику бота.

⏳ Работа бота будет приостановлена на 2-3 дня.

💬 Приносим извинения за неудобства! Если у вас возникли ошибки в запросах, пожалуйста, напишите в поддержку — мы компенсируем любые потери, чтобы вы могли использовать обновленного бота в будущем!

🙏 Спасибо за ваше понимание!"""

# URL для отправки сообщений через Telegram API
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        if response.status_code == 200:
            print(f"Сообщение отправлено пользователю {chat_id}")
        else:
            print(f"Ошибка при отправке пользователю {chat_id}: {response.json()}")
    except Exception as e:
        print(f"Ошибка при отправке пользователю {chat_id}: {e}")

def main():
    session = Session()
    chat_ids = session.query(Chat.chat_id).all()
    session.close()
    print(chat_ids)

    for user_id in chat_ids:
        user_id = user_id[0]
        send_message(chat_id=user_id, text=MESSAGE)

if __name__ == "__main__":
    main()
