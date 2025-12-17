import uuid

from sqlmodel import SQLModel, Field

from app.models import ProductBase


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
