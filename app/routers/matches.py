from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db import get_db
from datetime import date

router = APIRouter()


@router.get("/today")
async def get_today_matches(db: AsyncSession = Depends(get_db)):
    """Get all matches scheduled for today."""
    result = await db.execute(
        text("""
            SELECT match_id, match_number, match_date, match_time,
                   team_home, team_away, venue, leg, status
            FROM matches
            WHERE match_date = CURRENT_DATE
            ORDER BY match_time
        """)
    )
    rows = result.fetchall()
    return [
        {
            "match_id":     str(r[0]),
            "match_number": r[1],
            "match_date":   str(r[2]),
            "match_time":   r[3],
            "team_home":    r[4],
            "team_away":    r[5],
            "venue":        r[6],
            "leg":          r[7],
            "status":       r[8],
        }
        for r in rows
    ]


@router.get("/upcoming")
async def get_upcoming_matches(db: AsyncSession = Depends(get_db)):
    """
    Get next 5 upcoming matches.
    Auto-marks past matches as completed if they don't have a winner yet.
    """
    # First, auto-complete any past matches that are still marked 'upcoming'
    # A match is considered past if it's yesterday or earlier
    await db.execute(
        text("""
            UPDATE matches 
            SET status = 'completed'
            WHERE match_date < CURRENT_DATE 
              AND status = 'upcoming'
        """)
    )
    await db.commit()
    
    # Now get upcoming matches (today or future)
    result = await db.execute(
        text("""
            SELECT match_id, match_number, match_date, match_time,
                   team_home, team_away, venue, leg, status
            FROM matches
            WHERE match_date >= CURRENT_DATE AND status = 'upcoming'
            ORDER BY match_date, match_time
            LIMIT 5
        """)
    )
    rows = result.fetchall()
    return [
        {
            "match_id":     str(r[0]),
            "match_number": r[1],
            "match_date":   str(r[2]),
            "match_time":   r[3],
            "team_home":    r[4],
            "team_away":    r[5],
            "venue":        r[6],
            "leg":          r[7],
            "status":       r[8],
        }
        for r in rows
    ]


@router.get("/all")
async def get_all_matches(db: AsyncSession = Depends(get_db)):
    """
    Get full PSL 2026 schedule.
    Auto-marks past matches as completed if they don't have a winner yet.
    """
    # Auto-complete past matches
    await db.execute(
        text("""
            UPDATE matches 
            SET status = 'completed'
            WHERE match_date < CURRENT_DATE 
              AND status = 'upcoming'
        """)
    )
    await db.commit()
    
    result = await db.execute(
        text("""
            SELECT match_id, match_number, match_date, match_time,
                   team_home, team_away, venue, leg, status, winner
            FROM matches
            ORDER BY match_number
        """)
    )
    rows = result.fetchall()
    return [
        {
            "match_id":     str(r[0]),
            "match_number": r[1],
            "match_date":   str(r[2]),
            "match_time":   r[3],
            "team_home":    r[4],
            "team_away":    r[5],
            "venue":        r[6],
            "leg":          r[7],
            "status":       r[8],
            "winner":       r[9],
        }
        for r in rows
    ]


@router.get("/{match_id}")
async def get_match(match_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single match with playing squads."""
    result = await db.execute(
        text("""
            SELECT match_id, match_number, match_date, match_time,
                   team_home, team_away, venue, leg, status, winner
            FROM matches WHERE match_id = :mid
        """),
        {"mid": match_id}
    )
    match = result.fetchone()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found.")

    # Normalize team names for matching
    def normalize_team(team_name):
        """Handle team name variations"""
        team_lower = team_name.lower().strip()
        
        # Map variations to consistent names
        if 'rawal' in team_lower or 'pindi' in team_lower:
            return 'Rawalpindi%'  # Matches both "Rawalpindi PindiZ" and "Rawalpindiz"
        elif 'multan' in team_lower:
            return 'Multan%'  # Matches both "Multan Sultan" and "Multan Sultans"
        elif 'peshawar' in team_lower or 'zalmi' in team_lower:
            return 'Peshawar%'
        elif 'lahore' in team_lower or 'qalandar' in team_lower:
            return 'Lahore%'
        elif 'karachi' in team_lower:
            return 'Karachi%'
        elif 'quetta' in team_lower:
            return 'Quetta%'
        elif 'islamabad' in team_lower:
            return 'Islamabad%'
        elif 'hyderabad' in team_lower:
            return 'Hyderabad%'
        else:
            return f'%{team_name}%'
    
    home_pattern = normalize_team(match[4])
    away_pattern = normalize_team(match[5])
    
    # Get players from both teams
    home_result = await db.execute(
        text("SELECT player_id, player_name, role, credits FROM players WHERE team ILIKE :t ORDER BY role"),
        {"t": home_pattern}
    )
    away_result = await db.execute(
        text("SELECT player_id, player_name, role, credits FROM players WHERE team ILIKE :t ORDER BY role"),
        {"t": away_pattern}
    )
    
    home_players = home_result.fetchall()
    away_players = away_result.fetchall()

    return {
        "match_id":     str(match[0]),
        "match_number": match[1],
        "match_date":   str(match[2]),
        "match_time":   match[3],
        "team_home":    match[4],
        "team_away":    match[5],
        "venue":        match[6],
        "leg":          match[7],
        "status":       match[8],
        "winner":       match[9],
        "budget":       100.0,
        "max_per_team": 9,
        "squads": {
            match[4]: [
                {"player_id": r[0], "player_name": r[1], "role": r[2], "credits": float(r[3] or 8.0)}
                for r in home_players
            ],
            match[5]: [
                {"player_id": r[0], "player_name": r[1], "role": r[2], "credits": float(r[3] or 8.0)}
                for r in away_players
            ],
        }
    }


@router.patch("/{match_id}/status")
async def update_match_status(match_id: str, status: str, winner: str = None, db: AsyncSession = Depends(get_db)):
    """Update match status (upcoming/live/completed) and winner."""
    if status not in ["upcoming", "live", "completed"]:
        raise HTTPException(status_code=400, detail="Status must be upcoming, live, or completed.")

    await db.execute(
        text("UPDATE matches SET status = :s, winner = :w WHERE match_id = :mid"),
        {"s": status, "w": winner, "mid": match_id}
    )
    await db.commit()
    return {"message": f"Match status updated to {status}"}


@router.post("/auto-complete")
async def auto_complete_past_matches(db: AsyncSession = Depends(get_db)):
    """
    Manually trigger auto-completion of past matches.
    Marks all matches before today as 'completed' if still 'upcoming'.
    """
    result = await db.execute(
        text("""
            UPDATE matches 
            SET status = 'completed'
            WHERE match_date < CURRENT_DATE 
              AND status = 'upcoming'
            RETURNING match_id, match_number, match_date, team_home, team_away
        """)
    )
    updated = result.fetchall()
    await db.commit()
    
    return {
        "message": f"Auto-completed {len(updated)} past matches",
        "updated_matches": [
            {
                "match_id": str(r[0]),
                "match_number": r[1],
                "match_date": str(r[2]),
                "teams": f"{r[3]} vs {r[4]}"
            }
            for r in updated
        ]
    }
