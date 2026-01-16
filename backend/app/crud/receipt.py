import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlmodel import Session, col, desc, func, or_, select

from app.api.deps import CurrentUser
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
from app.utils import cast_ilike, col_ilike, date_ilike, unaccent_ilike


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
            .outerjoin(User.profile)
            .join(Receipt.items)
            .join(Receipt.branch)
            .join(Receipt.details)
            .join(Branch.store)
            .where(
                or_(
                    # Receipt
                    date_ilike(Receipt.date_time, query),
                    cast_ilike(Receipt.tax_amount, query),
                    cast_ilike(Receipt.total_amount, query),
                    col_ilike(Receipt.payment_method, query),
                    # User
                    col_ilike(User.email, query),
                    # Profile
                    unaccent_ilike(Profile.first_name, query),
                    unaccent_ilike(Profile.last_name, query),
                    unaccent_ilike(Profile.country, query),
                    unaccent_ilike(Profile.city, query),
                    unaccent_ilike(Profile.address, query),
                    cast_ilike(Profile.phone_number, query),
                    date_ilike(Profile.date_of_birth, query),
                    # Receipt items
                    unaccent_ilike(ReceiptItem.name, query),
                    cast_ilike(ReceiptItem.quantity, query),
                    cast_ilike(ReceiptItem.price, query),
                    cast_ilike(ReceiptItem.total_price, query),
                    # Receipt details
                    col_ilike(ReceiptDetails.ibfm, query),
                    cast_ilike(ReceiptDetails.bf, query),
                    col_ilike(ReceiptDetails.digital_signature, query),
                    # Branch
                    unaccent_ilike(Branch.address, query),
                    unaccent_ilike(Branch.city, query),
                    # Store
                    unaccent_ilike(Store.name, query),
                    cast_ilike(Store.jib, query),
                    cast_ilike(Store.pib, query),
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
            col(Receipt.date_time) >= datetime.fromisoformat(date_to)
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
    my_user: CurrentUser,
    query: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ReceiptsPublicDetailedMe | None:
    statement = select(Receipt).where(Receipt.user_id == my_user.id)

    if query is not None:
        statement = (
            statement.join(Receipt.items)
            .join(Receipt.branch)
            .join(Receipt.details)
            .join(Branch.store)
            .where(
                or_(
                    # Receipt
                    date_ilike(Receipt.date_time, query),
                    cast_ilike(Receipt.tax_amount, query),
                    cast_ilike(Receipt.total_amount, query),
                    col_ilike(Receipt.payment_method, query),
                    # Receipt items
                    unaccent_ilike(ReceiptItem.name, query),
                    cast_ilike(ReceiptItem.quantity, query),
                    cast_ilike(ReceiptItem.price, query),
                    cast_ilike(ReceiptItem.total_price, query),
                    # Receipt details
                    col_ilike(ReceiptDetails.ibfm, query),
                    cast_ilike(ReceiptDetails.bf, query),
                    # Branch
                    unaccent_ilike(Branch.address, query),
                    unaccent_ilike(Branch.city, query),
                    # Store
                    unaccent_ilike(Store.name, query),
                    cast_ilike(Store.jib, query),
                    cast_ilike(Store.pib, query),
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
    receipt_list: Sequence[ReceiptPublicDetailedMe] = [
        ReceiptPublicDetailedMe.model_validate(r) for r in receipts
    ]
    return ReceiptsPublicDetailedMe(data=receipt_list, count=count)
