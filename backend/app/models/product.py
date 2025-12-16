import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    name: str = Field(max_length=255)
    brand: str | None = Field(max_length=255)


class Product(ProductBase, table=True):
    id: uuid.UUID = Field(primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductCreate(ProductBase):
    pass


class ProductReceiptItemIn(ProductBase):
    pass


class ProductPublic(ProductBase):
    id: uuid.UUID


class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int


class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
