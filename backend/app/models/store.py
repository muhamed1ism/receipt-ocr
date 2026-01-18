import uuid
from datetime import datetime, timezone

from sqlmodel import Column, DateTime, Field, Relationship

from .base import BaseModel
from .branch import Branch


class StoreBase(BaseModel):
    name: str = Field(max_length=100)
    jib: str | None = Field(default=None, max_length=50)
    pib: str | None = Field(default=None, max_length=50)


class Store(StoreBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    branch: Branch | None = Relationship(back_populates="store")
