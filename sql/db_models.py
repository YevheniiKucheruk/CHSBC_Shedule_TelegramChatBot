import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship
from .database import Base

class Group(Base):
    __tablename__ = 'Groups'

    id = Column(Integer, primary_key=True)
    name_of_group = Column(String(30), nullable=False)
    speciality = Column(String(30), nullable=False)

class Week(Base):
    __tablename__ = 'week'

    id = Column(Integer, primary_key=True)
    is_upper = Column(Boolean, nullable=False)
    is_lower = Column(Boolean, nullable=False)

class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    nickname = Column(String(100))
    speciality = Column(String(100))
    name_of_group = Column(String(50))
    is_get_reminds = Column(Boolean, nullable=False)
    reminding_time = Column(Time, nullable=False)

class Monday(Base):
    __tablename__ = 'monday'

    id = Column(Integer, primary_key=True)
    num_of_lesson = Column(Integer, nullable=False)
    name_of_lesson = Column(String(30), nullable=False)
    lesson_room = Column(Integer, nullable=False)
    teacher_name = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey('Groups.id'))
    is_upper = Column(Boolean, nullable=False)
    subgroup = Column(String(30))
    group = relationship("Group")

class Tuesday(Base):
    __tablename__ = 'tuesday'

    id = Column(Integer, primary_key=True)
    num_of_lesson = Column(Integer, nullable=False)
    name_of_lesson = Column(String(30), nullable=False)
    lesson_room = Column(Integer, nullable=False)
    teacher_name = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey('Groups.id'))
    is_upper = Column(Boolean, nullable=False)
    subgroup = Column(String(30))
    group = relationship("Group")

class Wednesday(Base):
    __tablename__ = 'wednesday'

    id = Column(Integer, primary_key=True)
    num_of_lesson = Column(Integer, nullable=False)
    name_of_lesson = Column(String(30), nullable=False)
    lesson_room = Column(Integer, nullable=False)
    teacher_name = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey('Groups.id'))
    is_upper = Column(Boolean, nullable=False)
    subgroup = Column(String(30))
    group = relationship("Group")

class Thursday(Base):
    __tablename__ = 'thursday'

    id = Column(Integer, primary_key=True)
    num_of_lesson = Column(Integer, nullable=False)
    name_of_lesson = Column(String(30), nullable=False)
    lesson_room = Column(Integer, nullable=False)
    teacher_name = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey('Groups.id'))
    is_upper = Column(Boolean, nullable=False)
    subgroup = Column(String(30))
    group = relationship("Group")

class Friday(Base):
    __tablename__ = 'friday'

    id = Column(Integer, primary_key=True)
    num_of_lesson = Column(Integer, nullable=False)
    name_of_lesson = Column(String(30), nullable=False)
    lesson_room = Column(Integer, nullable=False)
    teacher_name = Column(String(30), nullable=False)
    group_id = Column(Integer, ForeignKey('Groups.id'))
    is_upper = Column(Boolean, nullable=False)
    subgroup = Column(String(30))
    group = relationship("Group")

class Time(Base):
    __tablename__ = 'time'

    id = Column(Integer, primary_key=True)
    num_of_lesson = Column(Integer, nullable=False)
    time_of_begin = Column(Time, nullable=False)
    time_of_end = Column(Time, nullable=False)