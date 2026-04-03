from sqlalchemy import Column, String, Integer, Numeric, Boolean, Date, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    player_id    = Column(String, primary_key=True)
    player_name  = Column(String, nullable=False)
    team         = Column(String)
    role         = Column(String)
    nationality  = Column(String)
    age          = Column(Integer)
    credits      = Column(Integer, default=8)

class CareerStat(Base):
    __tablename__ = "career_stats"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    player_id       = Column(String, ForeignKey("players.player_id"))
    player_name     = Column(String)
    season          = Column(String)
    matches         = Column(Integer, default=0)
    runs            = Column(Integer, default=0)
    average         = Column(Numeric(6,2))
    strike_rate     = Column(Numeric(6,2))
    wickets         = Column(Integer, default=0)
    economy         = Column(Numeric(5,2))
    bowling_average = Column(Numeric(6,2))
    catches         = Column(Integer, default=0)

class RecentForm(Base):
    __tablename__ = "recent_form"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    player_id      = Column(String, ForeignKey("players.player_id"))
    player_name    = Column(String)
    match_date     = Column(Date)
    opponent       = Column(String)
    runs_scored    = Column(Integer, default=0)
    balls_faced    = Column(Integer, default=0)
    fours          = Column(Integer, default=0)
    sixes          = Column(Integer, default=0)
    wickets_taken  = Column(Integer, default=0)
    overs_bowled   = Column(Float, default=0.0)
    runs_given     = Column(Integer, default=0)
    maidens        = Column(Integer, default=0)
    catches        = Column(Integer, default=0)
    stumpings      = Column(Integer, default=0)
    run_outs       = Column(Integer, default=0)
    points_earned  = Column(Integer, default=0)
    venue          = Column(String)
    season         = Column(String)

class User(Base):
    __tablename__ = "users"
    user_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username      = Column(String, unique=True, nullable=False)
    email         = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at    = Column(DateTime, server_default=func.now())
    is_active     = Column(Boolean, default=True)

class FantasyTeam(Base):
    __tablename__ = "fantasy_teams"
    team_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    team_name    = Column(String)
    season       = Column(String, default="2026")
    total_points = Column(Integer, default=0)
    created_at   = Column(DateTime, server_default=func.now())

class FantasyTeamPlayer(Base):
    __tablename__ = "fantasy_team_players"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    team_id         = Column(UUID(as_uuid=True), ForeignKey("fantasy_teams.team_id"))
    player_id       = Column(String, ForeignKey("players.player_id"))
    is_captain      = Column(Boolean, default=False)
    is_vice_captain = Column(Boolean, default=False)
    points_earned   = Column(Integer, default=0)
