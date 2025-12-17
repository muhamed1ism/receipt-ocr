import uuid
from datetime import date, datetime, timezone

from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import SQLModel, Field

from app.models import ProfileBase


class ProfileCreate(ProfileBase):
    user_id: uuid.UUID


class ProfilePublic(ProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID


class ProfilesPublic(SQLModel):
    data: list[ProfilePublic]
    count: int


class ProfileUpdate(SQLModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone_number: PhoneNumber | None = Field(default=None)
    date_of_birth: date | None = Field(default=None)
    country: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    currency_preference: str | None = Field(default=None)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
