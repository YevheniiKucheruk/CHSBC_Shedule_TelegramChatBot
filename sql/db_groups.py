import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from .db_models import Group


def get_group_by_id(db: Session, group_id: int):
    """
    Функція для отримання групи за її ID.
    """
    return db.query(Group).filter(Group.id == group_id).first()

def get_groups_by_speciality(db: Session, speciality: str):
    """
    Функція для отримання списку груп за спеціальністю.
    """
    return db.query(Group).filter(Group.speciality == speciality).all()

def get_group_by_name(db: Session, group_name: str):
    """
    Функція для отримання групи за її назвою.
    """
    return db.query(Group).filter(Group.name_of_group == group_name).first()
