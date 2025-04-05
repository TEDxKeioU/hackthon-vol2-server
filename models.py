from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from settings import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class TodoModel(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_digest = Column(String, nullable=False)


class Prompt_history(Base):
    __tablename__ = 'prompt_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    r_recipe_name = Column(String, nullable=False)