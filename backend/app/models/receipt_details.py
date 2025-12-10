import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class ReceiptDetailsBase(SQLModel):
    ibfm: str | None = Field(default=None, max_length=50)
    bf: int | None = Field(default=None)
    ibk: int | None = Field(default=None)
    digital_signature: str | None = Field(default=None, max_length=255)

class ReceiptDetails(ReceiptDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    receipt_id: uuid.UUID = Field(foreign_key="receipt.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

class ReceiptDetailsCreate(ReceiptDetailsBase):
    pass

class ReceiptDetailsPublic(ReceiptDetailsBase):
    id: uuid.UUID
    receipt_id: uuid.UUID

class ReceiptDetailssPublic(SQLModel):
    data: list[ReceiptDetailsPublic]
    count: int

class ReceiptDetailsUpdate(SQLModel):
    ibfm: str | None = Field(default=None, max_length=50)
    bf: int | None = Field(default=None)
    ibk: int | None = Field(default=None)
    digital_signature: str | None = Field(default=None, max_length=255)
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))
