"""
CricMind — Match Results Router
POST /results/{match_id} — push scorecard, auto-updates everything
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from app.db import get_db

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────
class PlayerResult(BaseModel):
    player_name:  str
    runs_scored:  int = 0
    balls_faced:  int = 0
    fours:        int = 0
    sixes:        int = 0
    dismissed:    bool = False
    wickets_taken:int = 0
    overs_bowled: float = 0.0
    runs_given:   int = 0
    maidens:      int = 0
    catches:      int = 0
    stumpings:    int = 0
    run_outs:     int = 0


class MatchResultRequest(BaseModel):
    winner:       str
    venue:        Optional[str] = None
    players:      List[PlayerResult]


# ── Points calculator ─────────────────────────────────────────────────────────
def calculate_fantasy_points(p: PlayerResult, role: str) -> tuple[float, str]:
    pts = 0.0
    log = []

    # Batting
    if p.runs_scored:
        pts += p.runs_scored
        log.append(f"{p.runs_scored} runs")
    if p.fours:
        pts += p.fours
        log.append(f"{p.fours} fours")
    if p.sixes:
        pts += p.sixes * 2
        log.append(f"{p.sixes} sixes")
    if p.runs_scored >= 100:
        pts += 25
        log.append("century bonus")
    elif p.runs_scored >= 50:
        pts += 10
        log.append("fifty bonus")
    if p.runs_scored == 0 and p.dismissed and role in ["Batsman", "Wicket-Keeper"]:
        pts -= 5
        log.append("duck")

    # Bowling
    if p.wickets_taken:
        pts += p.wickets_taken * 25
        log.append(f"{p.wickets_taken} wickets")
    if p.maidens:
        pts += p.maidens * 12
        log.append(f"{p.maidens} maidens")
    if p.overs_bowled >= 2 and p.runs_given > 0:
        economy = p.runs_given / p.overs_bowled
        if economy < 6:
            pts += 6
            log.append("economy bonus")
        elif economy > 10:
            pts -= 6
            log.append("economy penalty")

    # Fielding
    if p.catches:
        pts += p.catches * 10
        log.append(f"{p.catches} catches")
    if p.stumpings:
        pts += p.stumpings * 15
        log.append(f"{p.stumpings} stumpings")
    if p.run_outs:
        pts += p.run_outs * 10
        log.append(f"{p.run_outs} run outs")

    reason = ", ".join(log) if log else "no contribution"
    return round(pts, 1), reason


# ── Main endpoint ─────────────────────────────────────────────────────────────
@router.post("/{match_id}")
async def submit_match_results(
    match_id: str,
    req: MatchResultRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Push match scorecard. Automatically:
    - Inserts recent_form rows (opponent auto-filled from matches table)
    - Updates career_stats 2026 totals
    - Calculates fantasy points for all matchday teams
    - Updates matchday leaderboard
    - Marks match as completed
    """

    # Step 1 — fetch match info (we need team_home, team_away, venue)
    match_result = await db.execute(
        text("SELECT match_id, team_home, team_away, venue, status FROM matches WHERE match_id = :mid"),
        {"mid": match_id}
    )
    match = match_result.fetchone()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found.")
    if match[4] == "completed":
        raise HTTPException(status_code=400, detail="Match already marked completed. Results already submitted.")

    team_home = match[1]
    team_away = match[2]
    venue     = req.venue or match[3] or "Unknown"
    match_date = (await db.execute(
        text("SELECT match_date FROM matches WHERE match_id = :mid"), {"mid": match_id}
    )).fetchone()[0]

    processed  = []
    not_found  = []

    for player_result in req.players:
        # Step 2 — find player in DB by name
        name = player_result.player_name.strip()
        player_row = await db.execute(
            text("""
                SELECT player_id, player_name, team, role
                FROM players
                WHERE LOWER(player_name) = LOWER(:name)
                   OR LOWER(player_name) LIKE LOWER(:partial)
                LIMIT 1
            """),
            {"name": name, "partial": f"%{name.split()[-1]}%"}
        )
        player = player_row.fetchone()

        if not player:
            not_found.append(name)
            continue

        player_id   = player[0]
        player_name = player[1]
        player_team = player[2]
        player_role = player[3]

        # Step 3 — determine opponent
        # If player is in team_home, opponent is team_away and vice versa
        if player_team.lower() == team_home.lower():
            opponent = team_away
        elif player_team.lower() == team_away.lower():
            opponent = team_home
        else:
            # Player may have moved teams — use whichever team name partially matches
            opponent = team_away if team_home.lower() in player_team.lower() else team_home

        # Step 4 — calculate fantasy points
        pts, reason = calculate_fantasy_points(player_result, player_role)

        # Step 5 — insert recent_form row
        await db.execute(text("""
            INSERT INTO recent_form
                (player_id, player_name, match_date, opponent,
                 runs_scored, wickets_taken, points_earned, venue, season)
            VALUES (:pid, :name, :date, :opp, :runs, :wkts, :pts, :venue, '2026')
        """), {
            "pid":   player_id,
            "name":  player_name,
            "date":  match_date,
            "opp":   opponent,
            "runs":  player_result.runs_scored,
            "wkts":  player_result.wickets_taken,
            "pts":   int(pts),
            "venue": venue,
        })

        # Step 6 — update career_stats 2026
        existing = await db.execute(
            text("SELECT id, runs, wickets, matches, catches FROM career_stats WHERE player_id = :pid AND season = '2026'"),
            {"pid": player_id}
        )
        stat_row = existing.fetchone()

        if stat_row:
            new_runs    = (stat_row[1] or 0) + player_result.runs_scored
            new_wkts    = (stat_row[2] or 0) + player_result.wickets_taken
            new_matches = (stat_row[3] or 0) + 1
            new_catches = (stat_row[4] or 0) + player_result.catches

            # Recalculate average and strike rate
            new_avg = round(new_runs / new_matches, 2) if new_matches else 0
            new_sr  = round((player_result.runs_scored / player_result.balls_faced * 100), 2) if player_result.balls_faced else None
            new_eco = round(player_result.runs_given / player_result.overs_bowled, 2) if player_result.overs_bowled >= 1 else None

            await db.execute(text("""
                UPDATE career_stats SET
                    runs    = :runs,
                    wickets = :wkts,
                    matches = :matches,
                    catches = :catches,
                    average = :avg
                WHERE player_id = :pid AND season = '2026'
            """), {
                "runs": new_runs, "wkts": new_wkts,
                "matches": new_matches, "catches": new_catches,
                "avg": new_avg, "pid": player_id
            })
        else:
            # First match of season for this player — create row
            await db.execute(text("""
                INSERT INTO career_stats
                    (player_id, player_name, season, matches, runs, wickets, catches)
                VALUES (:pid, :name, '2026', 1, :runs, :wkts, :catches)
            """), {
                "pid": player_id, "name": player_name,
                "runs": player_result.runs_scored,
                "wkts": player_result.wickets_taken,
                "catches": player_result.catches,
            })

        # Step 7 — update fantasy points for all matchday teams with this player
        matchday_teams = await db.execute(text("""
            SELECT mt.id, mtp.is_captain, mtp.is_vice_captain
            FROM matchday_teams mt
            JOIN matchday_team_players mtp ON mt.id = mtp.matchday_team_id
            WHERE mt.match_id = :mid AND mtp.player_id = :pid
        """), {"mid": match_id, "pid": player_id})

        for team_row in matchday_teams.fetchall():
            team_id    = team_row[0]
            is_captain = team_row[1]
            is_vc      = team_row[2]

            # Apply multipliers
            final_pts = pts * 2.0 if is_captain else (pts * 1.5 if is_vc else pts)
            final_pts = round(final_pts, 1)

            # Update player points
            await db.execute(text("""
                UPDATE matchday_team_players
                SET points_earned = :pts
                WHERE matchday_team_id = :tid AND player_id = :pid
            """), {"pts": final_pts, "tid": str(team_id), "pid": player_id})

            # Log it
            await db.execute(text("""
                INSERT INTO points_log (team_id, player_id, match_date, points, reason)
                VALUES (:tid, :pid, :date, :pts, :reason)
                ON CONFLICT DO NOTHING
            """), {
                "tid": str(team_id), "pid": player_id,
                "date": match_date, "pts": final_pts,
                "reason": reason + (" (C 2x)" if is_captain else " (VC 1.5x)" if is_vc else "")
            })

        processed.append({"player": player_name, "points": pts, "reason": reason})

    # Step 8 — recalculate all team totals for this match
    await db.execute(text("""
        UPDATE matchday_teams mt
        SET total_points = (
            SELECT COALESCE(SUM(mtp.points_earned), 0)
            FROM matchday_team_players mtp
            WHERE mtp.matchday_team_id = mt.id
        )
        WHERE mt.match_id = :mid
    """), {"mid": match_id})

    # Step 9 — mark match as completed
    await db.execute(text("""
        UPDATE matches SET status = 'completed', winner = :winner
        WHERE match_id = :mid
    """), {"winner": req.winner, "mid": match_id})

    await db.commit()

    return {
        "message":       "Match results processed successfully!",
        "match":         f"{team_home} vs {team_away}",
        "winner":        req.winner,
        "players_updated": len(processed),
        "players_not_found": not_found,
        "results":       processed,
    }
