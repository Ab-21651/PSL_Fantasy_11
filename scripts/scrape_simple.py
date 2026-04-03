"""
Fixed Cricinfo Scraper - Simplified and more robust
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re

BASE_URL = "https://www.espncricinfo.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def scrape_match(match_url):
    """Scrape a single match"""
    print(f"\n🏏 Scraping: {match_url}")
    
    response = requests.get(match_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract teams from title - THIS IS THE KEY FIX
    teams = ["Unknown", "Unknown"]
    title = soup.find('title')
    if title and ' vs ' in title.text:
        parts = title.text.split(' vs ')
        teams[0] = parts[0].strip()
        teams[1] = parts[1].split(',')[0].strip()
    
    print(f"   Teams: {teams[0]} vs {teams[1]}")
    
    # Extract venue - look harder
    venue = "Unknown Venue"
    # Try all text elements for stadium/ground
    for elem in soup.find_all(['span', 'div', 'p']):
        text = elem.text
        if 'Stadium' in text or 'Ground' in text:
            if len(text) < 100:  # Avoid long paragraphs
                venue = text.strip()
                break
    
    print(f"   Venue: {venue}")
    
    # Extract winner - improved
    winner = teams[0]  # Default to team1
    for elem in soup.find_all(['p', 'span', 'div']):
        text = elem.text.lower()
        if 'won by' in text:
            # "Lahore Qalandars won by 5 wickets"
            winner_text = text.split('won by')[0].strip()
            # Check which team it matches
            for team in teams:
                if team.lower() in winner_text:
                    winner = team
                    break
            break
    
    print(f"   Winner: {winner}")
    
    # Extract date
    match_date = datetime.now().strftime("%Y-%m-%d")
    for elem in soup.find_all('span'):
        text = elem.text
        # Look for "Apr 02, 2026" format
        if re.search(r'[A-Z][a-z]{2} \d{2}, \d{4}', text):
            try:
                parsed_date = datetime.strptime(text.strip(), "%b %d, %Y")
                match_date = parsed_date.strftime("%Y-%m-%d")
                break
            except:
                pass
    
    print(f"   Date: {match_date}")
    
    # Extract batting
    all_performances = []
    batting_tables = soup.find_all('table', class_='ci-scorecard-table')
    
    for table in batting_tables:
        tbody = table.find('tbody')
        if not tbody:
            continue
        
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 7:
                continue
            
            # Player name - clean it
            player = cells[0].text.strip().replace('\xa0', ' ').replace('(c)', '').replace('†', '').strip()
            
            # Skip non-player rows
            if any(x in player.lower() for x in ['extra', 'total', 'did not', 'fall']):
                continue
            
            dismissal = cells[1].text.strip()
            runs = cells[2].text.strip()
            balls = cells[3].text.strip()
            fours = cells[5].text.strip()
            sixes = cells[6].text.strip()
            
            dismissed = 'not out' not in dismissal.lower() and dismissal != ''
            
            # Parse catches from dismissal
            catches, stumpings, run_outs = parse_dismissal(dismissal)
            
            all_performances.append({
                'match_date': match_date,
                'team_home': teams[0],
                'team_away': teams[1],
                'venue': venue,
                'winner': winner,
                'player_name': player,
                'runs_scored': int(runs) if runs.isdigit() else 0,
                'balls_faced': int(balls) if balls.isdigit() else 0,
                'fours': int(fours) if fours.isdigit() else 0,
                'sixes': int(sixes) if sixes.isdigit() else 0,
                'dismissed': dismissed,
                'wickets_taken': 0,
                'overs_bowled': 0.0,
                'runs_given': 0,
                'maidens': 0,
                'catches': catches,
                'stumpings': stumpings,
                'run_outs': run_outs,
            })
    
    # Extract bowling
    bowling_tables = soup.find_all('table')
    for table in bowling_tables:
        headers = [th.text.strip() for th in table.find_all('th')]
        if 'Bowling' not in headers and 'O' not in headers:
            continue
        
        tbody = table.find('tbody')
        if not tbody:
            continue
        
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 5:
                continue
            
            player = cells[0].text.strip().replace('\xa0', ' ').replace('(c)', '').replace('†', '').strip()
            if not player or len(player) < 2:
                continue
            
            overs = cells[1].text.strip()
            maidens = cells[2].text.strip()
            runs_given = cells[3].text.strip()
            wickets = cells[4].text.strip()
            
            all_performances.append({
                'match_date': match_date,
                'team_home': teams[0],
                'team_away': teams[1],
                'venue': venue,
                'winner': winner,
                'player_name': player,
                'runs_scored': 0,
                'balls_faced': 0,
                'fours': 0,
                'sixes': 0,
                'dismissed': False,
                'wickets_taken': int(wickets) if wickets.isdigit() else 0,
                'overs_bowled': float(overs) if overs.replace('.', '').isdigit() else 0.0,
                'runs_given': int(runs_given) if runs_given.isdigit() else 0,
                'maidens': int(maidens) if maidens.isdigit() else 0,
                'catches': 0,
                'stumpings': 0,
                'run_outs': 0,
            })
    
    print(f"   ✅ Extracted {len(all_performances)} player performances")
    return all_performances


def parse_dismissal(dismissal_text):
    """Extract fielding from dismissal"""
    catches, stumpings, run_outs = 0, 0, 0
    
    dismissal_lower = dismissal_text.lower()
    
    if dismissal_lower.startswith('c ') or 'c & b' in dismissal_lower or 'c&b' in dismissal_lower:
        catches = 1
    elif dismissal_lower.startswith('st '):
        stumpings = 1
    elif 'run out' in dismissal_lower:
        run_outs = 1
    
    return catches, stumpings, run_outs


if __name__ == "__main__":
    import sys
    
    # Get match URL from command line or use default
    if len(sys.argv) > 1:
        match_url = sys.argv[1]
    else:
        # Default to latest PSL match
        match_url = "https://www.espncricinfo.com/series/pakistan-super-league-2026-1515734/karachi-kings-vs-rawalpindiz-10th-match-1527561/full-scorecard"
    
    performances = scrape_match(match_url)
    
    if performances:
        df = pd.DataFrame(performances)
        df.to_csv('match_results_2026.csv', index=False)
        print(f"\n✅ Saved to match_results_2026.csv")
        print(f"📌 Run: python seed_match_results.py")
    else:
        print("\n❌ No data extracted")
