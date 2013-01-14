from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PlayerInfo(Base):
    __tablename__ = 'players'
    
    ID = Column(Integer, primary_key=True)
    BAT_HAND = Column(String)
    THROW_HAND = Column(String)
    BIRTHDAY = Column(String)
    COLLEGE_YEAR = Column(String)
    COLLEGE_NAME = Column(String)
    DRAFT_STATUS = Column(String)
    HEIGHT = Column(String)
    HOMETOWN = Column(String)
    POSITIONS = Column(String)
    WEIGHT = Column(String)