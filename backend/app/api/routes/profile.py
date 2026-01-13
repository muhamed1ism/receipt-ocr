import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.schemas import (
    ProfileCreate,
    ProfilePublic,
    ProfilesPublic,
    ProfileUpdate,
)
from app.schemas.profile import ProfileCreateMe

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfilesPublic,
)
def read_profiles(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> ProfilesPublic | None:
    """
    Retrieve profiles.
    """

    return crud.get_all_profiles(session=session, skip=skip, limit=limit)


@router.get(
    "/me",
    response_model=ProfilePublic,
)
def read_profile_me(
    session: SessionDep, current_user: CurrentUser
) -> ProfilePublic | None:
    """
    Retrieve profiles.
    """
    profile = crud.get_profile_by_user_id(session=session, user_id=current_user.id)
    pub_profile = ProfilePublic.model_validate(profile)

    return pub_profile


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfilePublic,
)
def create_profile(*, session: SessionDep, profile_in: ProfileCreate) -> ProfilePublic:
    """
    Create new profile.
    """
    profile = crud.get_profile_by_user_id(session=session, user_id=profile_in.user_id)
    if profile:
        raise HTTPException(
            status_code=400,
            detail="User already has profile in the system.",
        )

    profile = crud.create_profile(session=session, profile_create=profile_in)
    return ProfilePublic.model_validate(profile)


@router.post(
    "/me",
    response_model=ProfilePublic,
)
def create_profile_me(
    *, session: SessionDep, profile_in: ProfileCreateMe, current_user: CurrentUser
) -> ProfilePublic:
    """
    Create my new profile.
    """
    profile = crud.get_profile_by_user_id(session=session, user_id=current_user.id)
    if profile:
        raise HTTPException(
            status_code=400,
            detail="You already have profile in the system.",
        )

    profile_data = ProfileCreate(**profile_in.model_dump(), user_id=current_user.id)
    profile = crud.create_profile(session=session, profile_create=profile_data)
    return ProfilePublic.model_validate(profile)


@router.patch(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfilePublic,
)
def update_profile(
    *, session: SessionDep, user_id: uuid.UUID, profile_in: ProfileUpdate
) -> ProfilePublic:
    """
    Update user profile.
    """

    profile_db = crud.get_profile_by_user_id(session=session, user_id=user_id)
    if not profile_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    new_profile = crud.update_profile(
        session=session, db_profile=profile_db, profile_update=profile_in
    )
    return ProfilePublic.model_validate(new_profile)


@router.patch("/me", response_model=ProfilePublic)
def update_profile_me(
    *, session: SessionDep, profile_in: ProfileUpdate, current_user: CurrentUser
) -> ProfilePublic:
    """
    Update own profile.
    """
    current_profile = crud.get_profile_by_user_id(
        session=session, user_id=current_user.id
    )
    if not current_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    new_profile = crud.update_profile(
        session=session, db_profile=current_profile, profile_update=profile_in
    )
    return ProfilePublic.model_validate(new_profile)
