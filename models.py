from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from codebase.settings import DATABASE_LOCATION, DATABASE_TYPE

if DATABASE_TYPE == 'sqlite':
    DATABASE_LOCATION = f"/{DATABASE_LOCATION}"
connection_string = f"{DATABASE_TYPE}://{DATABASE_LOCATION}"
engine = create_engine(connection_string)

Base = declarative_base()

class PlayerMatchStats(Base):
    __tablename__ = "player_match_stats"
    stat_id = Column(Integer, primary_key=True)
    player_id = Column(Integer)
    player_object_id = Column(Integer)
    match_id = Column(Integer, ForeignKey("matches.match_id"))
    inning = Column(Integer)
    bat_runs = Column(Integer)
    balls_faced = Column(Integer)
    bat_fours = Column(Integer)
    bat_sixes = Column(Integer)
    bat_dot_balls = Column(Integer)
    not_out = Column(Boolean)
    how_out = Column(String(50))
    bowl_overs = Column(String)
    bowl_runs = Column(Integer)
    bowl_dot_balls = Column(Integer)
    bowl_wides = Column(Integer)
    bowl_noballs = Column(Integer)
    wickets = Column(Integer)
    team = Column(Integer)

class Match(Base):
    __tablename__ = "matches"
    match_id = Column(Integer, primary_key=True)
    match_title = Column(String(500))
    date = Column(DateTime)
    team_1 = Column(Integer)
    team_1_players = Column(Text)
    team_2_players = Column(Text)
    team_2 = Column(Integer)
    ground = Column(Integer)
    continent = Column(String(50))
    match_url = Column(String(300))
    result = Column(Text)
    total_innings = Column(Integer)
    toss = Column(Integer)
    match_winner = Column(Integer)
    status = Column(String(100))

Base.metadata.create_all(engine)
    


