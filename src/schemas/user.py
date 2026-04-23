import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    is_active: bool
    daily_new_limit: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    daily_new_limit: int
