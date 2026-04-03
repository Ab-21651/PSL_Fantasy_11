# 🏏 CricMind - Automated Match Data Pipeline

## 📋 Complete Workflow

### **Step 1: Install Scraper Dependencies**
```bash
cd "C:\Users\US\OneDrive\Desktop\PSL Project"
pip install -r requirements_scraper.txt
```

### **Step 2: Scrape Match Data from Cricinfo**

**Option A: Scrape ONLY Latest Match (Recommended for updates)**
```bash
python scrape_cricinfo.py --latest
```

**Option B: Scrape Last N Matches**
```bash
python scrape_cricinfo.py --last 3  # Scrape last 3 matches
```

**Option C: Scrape ALL Completed Matches**
```bash
python scrape_cricinfo.py
```

**What it does:**
- ✅ Finds completed PSL 2026 matches on ESPNCricinfo
- ✅ Scrapes full scorecards (batting, bowling, fielding)
- ✅ Extracts match info (teams, date, venue, winner)
- ✅ Saves to `match_results_2026.csv`
- ✅ **Only scrapes what you need** - no wasted time!

**Output:**
```csv
match_date,team_home,team_away,venue,winner,player_name,runs_scored,balls_faced,fours,sixes,dismissed,wickets_taken,overs_bowled,runs_given,maidens,catches,stumpings,run_outs
2026-04-01,Hyderabad Kingsmen,Multan Sultans,Gaddafi Stadium Lahore,Sultans,Saim Ayub,27,20,3,1,true,0,0.0,0,0,0,0,0
2026-04-01,Hyderabad Kingsmen,Multan Sultans,Gaddafi Stadium Lahore,Sultans,Maaz Sadaqat,62,26,5,5,true,0,0.0,0,0,0,0,0
```

### **Step 3: Seed Database**
```bash
python seed_match_results.py
```

**What it does:**
- ✅ Reads `match_results_2026.csv`
- ✅ Looks up player team from `players` table
- ✅ Determines opponent automatically
- ✅ Calculates fantasy points
- ✅ Updates `recent_form` table with opponent info
- ✅ Updates `career_stats` 2026 totals
- ✅ No manual work needed!

---

## 🔄 Update Workflow (After Each Match)

### **⚡ Quick Update (After Each New Match)**
```bash
# 1. Scrape ONLY the latest match
python scrape_cricinfo.py --latest

# 2. Seed database
python seed_match_results.py
```

**💡 Pro Tip:** This only scrapes the newest match, so it's super fast!

### **Option B: Via API (results.py)**
After creating `results.py` in FastAPI:

```bash
POST http://localhost:8000/results/{match_id}
{
  "winner": "Multan Sultans",
  "venue": "Gaddafi Stadium Lahore",
  "players": [
    {
      "player_name": "Saim Ayub",
      "runs_scored": 27,
      "balls_faced": 20,
      "fours": 3,
      "sixes": 1,
      "dismissed": true,
      "wickets_taken": 0,
      "catches": 0
    }
  ]
}
```

---

## 📊 Data Flow

```
ESPNCricinfo Match Pages
    ↓ (scrape_cricinfo.py)
match_results_2026.csv
    ↓ (seed_match_results.py)
Supabase Database
    ├─ recent_form (with opponent!)
    ├─ career_stats (updated totals)
    ├─ matchday_team_players (points calculated)
    └─ points_log (audit trail)
```

---

## 🎯 What Gets Updated

### **recent_form table:**
```sql
player_id | player_name | match_date | opponent        | runs | wickets | points | venue
----------|-------------|------------|-----------------|------|---------|--------|-------
0a4736eb  | Asif Ali    | 2026-04-01 | Multan Sultans | 9    | 0       | 10     | Lahore
```

### **career_stats table:**
```sql
player_id | season | matches | runs | wickets | catches
----------|--------|---------|------|---------|--------
0a4736eb  | 2026   | 6       | 247  | 0       | 4
```

### **matchday_team_players:**
```sql
matchday_team_id | player_id | is_captain | points_earned
-----------------|-----------|------------|---------------
uuid-123         | 0a4736eb  | true       | 20.0  (10 * 2x)
```

---

## ⚙️ Configuration

Edit `.env` file:
```env
# Supabase Connection
DB_HOST=db.yourproject.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
```

---

## 🐛 Troubleshooting

### **"Player not found" warnings**
```bash
⚠️  Player not found: A Zampa
```

**Solution:** Check player name in `players` table matches Cricinfo exactly
- Your DB: "Adam Zampa"
- Cricinfo: "A Zampa"
- Update seed_db.py ALIASES dict to map short names

### **No matches found**
- Verify Cricinfo URL in scraper matches current PSL 2026 series
- Check if matches are marked as "RESULT" status
- Try manual URL list instead of auto-discovery

### **Opponent showing as "Unknown"**
- Player's team in DB doesn't match either match team
- Check team name consistency (e.g., "Multan Sultan" vs "Multan Sultans")
- Update team-utils.ts mappings

---

## 📈 Next Steps

1. ✅ **Test the scraper:**
   ```bash
   python scrape_cricinfo.py
   ```

2. ✅ **Verify CSV output:**
   - Open `match_results_2026.csv`
   - Check player names match your `players` table

3. ✅ **Seed database:**
   ```bash
   python seed_match_results.py
   ```

4. ✅ **Query results:**
   ```sql
   SELECT * FROM recent_form WHERE season = '2026' ORDER BY match_date DESC LIMIT 10;
   ```

5. ✅ **Create results.py router** (for live API updates)

---

## 🎉 Benefits

✅ **Automatic opponent detection** - no manual lookup needed  
✅ **Fantasy points calculated** - uses official scoring rules  
✅ **Career stats updated** - cumulative totals maintained  
✅ **Audit trail** - points_log tracks every calculation  
✅ **Scalable** - works for entire PSL season automatically  

---

## 📞 Support

If scraper breaks (Cricinfo changes HTML structure):
1. Check scraper console output for errors
2. View source HTML of Cricinfo page
3. Update CSS selectors in `scrape_cricinfo.py`
4. Or use results.py API as backup

**Happy Scraping! 🏏🎯**
