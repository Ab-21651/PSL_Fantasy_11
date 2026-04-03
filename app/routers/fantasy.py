from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from pydantic import BaseModel
from typing import List
from app.db import get_db
from app.models import FantasyTeam, FantasyTeamPlayer, User, Player
from app.routers.auth import get_current_user
import uuid

router = APIRouter()

BUDGET         = 100.0   # total credits per user per match
MAX_FROM_TEAM  = 9       # max players from one team
MIN_PLAYERS    = 11      # must pick exactly 11


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class MatchdayTeamRequest(BaseModel):
    match_id:        str
    team_name:       str
    player_ids:      List[str]   # exactly 11
    captain_id:      str
    vice_captain_id: str


class SeasonTeamRequest(BaseModel):
    team_name:       str
    player_ids:      List[str]
    captain_id:      str
    vice_captain_id: str


# ── Helpers ───────────────────────────────────────────────────────────────────
async def validate_players(player_ids: List[str], db: AsyncSession) -> List[Player]:
    """Fetch all players and validate they exist."""
    result = await db.execute(
        select(Player).where(Player.player_id.in_(player_ids))
    )
    players = result.scalars().all()
    if len(players) != len(player_ids):
        found_ids = {p.player_id for p in players}
        missing = [pid for pid in player_ids if pid not in found_ids]
        raise HTTPException(status_code=404, detail=f"Players not found: {missing}")
    return players


async def validate_matchday_rules(
    player_ids: List[str],
    captain_id: str,
    vice_captain_id: str,
    match_id: str,
    players: List[Player],
    db: AsyncSession
):
    """Enforce all matchday fantasy rules."""

    # Rule 1 — exactly 11 players
    if len(player_ids) != MIN_PLAYERS:
        raise HTTPException(status_code=400, detail=f"You must select exactly {MIN_PLAYERS} players.")

    # Rule 2 — no duplicate player_ids
    if len(set(player_ids)) != len(player_ids):
        raise HTTPException(status_code=400, detail="Duplicate players in your team.")

    # Rule 3 — captain and vice captain must be in team
    if captain_id not in player_ids:
        raise HTTPException(status_code=400, detail="Captain must be in your selected team.")
    if vice_captain_id not in player_ids:
        raise HTTPException(status_code=400, detail="Vice captain must be in your selected team.")
    if captain_id == vice_captain_id:
        raise HTTPException(status_code=400, detail="Captain and vice captain must be different players.")

    # Rule 4 — fetch match to get playing teams
    match_result = await db.execute(
        text("SELECT team_home, team_away FROM matches WHERE match_id = :mid"),
        {"mid": match_id}
    )
    match = match_result.fetchone()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found.")

    team_home, team_away = match[0], match[1]
    
    # Rule 5 — all players must be from the two playing teams (fuzzy match)
    def team_matches(player_team, match_team):
        """Check if player team matches match team (handles variations)"""
        p_lower = player_team.lower().strip()
        m_lower = match_team.lower().strip()
        
        # Exact match
        if p_lower == m_lower:
            return True
        
        # Partial match (handles "Rawalpindi PindiZ" vs "Rawalpindiz")
        if p_lower in m_lower or m_lower in p_lower:
            return True
        
        # Key word matching
        p_words = set(p_lower.split())
        m_words = set(m_lower.split())
        
        # If they share significant words (not common words like "fc", "cc")
        common_words = p_words & m_words
        significant_common = {w for w in common_words if len(w) > 3}
        
        return len(significant_common) > 0
    
    invalid_players = []
    for p in players:
        home_match = team_matches(p.team, team_home)
        away_match = team_matches(p.team, team_away)
        
        if not home_match and not away_match:
            invalid_players.append(f"{p.player_name} (team: {p.team})")
    
    if invalid_players:
        raise HTTPException(
            status_code=400,
            detail=f"These players are not in today's match: {invalid_players}. Match teams are '{team_home}' vs '{team_away}'. Check player teams in database."
        )

    # Rule 6 — max 9 from one team
    team_counts = {}
    for p in players:
        team_counts[p.team] = team_counts.get(p.team, 0) + 1
    for team, count in team_counts.items():
        if count > MAX_FROM_TEAM:
            raise HTTPException(
                status_code=400,
                detail=f"Max {MAX_FROM_TEAM} players from one team. You have {count} from {team}."
            )

    # Rule 7 — budget check (sum of credits <= 100)
    total_credits = sum(float(p.credits or 8.0) for p in players)
    if total_credits > BUDGET:
        raise HTTPException(
            status_code=400,
            detail=f"Budget exceeded. Your team costs {total_credits:.1f} credits. Max allowed: {BUDGET}."
        )

    return total_credits, team_home, team_away


# ── Matchday endpoints ────────────────────────────────────────────────────────

@router.post("/matchday/team")
async def create_matchday_team(
    req: MatchdayTeamRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a fantasy team for a specific match. Requires authentication."""

    # Validate match exists and is upcoming
    match_result = await db.execute(
        text("SELECT match_id, status, team_home, team_away FROM matches WHERE match_id = :mid"),
        {"mid": req.match_id}
    )
    match = match_result.fetchone()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found.")
    if match[1] == "completed":
        raise HTTPException(status_code=400, detail="This match is already completed. You cannot create a team for it.")

    # Check user hasn't already made a team for this match
    user_id_str = str(current_user.user_id)
    existing = await db.execute(
        text("SELECT id FROM matchday_teams WHERE user_id = :uid AND match_id = :mid"),
        {"uid": user_id_str, "mid": req.match_id}
    )
    if existing.fetchone():
        raise HTTPException(status_code=400, detail="You already have a team for this match. Use PUT to update it.")

    # Fetch and validate players
    players = await validate_players(req.player_ids, db)
    total_credits, team_home, team_away = await validate_matchday_rules(
        req.player_ids, req.captain_id, req.vice_captain_id, req.match_id, players, db
    )

    # Create matchday team
    team_id = str(uuid.uuid4())
    await db.execute(
        text("""
            INSERT INTO matchday_teams (id, user_id, match_id, team_name, credits_used)
            VALUES (:tid, :uid, :mid, :name, :credits)
        """),
        {"tid": team_id, "uid": user_id_str, "mid": req.match_id,
         "name": req.team_name, "credits": total_credits}
    )

    # Add players
    for pid in req.player_ids:
        await db.execute(
            text("""
                INSERT INTO matchday_team_players (matchday_team_id, player_id, is_captain, is_vice_captain)
                VALUES (:tid, :pid, :cap, :vc)
            """),
            {
                "tid": team_id, "pid": pid,
                "cap": pid == req.captain_id,
                "vc":  pid == req.vice_captain_id,
            }
        )

    await db.commit()

    return {
        "message":      "Matchday team created successfully!",
        "team_id":      team_id,
        "match":        f"{team_home} vs {team_away}",
        "credits_used": total_credits,
        "budget_left":  round(BUDGET - total_credits, 1),
        "captain":      next(p.player_name for p in players if p.player_id == req.captain_id),
        "vice_captain": next(p.player_name for p in players if p.player_id == req.vice_captain_id),
    }


@router.get("/matchday/team/{match_id}")
async def get_matchday_team(
    match_id: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's team for a specific match. Requires authentication."""
    user_id = str(current_user.user_id)
    result = await db.execute(
        text("SELECT id, team_name, credits_used, total_points FROM matchday_teams WHERE user_id = :uid AND match_id = :mid"),
        {"uid": user_id, "mid": match_id}
    )
    team = result.fetchone()
    if not team:
        raise HTTPException(status_code=404, detail="No team found for this match.")

    team_id, team_name, credits_used, total_points = team

    # Get players
    players_result = await db.execute(
        text("""
            SELECT p.player_id, p.player_name, p.team, p.role, p.credits,
                   mtp.is_captain, mtp.is_vice_captain, mtp.points_earned
            FROM matchday_team_players mtp
            JOIN players p ON mtp.player_id = p.player_id
            WHERE mtp.matchday_team_id = :tid
            ORDER BY p.role
        """),
        {"tid": str(team_id)}
    )
    players = players_result.fetchall()

    return {
        "team_id":      str(team_id),
        "team_name":    team_name,
        "credits_used": float(credits_used),
        "total_points": float(total_points),
        "players": [
            {
                "player_id":      p[0],
                "player_name":    p[1],
                "team":           p[2],
                "role":           p[3],
                "credits":        float(p[4]) if p[4] else 8.0,
                "is_captain":     p[5],
                "is_vice_captain":p[6],
                "points_earned":  float(p[7]),
            }
            for p in players
        ]
    }


@router.get("/my-teams")
async def get_my_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all teams created by current user."""
    user_id = str(current_user.user_id)
    
    result = await db.execute(
        text("""
            SELECT mt.id, mt.match_id, mt.team_name, mt.credits_used, mt.total_points,
                   m.team_home, m.team_away, m.match_date, m.status
            FROM matchday_teams mt
            JOIN matches m ON mt.match_id = m.match_id
            WHERE mt.user_id = :uid
            ORDER BY m.match_date DESC
        """),
        {"uid": user_id}
    )
    
    teams = result.fetchall()
    
    return [
        {
            "team_id": str(t[0]),
            "match_id": str(t[1]),
            "team_name": t[2],
            "credits_used": float(t[3]),
            "total_points": float(t[4]) if t[4] else 0.0,
            "team_home": t[5],
            "team_away": t[6],
            "match_date": str(t[7]),
            "status": t[8]
        }
        for t in teams
    ]


@router.get("/matchday/leaderboard/{match_id}")
async def matchday_leaderboard(match_id: str, db: AsyncSession = Depends(get_db)):
    """Leaderboard for a specific match."""
    result = await db.execute(
        text("""
            SELECT u.username, mt.team_name, mt.total_points, mt.credits_used
            FROM matchday_teams mt
            JOIN users u ON mt.user_id = u.user_id
            WHERE mt.match_id = :mid
            ORDER BY mt.total_points DESC
            LIMIT 50
        """),
        {"mid": match_id}
    )
    rows = result.fetchall()
    return [
        {
            "rank":         i + 1,
            "username":     r[0],
            "team_name":    r[1],
            "total_points": float(r[2]),
            "credits_used": float(r[3]),
        }
        for i, r in enumerate(rows)
    ]


# ── Season team endpoints (kept from before) ──────────────────────────────────

@router.post("/season/team")
async def create_season_team(
    req: SeasonTeamRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a season-long fantasy team. Requires authentication."""
    if len(req.player_ids) != MIN_PLAYERS:
        raise HTTPException(status_code=400, detail="Select exactly 11 players.")

    players = await validate_players(req.player_ids, db)
    total_credits = sum(float(p.credits or 8.0) for p in players)

    if total_credits > BUDGET:
        raise HTTPException(status_code=400, detail=f"Budget exceeded: {total_credits:.1f}/{BUDGET} credits.")
    if req.captain_id not in req.player_ids:
        raise HTTPException(status_code=400, detail="Captain must be in your team.")
    if req.vice_captain_id not in req.player_ids:
        raise HTTPException(status_code=400, detail="Vice captain must be in your team.")

    team = FantasyTeam(
        team_id=uuid.uuid4(), user_id=current_user.user_id,
        team_name=req.team_name, season="2026"
    )
    db.add(team)
    await db.flush()

    for pid in req.player_ids:
        db.add(FantasyTeamPlayer(
            team_id=team.team_id, player_id=pid,
            is_captain=(pid == req.captain_id),
            is_vice_captain=(pid == req.vice_captain_id),
        ))

    await db.commit()
    return {
        "message":      "Season team created!",
        "team_id":      str(team.team_id),
        "credits_used": total_credits,
        "budget_left":  round(BUDGET - total_credits, 1),
    }


@router.get("/season/leaderboard")
async def season_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            SELECT u.username, ft.team_name, ft.total_points
            FROM fantasy_teams ft
            JOIN users u ON ft.user_id = u.user_id
            WHERE ft.season = '2026'
            ORDER BY ft.total_points DESC
            LIMIT 50
        """)
    )
    rows = result.fetchall()
    return [
        {"rank": i+1, "username": r[0], "team_name": r[1], "total_points": float(r[2])}
        for i, r in enumerate(rows)
    ]