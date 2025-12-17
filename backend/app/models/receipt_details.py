import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class ReceiptDetailsBase(SQLModel):
    ibfm: str | None = Field(default=None, max_length=50)
    bf: int | None = Field(default=None)
    ibk: int | None = Field(default=None)
    digital_signature: str | None = Field(default=None, max_length=255)


class ReceiptDetails(ReceiptDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    receipt_id: uuid.UUID = Field(
        foreign_key="receipt.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
