import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

from app.enums import CurrencyEnum

if TYPE_CHECKING:
    from .receipt_item import ReceiptItem


class ReceiptBase(SQLModel):
    date_time: datetime | None = Field(default=None)
    tax_amount: float | None = Field(default=None)
    total_amount: float | None = Field(default=None)
    payment_method: str | None = Field(default=None, max_length=50)
    currency: CurrencyEnum = Field(default=CurrencyEnum.BAM)


class Receipt(ReceiptBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    branch_id: uuid.UUID = Field(
        foreign_key="branch.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    items: Mapped[list["ReceiptItem"]] = Relationship(
        back_populates="receipt",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
