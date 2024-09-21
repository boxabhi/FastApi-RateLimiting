from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Interval
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)
    limit = Column(Integer, nullable=True)
    window_seconds = Column(Integer, nullable=True)
    


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    

    