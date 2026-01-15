import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.models import BranchBase
from app.schemas.store import StorePublic


class BranchCreate(BranchBase):
    store_id: uuid.UUID


class BranchReceiptIn(BranchBase):
    pass


class BranchPublic(BranchBase):
    id: uuid.UUID


class BranchesPublic(SQLModel):
    data: list[BranchPublic]
    count: int


class BranchPublicWithStore(BranchPublic):
    store: StorePublic


class BranchUpdate(SQLModel):
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

