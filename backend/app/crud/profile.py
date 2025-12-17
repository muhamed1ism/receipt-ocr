import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.models import Profile
from app.schemas import ProfileCreate, ProfilePublic, ProfilesPublic, ProfileUpdate


def create_profile(*, session: Session, profile_create: ProfileCreate) -> Profile:
    db_obj = Profile.model_validate(
        profile_create,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_profile(
    *,
    session: Session,
    db_profile: Profile,
    profile_update: ProfileUpdate,
) -> Any:
    profile_data = profile_update.model_dump(exclude_unset=True)
    extra_data = {}

    db_profile.sqlmodel_update(profile_data, update=extra_data)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


def get_all_profiles(*, session: Session, skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(Profile)
    count = session.exec(count_statement).one()

    statement = select(Profile).offset(skip).limit(limit)
    profiles = session.exec(statement).all()
    pub_profiles = [ProfilePublic.model_validate(u) for u in profiles]

    return ProfilesPublic(data=pub_profiles, count=count)


def get_profile_by_user_id(*, session: Session, user_id: uuid.UUID) -> Profile | None:
    statement = select(Profile).where(user_id == Profile.user_id)
    return session.exec(statement).first()
