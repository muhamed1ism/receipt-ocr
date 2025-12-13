import uuid

from fastapi import APIRouter, HTTPException, status

from app import crud
from app.api.deps import SessionDep
from app.models import Store, StorePublic, StoresPublic
from app.models.receipt import Receipt
from app.models.store import StoreCreate

router = APIRouter(prefix="/store", tags=["store"])


@router.get("/", response_model=StoresPublic)
def read_all_stores(session: SessionDep, skip: int = 0, limit: int = 0) -> StoresPublic:
    stores = crud.get_all_stores(session=session, skip=skip, limit=limit)
    if not stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stores not found",
        )

    return stores


@router.get("/{store_id}", response_model=StorePublic)
def read_store_by_id(session: SessionDep, store_id: uuid.UUID) -> StorePublic:
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found",
        )

    return StorePublic.model_validate(store)


@router.post("/", response_model=StorePublic)
def add_store(
    session: SessionDep, store_in: StoreCreate, receipt_id: uuid.UUID
) -> StorePublic:
    receipt = session.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    store = Store.model_validate(store_in)
    db_store = session.get(Store, store.id)
    if db_store:
        statement = crud.update_sto

    store_data = store_in.model_copy(update={"receipt_id": receipt_id})
    store = crud.create_store(
        session=session,
    )
