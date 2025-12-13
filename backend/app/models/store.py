import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class StoreBase(SQLModel):
    name: str = Field(max_length=100)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    jib: str | None = Field(default=None, max_length=50)
    pib: str | None = Field(default=None, max_length=50)


class Store(StoreBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StoreCreate(StoreBase):
    pass


class StorePublic(StoreBase):
    id: uuid.UUID


class StoresPublic(SQLModel):
    data: list[StorePublic]
    count: int


class StoreUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    jib: str | None = Field(default=None, max_length=50)
    pib: str | None = Field(default=None, max_length=50)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
