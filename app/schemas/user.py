from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import Role


class UserRead(BaseModel):
    id: str
    email: EmailStr
    role: Role
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRoleUpdate(BaseModel):
    role: Role
