import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlmodel import Session, and_, distinct, func, or_, select

from app.models import Profile, Receipt, ReceiptItem, User
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
    limit: int = 0,
    query: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> ReceiptsPublicDetailed | None:
    count_statement = select(func.count()).select_from(Receipt)
    count = session.exec(count_statement).one()

    statement = (
        select(Receipt)
        .join(User, Receipt.user_id == User.id)
        .outerjoin(Profile, User.id == Profile.user_id)
        # we aready using this in a different way
    )

    filters = []

    # Search trough user's name, email or receipt items
    if query:
        # joining receipt items to search product names
        statement = statement.outerjoin(
            ReceiptItem, Receipt.id == ReceiptItem.receipt_id
        )

        # create search filter for user info and items
        search_filter = or_(
            User.email.ilike(f"%{query}%"),
            Profile.first_name.ilike(f"%{query}%"),
            Profile.last_name.ilike(f"%{query}%"),
            ReceiptItem.name.ilike(f"%{query}%"),
        )
        filters.append(search_filter)

    # date range filters
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            filters.append(Receipt.date_time >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            filters.append(Receipt.date_time <= to_date)
        except ValueError:
            pass

    # Apply all filters
    if filters:
        statement = statement.where(and_(*filters))

    # Use distinct to  avoid duplication from joins
    statement = statement.distinct()

    # Count query
    count_statement = select(func.count(distinct(Receipt.id))).select_from(
        statement.subquery()
    )
    count = session.exec(count_statement).one()

    # Get results orderd by most recent
    statement = statement.order_by(Receipt.date_time.desc()).offset(skip).limit(limit)
    receipts = session.exec(statement).all()

    receipt_list: Sequence[ReceiptPublicDetailed] = [
        ReceiptPublicDetailed.model_validate(r) for r in receipts
    ]

    return ReceiptsPublicDetailed(data=receipt_list, count=count)


# ) -> ReceiptsPublic | None:
#     count_statement = select(func.count()).select_from(Receipt)
#     count = session.exec(count_statement).one()
#
#     statement = select(Receipt).offset(skip).limit(limit)
#     receipts = session.exec(statement).all()
#     pub_receipts = [ReceiptPublic.model_validate(r) for r in receipts]
#
#     return ReceiptsPublic(data=pub_receipts, count=count)


def get_my_receipts(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 0,
    my_user: User,
) -> ReceiptsPublicDetailedMe | None:
    count_statement = (
        select(func.count()).select_from(Receipt).where(Receipt.user_id == my_user.id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Receipt).where(Receipt.user_id == my_user.id).offset(skip).limit(limit)
    )
    receipts = session.exec(statement).all()
    receipt_list: Sequence[ReceiptPublicDetailedMe] = [
        ReceiptPublicDetailedMe.model_validate(r) for r in receipts
    ]

    return ReceiptsPublicDetailedMe(data=receipt_list, count=count)
