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
    created_at: datetime

    model_config = {"from_attributes": True}
