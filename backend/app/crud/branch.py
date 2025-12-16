import uuid

from sqlmodel import Session, select

from app.models import BranchCreate, Branch, BranchReceiptIn


def get_or_create_branch(*, session: Session, branch_data: BranchCreate | BranchReceiptIn, store_id: uuid.UUID) -> Branch:
    branch = session.exec(
        select(Branch).where(
            Branch.store_id == store_id,
            Branch.address == branch_data.address,
            Branch.city == branch_data.city,
        )
    ).one_or_none()

    if branch:
        return branch

    branch_create = branch_data.model_copy(update={"store_id": store_id})
    db_obj = Branch.model_validate(
        branch_create,
    )
    session.add(db_obj)
    session.flush()
    return db_obj