from sqlalchemy.orm import Session

from app.models.user import Role, User


def list_users(db: Session) -> list[User]:
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def update_user_status(db: Session, user_id: str, is_active: bool) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def update_user_role(db: Session, user_id: str, role: Role) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user
