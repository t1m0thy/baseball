 # teams table with leagues, teams, and season IDs, year, division

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TeamInfo(Base):
    __tablename__ = 'teams'

    ID = Column(Integer, primary_key=True)
    FULL_NAME = Column(String(255))
    TEAM_ID = Column(String(255))
    LEAGUE_ID = Column(String(255))
    SEASON_ID = Column(String(255))
    year = Column(Integer)
    division = Column(String(255))