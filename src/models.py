from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # relationships
    predictions = relationship("PredictionHistory", back_populates="user")
    dashboards = relationship("DashBoard", back_populates="user")  # lowercase 'dashboards'


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    fileName = Column(String, nullable=True)
    chunkWisePrediction = Column(JSON)
    modelWiseMajorityPrediction = Column(JSON)
    finalPrediction = Column(JSON)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="predictions")

    dashboard = relationship("DashBoard", back_populates="prediction")  # singular, lowercase


class DashBoard(Base):
    __tablename__ = "dashboard"
    
    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(String)
    chunkMajorityPrediction = Column(String)
    modelWiseMajorityPrediction = Column(String)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    prediction_id = Column(Integer, ForeignKey("prediction_history.id"))

    user = relationship("User", back_populates="dashboards")
    prediction = relationship("PredictionHistory", back_populates="dashboard")
