# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, TEXT, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from .db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date = Column(String, index=True)
    amount = Column(Float)
    description = Column(String)
    category = Column(String, index=True)
    raw = Column(JSON, nullable=True)

class Advice(Base):
    __tablename__ = "advice"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    advice_blob = Column(JSON)
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Memory(Base):
    __tablename__ = "memory"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key = Column(String)
    value = Column(JSON)
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
