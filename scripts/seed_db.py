"""
CricMind — Database Seeder
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

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def clean_df(df):
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={"layer_id": "player_id"})
    df = df.where(pd.notna(df), None)
    return df

def normalize_season(s):
    return str(s).strip().replace(".0", "")

# Short code → full name (all lowercase, must match players.csv exactly after lowercasing)
ALIASES = {
    "a zampa":             "adam zampa",
    "ad hales":            "alex hales",
    "af milne":            "adam milne",
    "ags gous":            "matthew gous",
    "aj hosein":           "akeal hosein",
    "aj turner":           "ashton turner",
    "as joseph":           "alzarri joseph",
    "b muzarabani":        "blessing muzarabani",
    "bj dwarshuis":        "byron dwarshuis",
    "bkg mendis":          "kusal mendis",
    "br mcdermott":        "ben mcdermott",
    "c campher":           "curtis campher",
    "c munro":             "colin munro",
    "cj jordan":           "chris jordan",
    "cr brathwaite":       "carlos brathwaite",
    "d madushanka":        "dilshan madushanka",
    "d wiese":             "david wiese",
    "da warner":           "david warner",
    "dj malan":            "dawid malan",
    "dj mitchell":         "daryl mitchell",
    "dj willey":           "david willey",
    "dr mousley":          "dan mousley",
    "dr sams":             "daniel sams",
    "fh allen":            "finn allen",
    "gf linde":            "george linde",
    "he van der dussen":   "rassie van der dussen",
    "j charles":           "johnson charles",
    "j little":            "josh little",
    "jds neesham":         "jimmy neesham",
    "jj roy":              "jason roy",
    "jl du plooy":         "leus du plooy",
    "jm cox":              "jordan cox",
    "jm vince":            "james vince",
    "jo holder":           "jason holder",
    "ka jamieson":         "kyle jamieson",
    "ka pollard":          "kieron pollard",
    "kr mayers":           "kyle mayers",
    "l tucker":            "lorcan tucker",
    "l wood":              "luke wood",
    "ld chandimal":        "dinesh chandimal",
    "lj evans":            "laurie evans",
    "m bryant":            "mac bryant",
    "m labuschagne":       "marnus labuschagne",
    "mdkj perera":         "kusal perera",
    "mg bracewell":        "michael bracewell",
    "mj guptill":          "martin guptill",
    "mj owen":             "mitchell owen",
    "mm ali":              "moeen ali",
    "ms chapman":          "mark chapman",
    "mw forde":            "matthew forde",
    "mohammad nawaz (3)":  "mohammad nawaz",
    "muhammad naeem":      "muhammad naeem",
    "naveen-ul-haq":       "naveen ul haq",
    "oc mccoy":            "obed mccoy",
    "op stone":            "olly stone",
    "p hatzoglou":         "peter hatzoglou",
    "pbb rajapaksa":       "bhanuka rajapaksa",
    "pi walter":           "paul walter",
    "parvez hossain emon": "parvez hossain emon",
    "r powell":            "rovman powell",
    "rp meredith":         "riley meredith",
    "rr hendricks":        "reeza hendricks",
    "rr rossouw":          "rilee rossouw",
    "sa abbott":           "sean abbott",
    "sd hope":             "shai hope",
    "se rutherford":       "sam rutherford",
    "sw billings":         "sam billings",
    "t kohler-cadmore":    "tom kohler-cadmore",
    "t shamsi":            "tabraiz shamsi",
    "tk curran":           "tom curran",
    "tl seifert":          "tim seifert",
    "ts mills":            "tymal mills",
    "wia fernando":        "asitha fernando",
    "zahid mahmood":       "zahid mahmood",
    "zaman khan":          "zaman khan",
    "ags gous":            "andries gous",
    "agha salman":         "salman ali agha",
    "muhammad naeem":      "mohammad naeem",
    "haseebullah khan":    "haseebullah",
    "parvez hossain emon": "parvez hussain emon",
    "irfan khan":          "muhammad irfan khan",
    "waseem muhammad":     "muhammad waseem",
    "khawaja nafay":       "khawaja mohammad nafay",
    "sufiyan muqeem":      "sufyan muqeem",
    "ts mills":            "tymal mills",
    "d wiese":             "david wiese",
    "ad hales":            "alex hales",
    "c munro":             "colin munro",
    "jo holder":           "jason holder",
    "fh allen":            "finn allen",
    "agha salman":         "agha salman",
    "salman fayyaz":       "salman fayyaz",
}

def get_name_to_id_map(conn):
    """Returns lowercase name -> player_id, including all aliases."""
    with conn.cursor() as cur:
        cur.execute("SELECT player_id, player_name FROM players;")
        rows = cur.fetchall()

    # Build base map from DB (lowercase)
    base = {row[1].strip().lower(): row[0] for row in rows}

    # Debug: print all player names so we can see exact spelling
    # Uncomment below if aliases still fail:
    # print("  DB names sample:", list(base.keys())[:20])

    # Add aliases — resolve through base map
    for short, full in ALIASES.items():
        if full in base:
            base[short] = base[full]
        # Also try: maybe the full name IS the key with different casing
        for db_name in list(base.keys()):
            if db_name == full:
                base[short] = base[db_name]
                break

    return base


def load_players(conn, filepath="players.csv"):
    print(f"Loading players from {filepath}...")
    df = clean_df(pd.read_csv(filepath))
    df = df.rename(columns={"name": "player_name"})

    rows = [
        (
            str(row["player_id"]).strip(),
            str(row["player_name"]).strip(),
            row.get("team"),
            row.get("role"),
            row.get("nationality"),
            row.get("age"),
        )
        for _, row in df.iterrows()
    ]

    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO players (player_id, player_name, team, role, nationality, age)
            VALUES %s
            ON CONFLICT (player_id) DO UPDATE SET
                player_name = EXCLUDED.player_name,
                team        = EXCLUDED.team,
                role        = EXCLUDED.role,
                nationality = EXCLUDED.nationality,
                age         = EXCLUDED.age
        """, rows)
    conn.commit()
    print(f"  Inserted/updated {len(rows)} players.")


def load_career_stats(conn, filepath, season_label):
    print(f"Loading career stats from {filepath} (season={season_label})...")
    df = clean_df(pd.read_csv(filepath))
    season = normalize_season(season_label)
    name_to_id = get_name_to_id_map(conn)

    rows = []
    skipped = []
    seen = set()  # track (player_id, season) to avoid duplicate conflict

    for _, row in df.iterrows():
        raw_name = str(row.get("player_name", "")).strip()
        player_id = name_to_id.get(raw_name.lower())

        if not player_id:
            skipped.append(raw_name)
            continue

        key = (player_id, season)
        if key in seen:
            # Duplicate in same CSV — skip second occurrence
            continue
        seen.add(key)

        rows.append((
            player_id,
            raw_name,
            season,
            int(row["matches"])   if row.get("matches")        is not None else 0,
            int(row["runs"])      if row.get("runs")           is not None else 0,
            row.get("average"),
            row.get("strike_rate"),
            int(row["wickets"])   if row.get("wickets")        is not None else 0,
            row.get("economy"),
            row.get("bowling_average"),
            int(row["catches"])   if row.get("catches")        is not None else 0,
        ))

    if not rows:
        print(f"  No matches. Skipped {len(skipped)} rows.")
        print(f"  Sample unmatched: {skipped[:5]}")
        return

    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO career_stats
                (player_id, player_name, season, matches, runs, average,
                 strike_rate, wickets, economy, bowling_average, catches)
            VALUES %s
            ON CONFLICT (player_id, season) DO UPDATE SET
                matches         = EXCLUDED.matches,
                runs            = EXCLUDED.runs,
                average         = EXCLUDED.average,
                strike_rate     = EXCLUDED.strike_rate,
                wickets         = EXCLUDED.wickets,
                economy         = EXCLUDED.economy,
                bowling_average = EXCLUDED.bowling_average,
                catches         = EXCLUDED.catches
        """, rows)
    conn.commit()
    print(f"  Inserted/updated {len(rows)} rows. Skipped {len(skipped)} unmatched.")
    if skipped:
        print(f"  Still unmatched: {skipped[:8]}{'...' if len(skipped) > 8 else ''}")


def load_recent_form(conn, filepath="recent_form.csv"):
    print(f"Loading recent form from {filepath}...")
    df = clean_df(pd.read_csv(filepath))
    df["match_date"] = pd.to_datetime(df["match_date"])
    df["season"] = df["match_date"].apply(
        lambda d: "2026" if d.year == 2026 else "2025" if d.year == 2025 else "2023/24"
    )
    name_to_id = get_name_to_id_map(conn)

    rows = []
    skipped = []
    for _, row in df.iterrows():
        raw_name = str(row.get("player_name", "")).strip()
        player_id = name_to_id.get(raw_name.lower())
        if not player_id:
            skipped.append(raw_name)
            continue
        rows.append((
            player_id,
            raw_name,
            row["match_date"].date(),
            row.get("opponent"),
            int(row["runs_scored"])   if row.get("runs_scored")   is not None else 0,
            int(row["wickets_taken"]) if row.get("wickets_taken") is not None else 0,
            int(row["points_earned"]) if row.get("points_earned") is not None else 0,
            row.get("venue"),
            row["season"],
        ))

    if not rows:
        print(f"  No matches. Skipped {len(skipped)} rows.")
        return

    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO recent_form
                (player_id, player_name, match_date, opponent,
                 runs_scored, wickets_taken, points_earned, venue, season)
            VALUES %s
        """, rows)
    conn.commit()
    print(f"  Inserted {len(rows)} rows. Skipped {len(skipped)} unmatched.")


if __name__ == "__main__":
    print("Connecting to database...")
    conn = get_conn()
    print("Connected.\n")

    load_players(conn, "players.csv")
    # load_career_stats(conn, "career_stats_2023_24.csv", "2023/24")
    # load_career_stats(conn, "career_stats_2025.csv",    "2025")
    load_career_stats(conn, "career_stats_2026.csv",    "2026")
    #load_recent_form(conn, "recent_form.csv")
    # load_career_stats(conn, "psl_2026.csv",    "2026")
    conn.close()
    print("\nAll done! Database seeded successfully.")