import uuid
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field

from app.models import BranchBase


class BranchCreate(BranchBase):
    store_id: uuid.UUID


class BranchReceiptIn(BranchBase):
    store_id: uuid.UUID


class BranchPublic(BranchBase):
    id: uuid.UUID


class BranchesPublic(SQLModel):
    data: list[BranchPublic]
    count: int


class BranchUpdate(SQLModel):
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
