import uuid
from typing import Any

from sqlmodel import Session, select

from app.models import ReceiptDetails
from app.schemas import ReceiptDetailsCreate, ReceiptDetailsUpdate, ReceiptDetailsReceiptIn

def get_or_create_receipt_details(
        *,
        session: Session,
        receipt_details_data: ReceiptDetailsCreate | ReceiptDetailsReceiptIn,
        receipt_id
) -> ReceiptDetails:
        details = session.exec(
            select(ReceiptDetails).where(ReceiptDetails.receipt_id == receipt_id)
        ).first()
        if details:
            return details

        receipt_details_create = receipt_details_data.model_copy(
            update={"receipt_id": receipt_id}
        )

        new_details = ReceiptDetails.model_validate(
            receipt_details_create,
        )
        session.add(new_details)
        session.commit()
        session.refresh(new_details)
        return new_details


def update_receipt_details(
    *,
    session: Session,
    db_receipt_details: ReceiptDetails,
    receipt_details_update: ReceiptDetailsUpdate,
) -> Any:
    receipt_details_data = receipt_details_update.model_dump(exclude_unset=True)
    extra_data = {}

    db_receipt_details.sqlmodel_update(receipt_details_data, update=extra_data)
    session.add(db_receipt_details)
    session.commit()
    session.refresh(db_receipt_details)
    return db_receipt_details


def get_receipt_details_by_receipt_id(
    *,
    session: Session,
    receipt_id: uuid.UUID,
) -> ReceiptDetails | None:
    statement = select(ReceiptDetails).where(receipt_id == receipt_id)
    return session.exec(statement).first()
