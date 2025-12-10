from typing import Any

from sqlmodel import Session

from app.models import Store, StoreCreate, StoreUpdate


def create_store(*, session: Session, store_create: StoreCreate) -> Store:
    db_obj = Store.model_validate(
        store_create,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_store(
    *,
    session: Session,
    db_store: Store,
    store_in: StoreUpdate,
) -> Any:
    store_data = store_in.model_dump(exclude_unset=True)
    extra_data = {}

    db_store.sqlmodel_update(store_data, update=extra_data)
    session.add(db_store)
    session.commit()
    session.refresh(db_store)
    return db_store
