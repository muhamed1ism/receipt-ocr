import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.models import StoreBase


class StoreCreate(StoreBase):
    pass


class StoreReceiptIn(StoreBase):
    pass


class StorePublic(StoreBase):
    id: uuid.UUID


class StoresPublic(SQLModel):
    data: list[StorePublic]
    count: int


class StoreUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    jib: str | None = Field(default=None, max_length=50)
    pib: str | None = Field(default=None, max_length=50)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
