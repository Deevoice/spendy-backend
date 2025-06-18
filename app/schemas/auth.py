from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    # avatar: str | None = None  # если base64, но мы будем файл

    class Config:
        from_attributes = True


class SessionInfo(BaseModel):
    id: int
    ip: str | None = None
    user_agent: str | None = None
    created_at: str
    last_used_at: str
    is_active: bool

    class Config:
        orm_mode = True
