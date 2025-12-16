import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
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
    receipt = crud.create_receipt(session=session, receipt_data=receipt_in, user_id=current_user.id)
    return ReceiptPublic.model_validate(receipt)


@router.patch(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ReceiptPublic,
)
def update_receipt(
    *, session: SessionDep, receipt_in: ReceiptUpdate, receipt_id: uuid.UUID
) -> ReceiptPublic:
    """
    Update user receipt with receipt_id.
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
