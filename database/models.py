from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://username:password@localhost:5432/db-name"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(engine)

class Chat(Base):
    __tablename__ = 'user_requests'
    chat_id = Column(Integer, primary_key=True)
    requests = Column(Integer, default=5)
