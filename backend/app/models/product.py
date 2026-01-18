import uuid
from datetime import datetime, timezone

from sqlmodel import Column, DateTime, Field

from .base import BaseModel


class ProductBase(BaseModel):
    name: str = Field(max_length=255)
    brand: str | None = Field(default=None, max_length=255)


class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
