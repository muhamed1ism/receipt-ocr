import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Receipt,
    ReceiptDetailsCreate,
    ReceiptDetailsPublic,
    ReceiptDetailsUpdate,
)

router = APIRouter(prefix="/receipt_details", tags=["receipt_details"])


@router.get(
    "/{receipt_id}",
    response_model=ReceiptDetailsPublic,
)
def read_receipt_details(
    session: SessionDep,
    receipt_id: uuid.UUID,
    current_user: CurrentUser,
) -> ReceiptDetailsPublic:
    """
    Retrieve receipt details.
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
    return ReceiptDetailsPublic.model_validate(receipt_details)


@router.post(
    "/",
    response_model=ReceiptDetailsPublic,
)
def create_receipt_details(
    session: SessionDep,
    receipt_details_in: ReceiptDetailsCreate,
    receipt_id: uuid.UUID,
    current_user: CurrentUser,
) -> ReceiptDetailsPublic:
    """
    Create my receipt details.
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

    receipt_details = crud.get_receipt_details_by_receipt_id(
        session=session, receipt_id=receipt_id
    )
    if receipt_details:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Receipt details already exist for this receipt",
        )

    receipt_details = crud.create_receipt_details(
        session=session,
        receipt_details_create=receipt_details_in,
        receipt_id=receipt_id,
    )

    return ReceiptDetailsPublic.model_validate(receipt_details)


@router.patch(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ReceiptDetailsPublic,
)
def update_receipt_details(
    session: SessionDep,
    receipt_details_in: ReceiptDetailsUpdate,
    receipt_id: uuid.UUID,
) -> ReceiptDetailsPublic:
    """
    Update receipt details.
    """

    receipt_details = crud.get_receipt_details_by_receipt_id(
        session=session, receipt_id=receipt_id
    )
    if not receipt_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt details not found",
        )

    new_receipt_details = crud.update_receipt_details(
        session=session,
        db_receipt_details=receipt_details,
        receipt_details_update=receipt_details_in,
    )
    return ReceiptDetailsPublic.model_validate(new_receipt_details)
