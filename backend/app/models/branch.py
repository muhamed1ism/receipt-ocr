import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class BranchBase(SQLModel):
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)


class Branch(BranchBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    store_id: uuid.UUID = Field(
        foreign_key="store.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
