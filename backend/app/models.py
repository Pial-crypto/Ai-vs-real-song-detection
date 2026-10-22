"""SQLAlchemy ORM models."""

from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(32), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    predictions = relationship("PredictionHistory", back_populates="user", cascade="all, delete-orphan")
    dashboards = relationship("DashBoard", back_populates="user", cascade="all, delete-orphan")


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=True)
    chunk_wise_prediction = Column(JSON, nullable=True)
    model_wise_majority_prediction = Column(JSON, nullable=True)
    final_prediction = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions")
    dashboard = relationship("DashBoard", back_populates="prediction", uselist=False, cascade="all, delete-orphan")


class DashBoard(Base):
    __tablename__ = "dashboard"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(String(64), nullable=True)
    chunk_majority_prediction = Column(String(64), nullable=True)
    model_wise_majority_prediction = Column(String(64), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("prediction_history.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="dashboards")
    prediction = relationship("PredictionHistory", back_populates="dashboard")
