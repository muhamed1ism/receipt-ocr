import uuid
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field

from app.models import ReceiptDetailsBase


class ReceiptDetailsCreate(ReceiptDetailsBase):
    receipt_id: uuid.UUID

class ReceiptDetailsReceiptIn(ReceiptDetailsBase):
    pass

class ReceiptDetailsPublic(ReceiptDetailsBase):
    id: uuid.UUID
    receipt_id: uuid.UUID


class ReceiptDetailsUpdate(SQLModel):
    ibfm: str | None = Field(default=None, max_length=50)
    bf: int | None = Field(default=None)
    ibk: int | None = Field(default=None)
    digital_signature: str | None = Field(default=None, max_length=255)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
