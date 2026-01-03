from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import String

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from app.crud import (
    create_receipt_item,
    get_or_create_branch,
    get_or_create_receipt_details,
    get_or_create_store,
)
from app.models.receipt import Receipt
from app.schemas import (
    ReceiptCreate,
    ReceiptPublic,
    ReceiptsPublic,
    ReceiptUpdate,
)

router = APIRouter(prefix="/receipt", tags=["receipt"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ReceiptPublic,
)
def read_receipts(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> ReceiptsPublic | None:
    """
    Retrieve all receipts.
    """
    receipts = crud.get_all_receipts(session=session, skip=skip, limit=limit)
    if not receipts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipts not found",
        )

    return receipts


@router.get(
    "/me",
    response_model=ReceiptsPublic,
)
def read_receipts_me(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> ReceiptsPublic | None:
    """
    Retrieve current user receipts.
    """
    receipt = crud.get_my_receipts(
        session=session, skip=skip, limit=limit, my_user=current_user
    )
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    return receipt


@router.post(
    "/create",
    response_model=ReceiptPublic,
)
def create_receipt(
    *, session: SessionDep, receipt_in: ReceiptCreate, current_user: CurrentUser
) -> ReceiptPublic:
    """
    Create my new receipt.
    """
    store = get_or_create_store(session=session, store_data=receipt_in.store)
    branch = get_or_create_branch(
        session=session, branch_data=receipt_in.branch, store_id=store.id
    )
    new_receipt = crud.create_receipt(
        session=session,
        receipt_data=receipt_in,
        user_id=current_user.id,
        branch_id=branch.id,
    )
    get_or_create_receipt_details(
        session=session,
        receipt_details_data=receipt_in.details,
        receipt_id=new_receipt.id,
    )

    created_items = []
    for item in receipt_in.items:
        db_item = create_receipt_item(
            session=session, receipt_item_data=item, receipt_id=new_receipt.id
        )
        created_items.append(db_item)
    return ReceiptPublic.model_validate(new_receipt)


@router.patch(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ReceiptPublic,
)
def update_receipt(
    *, session: SessionDep, receipt_in: ReceiptUpdate, receipt_id: uuid.UUID
) -> ReceiptPublic:
    """
    Update the user receipt with receipt_id.
    """

    receipt = crud.get_receipt_by_id(session=session, receipt_id=receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found."
        )

    new_receipt = crud.update_receipt(
        session=session, db_receipt=receipt, receipt_update=receipt_in
    )
    return ReceiptPublic.model_validate(new_receipt)


@router.delete("/{receipt_id}", dependencies=[Depends(get_current_user)])
def delete_receipt(
    *, session: SessionDep, receipt_id: uuid.UUID, current_user: CurrentUser
) -> Any:
    receipt = session.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    if receipt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not authorized to delete this receipt",
        )

    session.delete(receipt)
    session.commit()
    session.refresh(receipt)

    return "Receipt Deleted"
