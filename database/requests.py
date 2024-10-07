from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database.models import Chat

DATABASE_URL = "postgresql://user:password@localhost:5432/db-name"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def new_user(chat_id):

    session = Session()

    chat = session.query(Chat).filter_by(chat_id=chat_id).first()
    if not chat:
        # Если записи нет, добавляем ее
        new_chat = Chat(chat_id=chat_id)
        session.add(new_chat)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении записи в базу: {e}")

    session.close()
