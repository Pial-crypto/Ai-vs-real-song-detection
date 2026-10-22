"""Pydantic schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def _password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain an uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("password must contain a lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain a digit")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PredictionCreate(BaseModel):
    chunkWisePrediction: list[Any] = Field(default_factory=list)
    modelWiseMajorityPrediction: dict[str, Any] = Field(default_factory=dict)
    fileName: str = Field(min_length=1, max_length=255)
    finalPrediction: dict[str, Any] = Field(default_factory=dict)
    user_id: int


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str | None = None
    chunk_wise_prediction: list[Any] | None = None
    model_wise_majority_prediction: dict[str, Any] | None = None
    final_prediction: dict[str, Any] | None = None
    user_id: int
    created_at: datetime | None = None


class DashBoardCreate(BaseModel):
    createdAt: str
    chunkMajorityPrediction: str
    modelWiseMajorityPrediction: str
    user_id: int


class DashBoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: str | None = None
    chunk_majority_prediction: str | None = None
    model_wise_majority_prediction: str | None = None
    user_id: int
    prediction_id: int


class HealthResponse(BaseModel):
    status: str
    version: str
    database: bool
    environment: str


class ErrorResponse(BaseModel):
    error: dict[str, Any]
