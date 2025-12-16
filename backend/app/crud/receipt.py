import uuid

from sqlmodel import Session, func, select

from app.crud import get_or_create_store, create_receipt_item
from app.crud.branch import get_or_create_branch
from app.models import Receipt, ReceiptCreate, ReceiptUpdate
from app.models.receipt import ReceiptPublic, ReceiptsPublic
from app.models.user import User


def create_receipt(*, session: Session, receipt_data: ReceiptCreate, user_id: uuid.UUID) -> Receipt:
    with session.begin():
        store = get_or_create_store(session=session, store_data=receipt_data.store)
        branch = get_or_create_branch(session=session, branch_data=receipt_data.branch, store_id=store.id)


        receipt_create = receipt_data.model_dump(
            exclude={
                "store",
                "branch",
                "items",
            }
        )

        receipt = Receipt(
            **receipt_create,
            user_id=user_id,
            branch_id=branch.id,
        )

        session.add(receipt)
        session.flush()

        created_items = []
        for item in receipt_data.items:
            db_item = create_receipt_item(session=session, receipt_item_data=item, receipt_id=receipt.id)
            created_items.append(db_item)

        receipt.items = created_items
        return receipt


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
