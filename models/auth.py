
from pydantic import BaseModel, EmailStr
from typing import Optional


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
    last_sign_in: Optional[str] = None


class AuthResponse(BaseModel):
    user: User
    access_token: str
    refresh_token: str
