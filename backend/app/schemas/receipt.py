import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.enums import CurrencyEnum
from app.models import ReceiptBase
from app.schemas.branch import BranchPublicWithStore, BranchReceiptIn
from app.schemas.receipt_details import ReceiptDetailsPublic, ReceiptDetailsReceiptIn
from app.schemas.receipt_item import (
    ReceiptItemCreate,
    ReceiptItemPublic,
)
from app.schemas.store import StoreReceiptIn
from app.schemas.user import UserPublicWithProfile


class ReceiptCreate(ReceiptBase):
    store: StoreReceiptIn
    branch: BranchReceiptIn
    details: ReceiptDetailsReceiptIn
    items: list[ReceiptItemCreate]


class ReceiptPublic(ReceiptBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ReceiptPublicDetailed(ReceiptPublic):
    details: ReceiptDetailsPublic
    items: list[ReceiptItemPublic] = []
    branch: BranchPublicWithStore
    user: UserPublicWithProfile


class ReceiptsPublicDetailed(SQLModel):
    data: Sequence[ReceiptPublicDetailed]
    count: int


class ReceiptPublicDetailedMe(ReceiptPublic):
    details: ReceiptDetailsPublic
    items: list[ReceiptItemPublic] = []
    branch: BranchPublicWithStore


class ReceiptsPublicDetailedMe(SQLModel):
    data: Sequence[ReceiptPublicDetailedMe]
    count: int


class ReceiptsPublic(SQLModel):
    data: list[ReceiptPublic]
    count: int


class ReceiptUpdate(SQLModel):
    date_time: datetime | None = Field(default=None)
    tax: float | None = Field(default=None)
    total_price: float | None = Field(default=None)
    payment_method: str | None = Field(default=None, max_length=50)
    currency: CurrencyEnum | None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
