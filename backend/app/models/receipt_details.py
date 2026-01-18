import uuid
from datetime import datetime, timezone

from sqlmodel import Column, DateTime, Field, Relationship

from .base import BaseModel
from .receipt import Receipt


class ReceiptDetailsBase(BaseModel):
    ibfm: str | None = Field(default=None, max_length=50)
    bf: int | None = Field(default=None)
    digital_signature: str | None = Field(default=None, max_length=255)


class ReceiptDetails(ReceiptDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    receipt_id: uuid.UUID = Field(
        foreign_key="receipt.id", nullable=False, ondelete="CASCADE"
    )
    receipt: Receipt | None = Relationship(back_populates="details")
