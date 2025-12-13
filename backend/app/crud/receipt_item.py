import uuid
from typing import Any

from sqlmodel import Session

from app.models import ReceiptItem, ReceiptItemCreate, ReceiptItemUpdate


def create_receipt_item(
    *,
    session: Session,
    receipt_item_create: ReceiptItemCreate,
    receipt_id: uuid.UUID,
) -> ReceiptItem:
    receipt_item_data = receipt_item_create.model_copy(
        update={"receipt_id": receipt_id}
    )
    db_obj = ReceiptItem.model_validate(
        receipt_item_data,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_receipt_item(
    *,
    session: Session,
    db_receipt_item: ReceiptItem,
    receipt_item_update: ReceiptItemUpdate,
) -> Any:
    receipt_item_data = receipt_item_update.model_dump(exclude_unset=True)
    extra_data = {}

    db_receipt_item.sqlmodel_update(receipt_item_data, update=extra_data)
    session.add(db_receipt_item)
    session.commit()
    session.refresh(db_receipt_item)
    return db_receipt_item
