import uuid
from datetime import date, datetime, timezone

from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Field, Relationship, SQLModel

from app.enums import CurrencyEnum

from .user import User


class ProfileBase(SQLModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone_number: PhoneNumber | None = Field(default=None)
    date_of_birth: date | None = Field(default=None)
    country: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    currency_preference: CurrencyEnum = Field(default=CurrencyEnum.BAM)


class Profile(ProfileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: User | None = Relationship(back_populates="profile")
