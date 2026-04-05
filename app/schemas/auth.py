from pydantic import BaseModel, EmailStr

from app.models.user import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.viewer


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    status: str = "success"
    access_token: str
    token_type: str = "bearer"
    message: str = "Login successful"
