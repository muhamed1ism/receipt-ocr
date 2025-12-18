import uuid
from typing import Any

from sqlmodel import Session

from app.crud.product import get_or_create_product
from app.models import ReceiptItem
from app.schemas import ReceiptItemCreate, ReceiptItemUpdate, ProductCreate


def create_receipt_item(
    *,
    session: Session,
    receipt_item_data: ReceiptItemCreate,
    receipt_id: uuid.UUID | None,
) -> ReceiptItem:
    product_data = ProductCreate(
        name=receipt_item_data.name,
    )
    product = get_or_create_product(
        session=session,
        product_data=product_data
    )

    receipt_item_create = receipt_item_data.model_dump(
        exclude={
            "product",
        }
    )
    db_obj = ReceiptItem(
        **receipt_item_create,
        receipt_id=receipt_id,
        product_id=product.id,
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
