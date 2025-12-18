from sqlmodel import Session, func, select

from app.models import Store
from app.schemas import StoreCreate, StoreReceiptIn, StorePublic, StoresPublic, StoreUpdate


def get_or_create_store(*, session: Session, store_data: StoreCreate | StoreReceiptIn) -> Store:
    store = session.exec(
        select(Store).where(Store.name == store_data.name)
    ).one_or_none()
    if store:
        return store

    new_store = Store.model_validate(
        store_data,
    )
    session.add(new_store)
    session.commit()
    session.refresh(new_store)
    return new_store


def update_store(
    *,
    session: Session,
    db_store: Store,
    store_in: StoreUpdate,
) -> Store:
    store_data = store_in.model_dump(exclude_unset=True)
    extra_data = {}

    db_store.sqlmodel_update(store_data, update=extra_data)
    session.add(db_store)
    session.commit()
    session.refresh(db_store)
    return db_store


def get_all_stores(
    *, session: Session, skip: int = 0, limit: int = 0
) -> StoresPublic | None:
    count_statement = select(func.count()).select_from(Store)
    count = session.exec(count_statement).one()

    statement = select(Store).offset(skip).limit(limit)
    receipts = session.exec(statement).all()
    pub_receipts = [StorePublic.model_validate(r) for r in receipts]

    return StoresPublic(data=pub_receipts, count=count)


def delete_store(*, session: Session, store_id) -> StorePublic | None:
    statement = select(Store).where(Store.id == store_id)
    store = session.exec(statement).one()
    if not store:
        return None

    session.delete(store)
    return StorePublic.model_validate(store)
