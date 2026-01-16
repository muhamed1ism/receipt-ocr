import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

from .receipt import Receipt


class ReceiptDetailsBase(SQLModel):
    ibfm: str | None = Field(default=None, max_length=50)
    bf: int | None = Field(default=None)


class ReceiptDetails(ReceiptDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    receipt_id: uuid.UUID = Field(
        foreign_key="receipt.id", nullable=False, ondelete="CASCADE"
    )
    receipt: Receipt | None = Relationship(back_populates="details")
