from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from database.models import Chat
from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB-USER')}:{os.getenv('DB-PASSWORD')}@{os.getenv('DB-HOST')}:{os.getenv('DB-PORT')}/{os.getenv('DB-NAME')}"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def new_user(chat_id, username):
    """Добавление нового пользователя и проверка записи в БД."""
    session = Session()

    chat = session.query(Chat).filter_by(chat_id=chat_id).first()
    if not chat:
        # Если записи нет, добавляем ее
        new_chat = Chat(chat_id=chat_id, username=username)
        session.add(new_chat)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении записи в базу: {e}")

    session.close()

def charge_request(chat_id):
    """Списание одного запроса у пользователя."""
    session = Session()
    chat = session.query(Chat).filter_by(chat_id=chat_id).first()

    if chat.requests == 0:
        return False
    
    chat.requests -= 1
    session.commit()
    session.close()

    return True

def add_requests(chat_id, num):
    """Добавление заданного количества запросов пользователю."""
    session = Session()
    chat = session.query(Chat).filter_by(chat_id=chat_id).first()
    chat.requests += num
    session.commit()
    session.close()


def get_requests(chat_id):
    """Получение текущего количества запросов у пользователя."""
    session = Session()
    chat = session.query(Chat).filter_by(chat_id=chat_id).first()
    num = chat.requests
    session.close()

    return num
