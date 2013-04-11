from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PlayerInfo(Base):
    __tablename__ = 'players'

    ID = Column(Integer, primary_key=True)
    FIRST_NAME = Column(String(255))
    LAST_NAME = Column(String(255))
    BAT_HAND = Column(String(1))
    THROW_HAND = Column(String(1))
    BIRTHDAY = Column(String(12))
    COLLEGE_YEAR = Column(String(4))
    COLLEGE_NAME = Column(String(255))
    DRAFT_STATUS = Column(String(255))
    HEIGHT = Column(String(6))
    HOMETOWN = Column(String(255))
    POSITIONS = Column(String(12))
    WEIGHT = Column(String(12))
    ID_POINTSTREAK = Column(Integer)
    #PREVIOUS_COLLEGE
    #HIGH_SCHOOL
