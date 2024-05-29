import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from . import db_models

def initialize_user(db: Session, user_id: int, nickname: str, speciality: str, name_of_group: str, is_get_reminds: bool, reminding_time: str):
    """
    Функція для ініціалізації користувача в базі даних.

    Args:
    - db: Сесія бази даних.
    - user_id: ID користувача.
    - nickname: Нікнейм користувача.
    - speciality: Спеціальність користувача.
    - name_of_group: Назва групи користувача.
    - is_get_reminds: Флаг, що позначає, чи користувач отримує нагадування.
    - reminding_time: Час, коли користувач отримує нагадування.
    """
    db_user = db_models.User(
        id=user_id,
        nickname=nickname,
        speciality=speciality,
        name_of_group=name_of_group,
        is_get_reminds=is_get_reminds,
        reminding_time=reminding_time
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    """
    Функція для отримання користувача за його ID.

    Args:
    - db: Сесія бази даних.
    - user_id: ID користувача.

    Returns:
    - Об'єкт користувача з вказаним ID.
    """
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()

def update_user_info(db: Session, user_id: int, nickname: str = None, speciality: str = None, name_of_group: str = None, is_get_reminds: bool = None, reminding_time: str = None):
    """
    Функція для оновлення інформації про користувача.
    """
    db_user = get_user_by_id(db, user_id)
    if db_user:
        if nickname is not None:
            db_user.nickname = nickname
        if speciality is not None:
            db_user.speciality = speciality
        if name_of_group is not None:
            db_user.name_of_group = name_of_group
        if is_get_reminds is not None:
            db_user.is_get_reminds = is_get_reminds
        if reminding_time is not None:
            db_user.reminding_time = reminding_time
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """
    Функція для видалення користувача за його ID.
    """
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user