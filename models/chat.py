from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Message(BaseModel):
    id: UUID
    chat_session_id: UUID
    role: str
    content: str
    timestamp: datetime


class ChatSession(BaseModel):
    id: UUID
    user_id: UUID
    client_parameters_id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str


class ClientParameters(BaseModel):
    id: UUID
    user_id: UUID
    client_name: str
    client_type: str
    budget_min: int
    budget_max: int
    urgency_level: int
    personality_traits: str
    property_preferences: Optional[str] = None
    special_requirements: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    chat_session_id: UUID
    role: str
    content: str


class ChatSessionCreate(BaseModel):
    user_id: UUID
    client_parameters_id: UUID
    status: str = "active"  # Default status when creating a session


class ClientParametersCreate(BaseModel):
    user_id: UUID
    client_name: str
    client_type: str
    budget_min: int
    budget_max: int
    urgency_level: int
    personality_traits: str
    property_preferences: Optional[str] = None
    special_requirements: Optional[str] = None
