import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
