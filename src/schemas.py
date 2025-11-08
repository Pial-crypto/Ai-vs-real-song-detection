from pydantic import BaseModel, EmailStr
from typing import List
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class PredictionCreate(BaseModel):
    chunkWisePrediction: List        # no type inside
    modelWiseMajorityPrediction: dict
    fileName: str
    finalPrediction: dict
    user_id: int


class DashBoardCreate(BaseModel):
    createdAt: str
    chunkMajorityPrediction: str
    modelWiseMajorityPrediction: str
    user_id: int
    