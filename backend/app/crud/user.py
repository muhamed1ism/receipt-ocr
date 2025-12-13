from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate
from app.models.common import Message
from app.models.user import UserUpdateMe


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        password = user_data["password"]
        extra_data["hashed_password"] = get_password_hash(password)

    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user_me(
    *, session: Session, user_update: UserUpdateMe, my_user: User
) -> User:
    user_data = user_update.model_dump(exclude_unset=True)
    my_user.sqlmodel_update(user_data)
    session.add(my_user)
    session.commit()
    session.refresh(my_user)
    return my_user


def update_password_me(
    *, session: Session, new_password: str, my_user: User
) -> Message:
    hashed_password = get_password_hash(new_password)
    my_user.hashed_password = hashed_password
    session.add(my_user)
    session.commit()
    return Message(message="Password updated successfully")


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
