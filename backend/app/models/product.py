import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    name: str = Field(max_length=255)
    brand: str | None = Field(default=None, max_length=255)


class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
