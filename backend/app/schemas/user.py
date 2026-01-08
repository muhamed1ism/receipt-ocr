import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.models import UserBase
from app.schemas.profile import ProfilePublic


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserPublicWithProfile(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    profile: ProfilePublic | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UsersPublicWithProfile(SQLModel):
    data: list[UserPublicWithProfile]
    count: int


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
