# 🎯 Fantasy Points System - User Guide

## **What Users See vs What They Don't**

### ✅ **VISIBLE to Users (For Team Selection)**
Users can see these stats to make informed decisions:

- **Career Stats:**
  - Total runs, wickets, catches
  - Batting average, strike rate
  - Bowling economy, average
  - Matches played

- **Recent Form (Last 5 Matches):**
  - Runs scored, balls faced
  - Fours, sixes hit
  - Wickets taken, overs bowled
  - Runs given, maidens
  - Catches, stumpings, run-outs
  - Opponent name
  - Match venue

- **Player Info:**
  - Name, team, role
  - Credits (price)
  - Nationality, age

### ❌ **HIDDEN from Users**
To maintain fairness and skill-based selection:

- **Fantasy Points** from past matches
  - Users must predict future performance, not copy past results
  - Points only shown AFTER match on leaderboard
  - This is how all major fantasy platforms work (Dream11, FanDuel, etc.)

---

## 📊 **Fantasy Points Calculation**

Points are calculated **AFTER** the match completes:

### **Batting Points**
| Action | Points |
|--------|--------|
| Every run | +1 |
| Every four | +1 |
| Every six | +2 |
| Half-century (50 runs) | +10 bonus |
| Century (100 runs) | +25 bonus |
| Duck (0 runs, dismissed) | -5 (Batsmen/WK only) |

### **Bowling Points**
| Action | Points |
|--------|--------|
| Every wicket | +25 |
| Every maiden over | +12 |
| Economy < 6.0 (min 2 overs) | +6 bonus |
| Economy > 10.0 (min 2 overs) | -6 penalty |

### **Fielding Points**
| Action | Points |
|--------|--------|
| Catch | +10 |
| Stumping | +15 |
| Run-out | +10 |

### **Captain/Vice-Captain Multipliers**
- **Captain:** Points × 2.0
- **Vice-Captain:** Points × 1.5

---

## 🎮 **How Fantasy Selection Works**

### **Before Match (Team Selection Phase)**
1. ✅ Users see career stats and recent form
2. ✅ Users create teams based on:
   - Player's historical performance
   - Recent form trends
   - Role (Batsman, Bowler, All-Rounder, WK)
   - Price/Credits
   - Team composition rules (max 7 from one team, etc.)
3. ❌ Users **DO NOT** see fantasy points from past matches
4. ✅ Users select Captain (2x points) and Vice-Captain (1.5x points)

### **After Match (Points Calculation)**
1. ✅ Scraper gets match results from Cricinfo
2. ✅ System calculates fantasy points for each player
3. ✅ Captain/VC multipliers applied to user teams
4. ✅ Leaderboard updated with final scores
5. ✅ Users can NOW see points earned

---

## 🏆 **Why Hide Points Before Selection?**

**Problem if points are visible:**
- Users just copy the highest-scoring players from last match
- No skill involved - just pattern matching
- Everyone picks the same team
- Boring and defeats the purpose of fantasy sports

**Solution (current implementation):**
- Users must analyze stats and predict performance
- Requires cricket knowledge and strategy
- Creates variety in team selections
- Rewards good cricket insights

---

## 🔄 **Typical User Flow**

1. **Team Selection:**
   ```
   User views upcoming match: KK vs MS
   ↓
   Reviews player stats, recent form
   ↓
   Analyzes: "Babar Azam has 3 fifties in last 5 matches vs spin-heavy teams"
   ↓
   Selects players within budget (100 credits)
   ↓
   Chooses Captain (2x) and VC (1.5x)
   ↓
   Submits team before match deadline
   ```

2. **Match Day:**
   ```
   Match happens in real life
   ↓
   Admin runs: python scrape_cricinfo.py --latest
   ↓
   Admin runs: python seed_match_results.py
   ↓
   Points calculated for all players
   ↓
   User teams scored with Captain/VC multipliers
   ↓
   Leaderboard updated
   ```

3. **After Match:**
   ```
   Users see their rank and total points
   ↓
   Can view breakdown: which players scored how many points
   ↓
   Learn from performance for next match
   ```

---

## 🎯 **API Endpoints Reference**

### **For Users (Frontend)**
```http
GET /players                    # List all players with basic info
GET /players/{id}/stats         # Career stats (NO POINTS)
GET /players/{id}/form          # Recent form (NO POINTS)
GET /matches/upcoming           # Next 5 matches
GET /matches/{id}               # Match details with squads
POST /fantasy/teams             # Create fantasy team
GET /fantasy/teams/{id}         # View team
GET /fantasy/leaderboard        # Rankings AFTER match
```

### **For Admins (Backend)**
```http
POST /results/{match_id}        # Submit match results + auto-calculate points
POST /matches/auto-complete     # Mark past matches as completed
```

---

## 📌 **Key Takeaways**

1. ✅ **Career stats and recent form are PUBLIC** - helps users make informed decisions
2. ❌ **Fantasy points are HIDDEN before match** - maintains fairness
3. ✅ **Points only shown on leaderboard AFTER match** - rewards prediction skill
4. ✅ **Scraper gets latest match only** - fast updates
5. ✅ **Auto-completion of past matches** - based on date, not manual updates

---

## 🚀 **Quick Commands**

```bash
# After a new match completes:
python scrape_cricinfo.py --latest
python seed_match_results.py

# Restart FastAPI to reflect changes:
uvicorn app.main:app --reload

# Check leaderboard:
GET http://localhost:8000/fantasy/leaderboard?matchday_id={id}
```

---

**Built with ❤️ for fair fantasy cricket! 🏏**
