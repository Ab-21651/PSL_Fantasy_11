from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text
from pydantic import BaseModel
from app.db import get_db
from app.models import Player, CareerStat, RecentForm, User
from app.routers.auth import get_current_user
import os, httpx, json, re
from datetime import date

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.1-8b-instant"

class AIRequest(BaseModel):
    question: str


# ── Groq caller ───────────────────────────────────────────────────────────────
async def ask_groq(system_prompt: str, user_question: str, max_tokens: int = 400) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in .env")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_question},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            }
        )
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Groq error: {r.text}")
        return r.json()["choices"][0]["message"]["content"].strip()


# ── Intent detection ──────────────────────────────────────────────────────────
async def detect_intent(question: str) -> dict:
    prompt = """Analyze this cricket question and return ONLY a JSON object:
{
  "type": "player_lookup" | "top_performers" | "comparison" | "team_history" | "general",
  "player_names": [list of player names mentioned, empty if none],
  "team_name": "team name if mentioned" | null,
  "stat": "runs" | "wickets" | "economy" | "strike_rate" | "average" | "points" | null,
  "role": "Batsman" | "Bowler" | "All-rounder" | null,
  "season": "2026" | "2025" | "2023/24" | null
}

Type rules:
- "player_lookup": question is about a specific player
- "top_performers": looking for best/top players by a stat or role
- "comparison": comparing two or more players
- "team_history": asking about a team's best players across seasons (even if those players have since moved teams)
- "general": anything else

Examples:
"Is Babar good?" → {"type":"player_lookup","player_names":["Babar Azam"],"team_name":null,"stat":null,"role":null,"season":null}
"Best bowler 2025 by wickets" → {"type":"top_performers","player_names":[],"team_name":null,"stat":"wickets","role":"Bowler","season":"2025"}
"Compare Shaheen vs Naseem" → {"type":"comparison","player_names":["Shaheen Shah Afridi","Naseem Shah"],"team_name":null,"stat":null,"role":null,"season":null}
"Who was best for Quetta last 2 seasons?" → {"type":"team_history","player_names":[],"team_name":"Quetta Gladiators","stat":null,"role":null,"season":null}
"Top batsmen this season" → {"type":"top_performers","player_names":[],"team_name":null,"stat":"runs","role":"Batsman","season":"2026"}

Return ONLY the JSON, nothing else."""

    raw = await ask_groq(prompt, question, max_tokens=150)
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group()) if match else {
            "type": "general", "player_names": [], "team_name": None,
            "stat": None, "role": None, "season": None
        }
    except Exception:
        return {"type": "general", "player_names": [], "team_name": None,
                "stat": None, "role": None, "season": None}


# ── DB context builders ───────────────────────────────────────────────────────
async def build_player_context(player: Player, db: AsyncSession) -> str:
    stats_r = await db.execute(
        select(CareerStat).where(CareerStat.player_id == player.player_id)
        .order_by(CareerStat.season.desc())
    )
    stats = stats_r.scalars().all()

    form_r = await db.execute(
        select(RecentForm).where(RecentForm.player_id == player.player_id)
        .order_by(RecentForm.match_date.desc()).limit(5)
    )
    form = form_r.scalars().all()

    ctx = f"PLAYER: {player.player_name}\nCURRENT TEAM (PSL 2026): {player.team}\nROLE: {player.role}\nAGE: {player.age}\n\nPSL CAREER STATS:\n"
    for s in stats:
        if player.role in ["Batsman", "Wicket-Keeper"]:
            ctx += f"  {s.season}: {s.matches} matches | {s.runs} runs | avg {s.average} | SR {s.strike_rate} | {s.catches} catches\n"
        elif player.role == "Bowler":
            ctx += f"  {s.season}: {s.matches} matches | {s.wickets} wickets | economy {s.economy} | bowl avg {s.bowling_average}\n"
        else:
            ctx += f"  {s.season}: {s.matches} matches | {s.runs} runs | avg {s.average} | {s.wickets} wickets | economy {s.economy}\n"

    if form:
        ctx += "\nRECENT FORM (last 5 PSL matches):\n"
        for f in form:
            ctx += f"  {f.match_date} vs {f.opponent}: {f.runs_scored} runs, {f.wickets_taken} wkts, {f.points_earned} pts\n"
    else:
        ctx += "\nRECENT FORM: No recent data available.\n"
    return ctx


async def build_top_performers_context(stat: str, role: str, season: str, db: AsyncSession) -> str:
    season = season or "2026"
    stat = stat or "runs"

    q = select(CareerStat, Player).join(Player, CareerStat.player_id == Player.player_id)
    q = q.where(CareerStat.season == season)

    if role:
        q = q.where(Player.role.ilike(f"%{role}%"))

    order_col = {
        "runs":        CareerStat.runs,
        "wickets":     CareerStat.wickets,
        "average":     CareerStat.average,
        "strike_rate": CareerStat.strike_rate,
        "points":      CareerStat.runs,
    }.get(stat, CareerStat.runs)

    if stat == "economy":
        q = q.where(CareerStat.economy.isnot(None)).where(CareerStat.matches >= 3).order_by(CareerStat.economy.asc())
    else:
        q = q.order_by(desc(order_col))

    result = await db.execute(q.limit(5))
    rows = result.all()

    if not rows:
        return f"No {role or 'player'} data found for PSL {season}."

    ctx = f"TOP {role.upper() if role else 'PLAYERS'} BY {stat.upper()} — PSL {season}:\n"
    for i, (s, p) in enumerate(rows, 1):
        if stat == "wickets":
            ctx += f"  {i}. {p.player_name} ({p.team}) — {s.wickets} wkts | economy {s.economy} | {s.matches} matches\n"
        elif stat == "economy":
            ctx += f"  {i}. {p.player_name} ({p.team}) — economy {s.economy} | {s.wickets} wkts | {s.matches} matches\n"
        else:
            ctx += f"  {i}. {p.player_name} ({p.team}) — {s.runs} runs | avg {s.average} | SR {s.strike_rate} | {s.matches} matches\n"
    return ctx


async def build_team_history_context(team_name: str, db: AsyncSession) -> str:
    """Fetch top performers who played FOR this team in past seasons.
    Note: player may have since moved to a different team in 2026."""

    # Find players whose career_stats are linked and who played for this team
    # We join on player_name match from career_stats since team isn't stored in career_stats
    # So we use players table team as approximation + all their stats
    result = await db.execute(
        select(CareerStat, Player)
        .join(Player, CareerStat.player_id == Player.player_id)
        .where(Player.team.ilike(f"%{team_name}%"))
        .where(CareerStat.season.in_(["2025", "2023/24"]))
        .order_by(desc(CareerStat.runs))
        .limit(10)
    )
    rows = result.all()

    if not rows:
        # Try fuzzy team name match
        team_keywords = team_name.lower().split()
        keyword = team_keywords[-1] if team_keywords else team_name
        result = await db.execute(
            select(CareerStat, Player)
            .join(Player, CareerStat.player_id == Player.player_id)
            .where(Player.team.ilike(f"%{keyword}%"))
            .where(CareerStat.season.in_(["2025", "2023/24"]))
            .order_by(desc(CareerStat.runs))
            .limit(10)
        )
        rows = result.all()

    if not rows:
        return f"No historical data found for {team_name}."

    ctx = f"HISTORICAL PERFORMERS FOR {team_name.upper()} (PSL 2023/24 and 2025):\n"
    ctx += "(Note: some players may have moved to different teams in PSL 2026)\n\n"

    for s, p in rows:
        ctx += f"  {p.player_name} — {s.season}: {s.runs} runs, {s.wickets} wkts"
        ctx += f", avg {s.average}, SR {s.strike_rate}" if s.runs else ""
        ctx += f" | Current 2026 team: {p.team}\n"
    return ctx


# ── Main endpoint ─────────────────────────────────────────────────────────────
@router.post("/ask")
async def ask_ai(
    req: AIRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ask AI about PSL players. Limited to 10 questions per day. Requires authentication."""
    question = req.question.strip()

    # Check daily usage limit
    user_id = str(current_user.user_id)
    today = date.today()
    
    usage_result = await db.execute(
        text("SELECT questions_asked FROM ai_usage WHERE user_id = :uid AND usage_date = :today"),
        {"uid": user_id, "today": today}
    )
    usage = usage_result.fetchone()
    
    if usage:
        questions_asked = usage[0]
        if questions_asked >= 10:
            raise HTTPException(
                status_code=429, 
                detail="Daily limit reached. You can ask 10 questions per day. Come back tomorrow!"
            )
        # Increment count
        await db.execute(
            text("UPDATE ai_usage SET questions_asked = questions_asked + 1 WHERE user_id = :uid AND usage_date = :today"),
            {"uid": user_id, "today": today}
        )
    else:
        # First question today
        await db.execute(
            text("INSERT INTO ai_usage (user_id, usage_date, questions_asked) VALUES (:uid, :today, 1)"),
            {"uid": user_id, "today": today}
        )
    
    await db.commit()

    # Step 1 — detect intent
    intent = await detect_intent(question)

    context = ""
    players_found = []

    # Step 2 — fetch relevant DB data based on intent
    if intent["type"] == "player_lookup" and intent.get("player_names"):
        for name in intent["player_names"][:2]:
            result = await db.execute(
                select(Player).where(Player.player_name.ilike(f"%{name}%")).limit(1)
            )
            p = result.scalar_one_or_none()
            if p:
                context += await build_player_context(p, db) + "\n"
                players_found.append(p.player_name)

    elif intent["type"] == "comparison" and intent.get("player_names"):
        for name in intent["player_names"][:2]:
            result = await db.execute(
                select(Player).where(Player.player_name.ilike(f"%{name}%")).limit(1)
            )
            p = result.scalar_one_or_none()
            if p:
                context += await build_player_context(p, db) + "\n---\n"
                players_found.append(p.player_name)

    elif intent["type"] == "top_performers":
        context = await build_top_performers_context(
            stat=intent.get("stat") or "runs",
            role=intent.get("role") or "",
            season=intent.get("season") or "2026",
            db=db
        )

    elif intent["type"] == "team_history" and intent.get("team_name"):
        context = await build_team_history_context(intent["team_name"], db)

    # Step 3 — build system prompt
    if context:
        system_prompt = f"""You are CricMind, an expert PSL fantasy cricket analyst.

STRICT RULES:
1. Base your answer ONLY on the data provided below. Never invent stats.
2. The "CURRENT TEAM (PSL 2026)" field shows where the player plays NOW — trust it completely.
3. A player may have played for a different team in past seasons — that is normal, teams change every year.
4. If PSL HISTORY says "NEW TO PSL" — clearly state the player has no PSL record and base advice on their international reputation only.
5. If stats exist, always mention specific numbers.
6. Keep answer to 4-5 sentences max.
7. For fantasy advice always end with: STRONG PICK, GOOD PICK, RISKY PICK, or AVOID.

DATA:
{context}"""
    else:
        system_prompt = """You are CricMind, an expert PSL 2026 fantasy cricket analyst.
You don't have specific data for this query in the database.
Be honest about what you don't know. Give general PSL cricket advice based on the question.
Keep answer to 3-4 sentences. End with a verdict if it's a fantasy question."""

    # Step 4 — get answer
    answer = await ask_groq(system_prompt, question)

    return {
        "question":        question,
        "intent":          intent["type"],
        "players_found":   players_found if players_found else None,
        "answer":          answer,
        "remaining_questions": 10 - (questions_asked + 1 if usage else 1),
    }


# ── Usage check endpoint ──────────────────────────────────────────────────────
@router.get("/usage")
async def get_ai_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check how many AI questions you have left today. Requires authentication."""
    user_id = str(current_user.user_id)
    today = date.today()
    
    result = await db.execute(
        text("SELECT questions_asked FROM ai_usage WHERE user_id = :uid AND usage_date = :today"),
        {"uid": user_id, "today": today}
    )
    usage = result.fetchone()
    questions_asked = usage[0] if usage else 0
    
    return {
        "questions_asked": questions_asked,
        "questions_remaining": 10 - questions_asked,
        "daily_limit": 10,
        "resets_at": "midnight UTC"
    }