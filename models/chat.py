from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID
from pydantic import BaseModel
from enum import Enum
from models.auth import User


class ChatSessionStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
    paused = "paused"


class Gender(str, Enum):
    male = "male"
    female = "female"


class Message(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime


class ClientParameters(BaseModel):
    id: UUID
    user: User
    client_name: str
    client_type: str
    budget_min: int
    budget_max: int
    urgency_level: int
    personality_traits: str
    property_preferences: Optional[str]
    special_requirements: Optional[str]


class ClientProfile(BaseModel):
    id: UUID
    name: str
    gender: Gender
    age: int
    marital_status: str
    children: int
    pets: int
    education_level: str
    occupation: str


class ChatSession(BaseModel):
    id: UUID
    user_id: User
    client_parameters: ClientParameters
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    messages: List[Message]
    status: ChatSessionStatus
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    chat_session: ChatSession
    sender: Union[User, ClientProfile]
    content: str


class ChatSessionCreate(BaseModel):
    user: User
    client_parameters: ClientParameters
    status: ChatSessionStatus


class ClientParametersCreate(BaseModel):
    user: User
    client_name: str
    client_type: str
    budget_min: int
    budget_max: int
    urgency_level: int
    personality_traits: str
    property_preferences: Optional[str]
    special_requirements: Optional[str]
