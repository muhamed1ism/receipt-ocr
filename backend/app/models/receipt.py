import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlmodel import Column, DateTime, Field, Relationship

from app.enums import CurrencyEnum

from .base import BaseModel

if TYPE_CHECKING:
    from .branch import Branch
    from .receipt_details import ReceiptDetails
    from .receipt_item import ReceiptItem
    from .user import User


class ReceiptBase(BaseModel):
    date_time: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
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
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    branch: Mapped["Branch"] = Relationship(
        back_populates="receipt",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    details: Mapped["ReceiptDetails"] = Relationship(
        back_populates="receipt",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    items: Mapped[list["ReceiptItem"]] = Relationship(
        back_populates="receipt",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    user: Mapped["User"] = Relationship(
        back_populates="receipt",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
