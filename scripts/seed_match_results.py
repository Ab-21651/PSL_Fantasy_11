"""
CricMind — Database Seeder with Cricinfo Match Results
Seeds recent_form table with opposition and full match data
Aggregates batting + bowling stats for players appearing twice
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", 5432),
    "dbname":   os.getenv("DB_NAME", "cricmind"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Name aliases for matching (from original seed_db.py)
ALIASES = {
    "a zampa": "adam zampa",
    "ad hales": "alex hales",
    "m labuschagne": "marnus labuschagne",
    "mg bracewell": "michael bracewell",
    "am hardie": "aaron hardie",
    "irfan khan": "muhammad irfan khan",
    "salman agha": "agha salman",
    "khawaja nafay": "khawaja mohammad nafay",
    "sufiyan muqeem": "sufyan muqeem",
    "mohammad wasim": "muhammad wasim",
    "syed saad ali": "saad ali",
    "josh philippe": "joshua philippe",
    "steven smith": "steve smith",
    # Add more as needed from your original seed_db.py
}

def find_best_player_match(player_name, name_to_id_map):
    """
    Try to find player in database using fuzzy matching
    Returns (player_id, team, role, matched_name) or None
    """
    player_lower = player_name.strip().lower()
    
    # 1. Exact match
    if player_lower in name_to_id_map:
        info = name_to_id_map[player_lower]
        return (info['id'], info['team'], info['role'], player_name)
    
    # 2. Try with alias
    if player_lower in ALIASES:
        alias = ALIASES[player_lower]
        if alias in name_to_id_map:
            info = name_to_id_map[alias]
            return (info['id'], info['team'], info['role'], player_name)
    
    # 3. Fuzzy match: check if scraped name is a substring of DB name
    for db_name, info in name_to_id_map.items():
        # Check if player_lower is contained in db_name or vice versa
        if player_lower in db_name or db_name in player_lower:
            # Additional check: must share at least one word
            scraped_words = set(player_lower.split())
            db_words = set(db_name.split())
            if scraped_words & db_words:  # Intersection
                return (info['id'], info['team'], info['role'], db_name)
    
    # 4. Try without middle name (e.g., "Mohammad Haris" → "Mohammad" + "Haris")
    parts = player_lower.split()
    if len(parts) >= 2:
        # Try first + last name
        first_last = f"{parts[0]} {parts[-1]}"
        for db_name, info in name_to_id_map.items():
            if first_last in db_name or db_name in first_last:
                return (info['id'], info['team'], info['role'], db_name)
    
    return None

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def get_name_to_id_map(conn):
    """
    Returns lowercase name -> (player_id, team, role), including all aliases
    """
    with conn.cursor() as cur:
        cur.execute("SELECT player_id, player_name, team, role FROM players;")
        rows = cur.fetchall()
    
    # Build base map from DB (lowercase)
    base = {row[1].strip().lower(): {'id': row[0], 'team': row[2], 'role': row[3]} for row in rows}
    
    # Add aliases
    for short, full in ALIASES.items():
        if full in base:
            base[short] = base[full]
    
    return base

def aggregate_player_performances(df):
    """
    Combine batting and bowling stats for the same player in the same match
    """
    # Group by match_date, team_home, team_away, player_name
    grouped = df.groupby(['match_date', 'team_home', 'team_away', 'player_name', 'venue', 'winner']).agg({
        'runs_scored': 'sum',
        'balls_faced': 'sum',
        'fours': 'sum',
        'sixes': 'sum',
        'dismissed': 'max',  # True if dismissed at all
        'wickets_taken': 'sum',
        'overs_bowled': 'sum',
        'runs_given': 'sum',
        'maidens': 'sum',
        'catches': 'sum',
        'stumpings': 'sum',
        'run_outs': 'sum',
    }).reset_index()
    
    return grouped

def calculate_fantasy_points(row, role):
    """
    Calculate fantasy points based on performance
    """
    pts = 0.0
    
    # Batting points
    pts += row['runs_scored']
    pts += row['fours']
    pts += row['sixes'] * 2
    
    if row['runs_scored'] >= 100:
        pts += 25
    elif row['runs_scored'] >= 50:
        pts += 10
    
    if row['runs_scored'] == 0 and row['dismissed'] and role in ["Batsman", "Wicket-Keeper"]:
        pts -= 5
    
    # Bowling points
    pts += row['wickets_taken'] * 25
    pts += row['maidens'] * 12
    
    if row['overs_bowled'] >= 2 and row['runs_given'] > 0:
        economy = row['runs_given'] / row['overs_bowled']
        if economy < 6:
            pts += 6
        elif economy > 10:
            pts -= 6
    
    # Fielding points
    pts += row['catches'] * 10
    pts += row['stumpings'] * 15
    pts += row['run_outs'] * 10
    
    return round(pts, 1)

def normalize_team_name(team_name):
    """
    Normalize team names to handle variations
    """
    if not team_name:
        return ""
    
    team_lower = team_name.lower().strip()
    
    # Map variations to standard names
    team_map = {
        'peshawar zalmi': 'Peshawar Zalmi',
        'peshawar zamli': 'Peshawar Zalmi',
        'islamabad united': 'Islamabad United',
        'multan sultans': 'Multan Sultans',
        'multan sultan': 'Multan Sultans',
        'hyderabad kingsmen': 'Hyderabad Kingsmen',
        'lahore qalandars': 'Lahore Qalandars',
        'karachi kings': 'Karachi Kings',
        'quetta gladiators': 'Quetta Gladiators',
        'rawalpindi pindiz': 'Rawalpindi PindiZ',
        'rawalpindiz': 'Rawalpindi PindiZ',
    }
    
    # Try exact match first
    if team_lower in team_map:
        return team_map[team_lower]
    
    # Try partial match
    for key, value in team_map.items():
        if key in team_lower or team_lower in key:
            return value
    
    return team_name  # Return original if no match


def update_match_status(cursor, match_date, team_home, team_away, winner):
    """
    Update match status with fuzzy team name matching
    """
    # Normalize team names
    norm_home = normalize_team_name(team_home)
    norm_away = normalize_team_name(team_away)
    norm_winner = normalize_team_name(winner)
    
    # Try exact match first
    cursor.execute("""
        UPDATE matches 
        SET status = 'completed', winner = %s
        WHERE match_date = %s 
          AND team_home = %s 
          AND team_away = %s
          AND status != 'completed'
    """, (norm_winner, match_date, norm_home, norm_away))
    
    if cursor.rowcount > 0:
        return True
    
    # If no exact match, try fuzzy match
    cursor.execute("""
        UPDATE matches 
        SET status = 'completed', winner = %s
        WHERE match_date = %s 
          AND (team_home ILIKE %s OR team_home ILIKE %s)
          AND (team_away ILIKE %s OR team_away ILIKE %s)
          AND status != 'completed'
    """, (norm_winner, match_date, f'%{norm_home}%', f'%{norm_away}%', 
          f'%{norm_away}%', f'%{norm_home}%'))
    
    return cursor.rowcount > 0


def get_opponent(team_home, team_away, player_team):
    """
    Determine opponent based on which team the player is on
    """
    if not player_team:
        return "Unknown"
    
    player_team_lower = player_team.lower()
    
    if team_home.lower() in player_team_lower or player_team_lower in team_home.lower():
        return team_away
    elif team_away.lower() in player_team_lower or player_team_lower in team_away.lower():
        return team_home
    else:
        # If no match, return away team as default
        return team_away

def seed_match_results(csv_file='match_results_2026.csv'):
    """
    Seed recent_form and update career_stats from scraped match results
    Aggregates batting + bowling for same player
    Updates match status to 'completed'
    """
    print(f"📥 Loading match results from {csv_file}...")
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        print("   Run scrape_cricinfo.py first!")
        return
    
    df = pd.read_csv(csv_file)
    print(f"📊 Found {len(df)} player performance rows")
    
    # Aggregate duplicate players (batting + bowling)
    print("🔄 Aggregating batting and bowling stats for same players...")
    df_agg = aggregate_player_performances(df)
    print(f"✅ Aggregated to {len(df_agg)} unique player performances")
    
    conn = get_conn()
    cursor = conn.cursor()
    
    # Get player ID mapping
    name_to_data = get_name_to_id_map(conn)
    
    recent_form_rows = []
    updated_players = set()
    skipped_players = []
    processed_matches = set()  # Track matches to update status
    
    for idx, row in df_agg.iterrows():
        player_name = row['player_name'].strip()
        
        # Use fuzzy matching to find player
        match_result = find_best_player_match(player_name, name_to_data)
        
        if not match_result:
            skipped_players.append(player_name)
            continue
        
        player_id, player_team, player_role, matched_name = match_result
        
        # Determine opponent
        opponent = get_opponent(row['team_home'], row['team_away'], player_team)
        
        # Calculate fantasy points
        points = calculate_fantasy_points(row, player_role)
        
        # Prepare recent_form row with ALL fields
        recent_form_rows.append((
            player_id,
            matched_name,  # Use DB name, not scraped name
            row['match_date'],
            opponent,
            int(row['runs_scored']),
            int(row.get('balls_faced', 0)),
            int(row.get('fours', 0)),
            int(row.get('sixes', 0)),
            int(row['wickets_taken']),
            float(row.get('overs_bowled', 0.0)),
            int(row.get('runs_given', 0)),
            int(row.get('maidens', 0)),
            int(row.get('catches', 0)),
            int(row.get('stumpings', 0)),
            int(row.get('run_outs', 0)),
            int(points),
            row['venue'],
            '2026'
        ))
        
        updated_players.add(matched_name)
        
        # Track match for status update
        match_key = (row['match_date'], row['team_home'], row['team_away'])
        processed_matches.add((match_key, row['winner']))
        
        # Update career stats (ADD to existing, don't overwrite)
        cursor.execute("""
            SELECT runs, wickets, matches, catches 
            FROM career_stats 
            WHERE player_id = %s AND season = '2026'
        """, (player_id,))
        
        stats = cursor.fetchone()
        
        if stats:
            # ADD to existing stats
            new_runs = (stats[0] or 0) + int(row['runs_scored'])
            new_wickets = (stats[1] or 0) + int(row['wickets_taken'])
            new_matches = (stats[2] or 0) + 1
            new_catches = (stats[3] or 0) + int(row.get('catches', 0))
            
            cursor.execute("""
                UPDATE career_stats SET
                    runs = %s,
                    wickets = %s,
                    matches = %s,
                    catches = %s
                WHERE player_id = %s AND season = '2026'
            """, (new_runs, new_wickets, new_matches, new_catches, player_id))
        else:
            # First match for this player in 2026
            cursor.execute("""
                INSERT INTO career_stats 
                (player_id, player_name, season, matches, runs, wickets, catches)
                VALUES (%s, %s, '2026', 1, %s, %s, %s)
            """, (player_id, matched_name, int(row['runs_scored']), 
                  int(row['wickets_taken']), int(row.get('catches', 0))))
    
    # Bulk insert recent_form (skip if already exists)
    if recent_form_rows:
        execute_values(cursor, """
            INSERT INTO recent_form 
            (player_id, player_name, match_date, opponent, 
             runs_scored, balls_faced, fours, sixes,
             wickets_taken, overs_bowled, runs_given, maidens,
             catches, stumpings, run_outs,
             points_earned, venue, season)
            VALUES %s
            ON CONFLICT DO NOTHING
        """, recent_form_rows)
        
        print(f"\n✅ Inserted/Updated {len(recent_form_rows)} recent_form entries")
        print(f"✅ Updated career stats for {len(updated_players)} players")
        
        if skipped_players:
            unique_skipped = list(set(skipped_players))
            print(f"\n⚠️  Skipped {len(unique_skipped)} unmatched players:")
            print(f"   {unique_skipped[:10]}")
            print(f"   Try adding these to ALIASES dict or check player names in database")
    
    # Update match statuses to 'completed'
    print(f"\n🏁 Updating {len(processed_matches)} matches to 'completed' status...")
    matches_updated = 0
    
    for match_info, winner in processed_matches:
        match_date, team_home, team_away = match_info
        
        if update_match_status(cursor, match_date, team_home, team_away, winner):
            matches_updated += 1
    
    print(f"✅ Updated {matches_updated} matches to 'completed' status")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n🎉 Database seeding complete!")
    print(f"   Recent form entries: {len(recent_form_rows)}")
    print(f"   Players updated: {len(updated_players)}")
    print(f"   Matches completed: {matches_updated}")


if __name__ == "__main__":
    seed_match_results()
