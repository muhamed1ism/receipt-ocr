from typing import Any

from sqlmodel import Session

from app.models import (
    ReceiptDetails,
    ReceiptDetailsCreate,
    ReceiptDetailsUpdate,
)


def create_receipt_details(
    *, session: Session, receipt_details_create: ReceiptDetailsCreate
) -> ReceiptDetails:
    db_obj = ReceiptDetails.model_validate(
        receipt_details_create,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_receipt_details(
    *,
    session: Session,
    db_receipt_details: ReceiptDetails,
    receipt_details_in: ReceiptDetailsUpdate,
) -> Any:
    receipt_details_data = receipt_details_in.model_dump(exclude_unset=True)
    extra_data = {}

    db_receipt_details.sqlmodel_update(receipt_details_data, update=extra_data)
    session.add(db_receipt_details)
    session.commit()
    session.refresh(db_receipt_details)
    return db_receipt_details
