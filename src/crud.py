from sqlalchemy.orm import Session
import models,utils
from schemas import PredictionCreate

def get_user(db: Session, email: str,password:str): return db.query(models.User).filter(models.User.email == email and models.User.password==password).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_data: dict):
    print("User data received for creation:", user_data)
    if get_user_by_email(db,user_data["email"]):
        raise ValueError("Email already registered")
    hashed_pw = utils.hash_password(user_data["password"])
    db_user = models.User(
        username=user_data["username"],
        email=user_data["email"],
        password=hashed_pw,
        id= user_data.get("id")
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_prediction_history(db: Session, prediction_data: PredictionCreate):
    db_prediction = models.PredictionHistory(
        chunkWisePrediction=prediction_data.chunkWisePrediction,
        modelWiseMajorityPrediction=prediction_data.modelWiseMajorityPrediction,
        finalPrediction=prediction_data.finalPrediction,
        user_id=prediction_data.user_id
        ,fileName=prediction_data.fileName
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_prediction_history_by_user(db: Session, user_id: int):
    return db.query(models.PredictionHistory).filter(models.PredictionHistory.user_id == user_id).all()

def delete_prediction_by_id(db: Session, prediction_id: int):
    prediction = db.query(models.PredictionHistory).filter(models.PredictionHistory.id == prediction_id).first()
    if prediction:
        db.delete(prediction)
        db.commit()

def add_dashboard(db: Session, prediction_id: int, dashboard_data):
    db_dashboard = models.DashBoard(
        id=prediction_id,
        createdAt=dashboard_data.createdAt,
        chunkMajorityPrediction=dashboard_data.chunkMajorityPrediction,
        modelWiseMajorityPrediction=dashboard_data.modelWiseMajorityPrediction,
        user_id=dashboard_data.user_id
    )
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard

def get_dashboards(db: Session):
    return db.query(models.DashBoard).all()

def get_all_users(db: Session):
    return db.query(models.User).all()
