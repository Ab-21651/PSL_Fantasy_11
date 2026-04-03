from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db import get_db
from app.models import Player, CareerStat, RecentForm
import math

router = APIRouter()

def safe_float(value):
    """Convert to float, return None if NaN or Infinity"""
    if value is None:
        return None
    try:
        f = float(value)
        # Check if it's NaN or Infinity
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (ValueError, TypeError):
        return None

# GET /players — list all players, optional filters
@router.get("/")
async def get_players(
    team: str = Query(None, description="Filter by team name"),
    role: str = Query(None, description="Filter by role"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Player)
    if team:
        query = query.where(Player.team.ilike(f"%{team}%"))
    if role:
        query = query.where(Player.role.ilike(f"%{role}%"))
    result = await db.execute(query)
    players = result.scalars().all()
    return [
        {
            "player_id":   p.player_id,
            "player_name": p.player_name,
            "team":        p.team,
            "role":        p.role,
            "nationality": p.nationality,
            "age":         p.age,
            "credits":     p.credits,
        }
        for p in players
    ]

# GET /players/{player_id} — single player profile
@router.get("/{player_id}")
async def get_player(player_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Player).where(Player.player_id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return {
        "player_id":   player.player_id,
        "player_name": player.player_name,
        "team":        player.team,
        "role":        player.role,
        "nationality": player.nationality,
        "age":         player.age,
        "credits":     player.credits,
    }

# GET /players/{player_id}/stats — career stats across seasons
@router.get("/{player_id}/stats")
async def get_player_stats(player_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CareerStat)
        .where(CareerStat.player_id == player_id)
        .order_by(CareerStat.season)
    )
    stats = result.scalars().all()
    return [
        {
            "season":          s.season,
            "matches":         s.matches,
            "runs":            s.runs,
            "average":         safe_float(s.average),
            "strike_rate":     safe_float(s.strike_rate),
            "wickets":         s.wickets,
            "economy":         safe_float(s.economy),
            "bowling_average": safe_float(s.bowling_average),
            "catches":         s.catches,
        }
        for s in stats
    ]

# GET /players/{player_id}/form — last 5 matches (NO POINTS SHOWN)
@router.get("/{player_id}/form")
async def get_player_form(player_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get player's recent form for team selection.
    Points are NOT included - users should select based on performance, not points!
    """
    result = await db.execute(
        select(RecentForm)
        .where(RecentForm.player_id == player_id)
        .order_by(RecentForm.match_date.desc())
        .limit(5)
    )
    form = result.scalars().all()
    return [
        {
            "match_date":     str(f.match_date),
            "opponent":       f.opponent,
            "runs_scored":    f.runs_scored,
            "balls_faced":    f.balls_faced,
            "fours":          f.fours,
            "sixes":          f.sixes,
            "wickets_taken":  f.wickets_taken,
            "overs_bowled":   safe_float(f.overs_bowled),
            "runs_given":     f.runs_given,
            "catches":        f.catches,
            "venue":          f.venue,
            "season":         f.season,
            # "points_earned": f.points_earned,  # ❌ REMOVED - only shown on leaderboard after match
        }
        for f in form
    ]
