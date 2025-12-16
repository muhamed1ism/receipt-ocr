import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Receipt,
    ReceiptItemCreate,
    ReceiptItemPublic,
    ReceiptItemsPublic,
    ReceiptItemUpdate,
)
from app.models.receipt_item import ReceiptItem

router = APIRouter(prefix="/receipt_item", tags=["receipt_item"])


@router.get(
    "/{receipt_id}",
    response_model=ReceiptItemsPublic,
)
def read_receipt_items(
    session: SessionDep,
    receipt_id: uuid.UUID,
    current_user: CurrentUser,
) -> ReceiptItemsPublic:
    """
    Retrieve receipt items.
    """

    receipt = session.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    if not current_user.is_superuser and receipt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    receipt_details = crud.get_receipt_details_by_receipt_id(
        session=session, receipt_id=receipt_id
    )
    return ReceiptItemsPublic.model_validate(receipt_details)


@router.post(
    "/",
    response_model=ReceiptItemPublic,
)
def create_receipt_details(
    session: SessionDep,
    receipt_item_in: ReceiptItemCreate,
    receipt_id: uuid.UUID,
    current_user: CurrentUser,
) -> ReceiptItemPublic:
    """
    Create my receipt item.
    """

    receipt = session.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found"
        )

    if receipt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create receipt details for this receipt",
        )

    receipt_item = crud.create_receipt_item(
        session=session,
        receipt_item_data=receipt_item_in,
        receipt_id=receipt_id,
    )

    return ReceiptItemPublic.model_validate(receipt_item)


@router.patch(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ReceiptItemPublic,
)
def update_receipt_details(
    session: SessionDep,
    receipt_item_in: ReceiptItemUpdate,
    id: uuid.UUID,
) -> ReceiptItemPublic:
    """
    Update receipt item.
    """

    receipt_item = session.get(ReceiptItem, id)
    if not receipt_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt item not found",
        )

    new_receipt_item = crud.update_receipt_item(
        session=session,
        db_receipt_item=receipt_item,
        receipt_item_update=receipt_item_in,
    )
    return ReceiptItemPublic.model_validate(new_receipt_item)
