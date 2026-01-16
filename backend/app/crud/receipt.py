import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlmodel import Session, String, cast, col, desc, func, or_, select

from app.models import Profile, Receipt, ReceiptItem, User
from app.models.branch import Branch
from app.models.receipt_details import ReceiptDetails
from app.models.store import Store
from app.schemas import (
    ReceiptCreate,
    ReceiptPublicDetailed,
    ReceiptsPublicDetailed,
    ReceiptUpdate,
)
from app.schemas.receipt import ReceiptPublicDetailedMe, ReceiptsPublicDetailedMe


def create_receipt(
    *,
    session: Session,
    receipt_data: ReceiptCreate,
    user_id: uuid.UUID,
    branch_id: uuid.UUID,
) -> Receipt:
    receipt_create = receipt_data.model_dump(
        exclude={
            "store",
            "branch",
            "details",
            "items",
        }
    )

    receipt = Receipt(
        **receipt_create,
        user_id=user_id,
        branch_id=branch_id,
    )

    session.add(receipt)
    session.commit()
    session.refresh(receipt)
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
    *,
    session: Session,
    skip: int = 0,
    limit: int = 40,
    query: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ReceiptsPublicDetailed | None:
    statement = select(Receipt)

    if query is not None:
        statement = (
            statement.join(Receipt.user)
            .join(User.profile)
            .join(Receipt.items)
            .join(Receipt.branch)
            .join(Receipt.details)
            .join(Branch.store)
            .where(
                or_(
                    func.to_char(Receipt.date_time, "DD. MM. YYYY. HH24:MI:SS").ilike(
                        f"%{query}%"
                    ),
                    cast(Receipt.tax_amount, String).ilike(f"%{query}%"),
                    cast(Receipt.total_amount, String).ilike(f"%{query}%"),
                    col(Receipt.payment_method).ilike(f"%{query}%"),
                    col(User.email).ilike(f"%{query}%"),
                    col(Profile.first_name).ilike(f"%{query}%"),
                    col(Profile.last_name).ilike(f"%{query}%"),
                    col(Profile.country).ilike(f"%{query}%"),
                    col(Profile.city).ilike(f"%{query}%"),
                    col(Profile.address).ilike(f"%{query}%"),
                    col(Profile.phone_number).ilike(f"%{query}%"),
                    func.to_char(Profile.date_of_birth, "DD. MM. YYYY.").ilike(
                        f"%{query}%"
                    ),
                    col(ReceiptItem.name).ilike(f"%{query}%"),
                    cast(ReceiptItem.quantity, String).ilike(f"%{query}%"),
                    cast(ReceiptItem.price, String).ilike(f"%{query}%"),
                    cast(ReceiptItem.total_price, String).ilike(f"%{query}%"),
                    col(ReceiptDetails.ibfm).ilike(f"%{query}%"),
                    col(ReceiptDetails.bf).ilike(f"%{query}%"),
                    col(Branch.address).ilike(f"%{query}%"),
                    col(Branch.city).ilike(f"%{query}%"),
                    col(Store.name).ilike(f"%{query}%"),
                    cast(Store.jib, String).ilike(f"%{query}%"),
                    cast(Store.pib, String).ilike(f"%{query}%"),
                )
            )
            .distinct()
        )

    if date_from is not None:
        statement = statement.where(
            col(Receipt.date_time) >= datetime.fromisoformat(date_from)
        )

    if date_to is not None:
        statement = statement.where(
            col(Receipt.date_time) <= datetime.fromisoformat(date_to)
        )

    count_statement = (
        select(func.count()).select_from(statement.subquery()).order_by(None)
    )
    count = session.exec(count_statement).one()

    statement = statement.order_by(desc(Receipt.date_time)).limit(limit).offset(skip)
    receipts = session.exec(statement).all()
    receipt_list: Sequence[ReceiptPublicDetailed] = [
        ReceiptPublicDetailed.model_validate(r) for r in receipts
    ]

    return ReceiptsPublicDetailed(data=receipt_list, count=count)


def get_my_receipts(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 40,
    my_user: User,
    query: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ReceiptsPublicDetailedMe | None:
    statement = select(Receipt)

    if query is not None:
        statement = (
            select(Receipt)
            .join(Receipt.items)
            .join(Receipt.branch)
            .join(Branch.store)
            .where(
                or_(
                    func.to_char(Receipt.date_time, "DD. MM. YYYY. HH24:MI:SS").ilike(
                        f"%{query}%"
                    ),
                    cast(Receipt.tax_amount, String).ilike(f"%{query}%"),
                    cast(Receipt.total_amount, String).ilike(f"%{query}%"),
                    col(Receipt.payment_method).ilike(f"%{query}%"),
                    func.to_char(Profile.date_of_birth, "DD. MM. YYYY.").ilike(
                        f"%{query}%"
                    ),
                    col(ReceiptItem.name).ilike(f"%{query}%"),
                    cast(ReceiptItem.quantity, String).ilike(f"%{query}%"),
                    cast(ReceiptItem.price, String).ilike(f"%{query}%"),
                    cast(ReceiptItem.total_price, String).ilike(f"%{query}%"),
                    col(Branch.address).ilike(f"%{query}%"),
                    col(Branch.city).ilike(f"%{query}%"),
                    col(Store.name).ilike(f"%{query}%"),
                    cast(Store.jib, String).ilike(f"%{query}%"),
                    cast(Store.pib, String).ilike(f"%{query}%"),
                )
            )
            .where(Receipt.user_id == my_user.id)
            .distinct()
        )

    if date_from is not None:
        statement = statement.where(
            col(Receipt.date_time) >= datetime.fromisoformat(date_from)
        )

    if date_to is not None:
        statement = statement.where(
            col(Receipt.date_time) <= datetime.fromisoformat(date_to)
        )

    count_statement = (
        select(func.count()).select_from(statement.subquery()).order_by(None)
    )
    count = session.exec(count_statement).one()

    statement = statement.order_by(desc(Receipt.date_time)).limit(limit).offset(skip)
    receipts = session.exec(statement).all()
    receipt_list: Sequence[ReceiptPublicDetailedMe] = [
        ReceiptPublicDetailedMe.model_validate(r) for r in receipts
    ]

    return ReceiptsPublicDetailedMe(data=receipt_list, count=count)
