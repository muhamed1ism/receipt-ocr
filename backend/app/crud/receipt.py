import uuid

from sqlmodel import Session, func, select

from app.models import Receipt, ReceiptCreate, ReceiptUpdate
from app.models.receipt import ReceiptPublic, ReceiptsPublic
from app.models.user import User


def create_receipt(*, session: Session, receipt_create: ReceiptCreate) -> Receipt:
    db_obj = Receipt.model_validate(
        receipt_create,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_receipt(
    *, session: Session, db_receipt: Receipt, receipt_update: ReceiptUpdate
) -> Receipt:
    receipt_data = receipt_update.model_dump(exclude_unset=True)
    extra_data = {}

    db_receipt.sqlmodel_update(receipt_data, update=extra_data)
    session.add(db_receipt)
    session.commit()
    session.refresh(db_receipt)
    return db_receipt


def get_receipt_by_id(*, session: Session, receipt_id: uuid.UUID) -> Receipt | None:
    statement = select(Receipt).where(Receipt.id == receipt_id)

    receipt = session.exec(statement).first()
    return receipt


def get_all_receipts(
    *, session: Session, skip: int = 0, limit: int = 0
) -> ReceiptsPublic | None:
    count_statement = select(func.count()).select_from(Receipt)
    count = session.exec(count_statement).one()

    statement = select(Receipt).offset(skip).limit(limit)
    receipts = session.exec(statement).all()
    pub_receipts = [ReceiptPublic.model_validate(r) for r in receipts]

    return ReceiptsPublic(data=pub_receipts, count=count)


def get_my_receipts(
    *, session: Session, skip: int = 0, limit: int = 0, my_user: User
) -> ReceiptsPublic | None:
    count_statement = (
        select(func.count()).select_from(Receipt).where(Receipt.user_id == my_user.id)
    )
    count = session.exec(count_statement).one()

    statement = select(Receipt).offset(skip).limit(limit)
    receipts = session.exec(statement).all()
    pub_receipts = [ReceiptPublic.model_validate(r) for r in receipts]

    return ReceiptsPublic(data=pub_receipts, count=count)
