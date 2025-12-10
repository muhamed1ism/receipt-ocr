from typing import Any

from sqlmodel import Session

from app.models import Receipt, ReceiptCreate, ReceiptUpdate


def create_receipt(*, session: Session, receipt_create: ReceiptCreate) -> Receipt:
    db_obj = Receipt.model_validate(
        receipt_create,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_receipt(
    *, session: Session, db_receipt: Receipt, receipt_in: ReceiptUpdate
) -> Any:
    receipt_data = receipt_in.model_dump(exclude_unset=True)
    extra_data = {}

    db_receipt.sqlmodel_update(receipt_data, update=extra_data)
    session.add(db_receipt)
    session.commit()
    session.refresh(db_receipt)
    return db_receipt
