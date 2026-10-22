"""Pydantic schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

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


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    action: str
    resource: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None


class NotificationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=1024)
    level: str = "info"


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    level: str
    read: bool
    created_at: Optional[datetime] = None


class FeatureFlagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    enabled: bool
    description: Optional[str] = None
    rollout_percent: int


class FeatureFlagUpdate(BaseModel):
    enabled: Optional[bool] = None
    description: Optional[str] = None
    rollout_percent: Optional[int] = Field(default=None, ge=0, le=100)


class ModelMetadataOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    accuracy: Optional[str] = None
    path: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


class BatchJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    total_files: int
    processed_files: int
    results: Optional[Any] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class UserProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    bio: Optional[str] = None
    updated_at: Optional[datetime] = None


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    bio: Optional[str] = None


class ExportJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    format: str
    status: str
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
