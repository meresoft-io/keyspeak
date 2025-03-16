from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str
    email: EmailStr
    email_confirmed: bool = False
    last_sign_in: Optional[datetime] = None
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class AuthResponse(BaseModel):
    user: User
    access_token: str
    refresh_token: str


class JWTStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
