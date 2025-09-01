# filter_players.py
import json
import os
from datetime import datetime
import requests

VALID_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DEF"}
EXCLUDED_STATUSES = {"injured_reserve", "non_football_injury", "physically_unable_to_perform"}

SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"
OUTPUT_PATH = "docs/players_2025.json"

# Full NFL team map for DEF generation
TEAM_MAP = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LV": "Las Vegas Raiders",
    "LAC": "Los Angeles Chargers",
    "LAR": "Los Angeles Rams",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SEA": "Seattle Seahawks",
    "SF": "San Francisco 49ers",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders",
}


def filter_players(players: dict) -> dict:
    """
    Return a dict keyed by player_id with only the fields:
    player_id, full_name, first_name, last_name, position,
    status, years_exp, depth_chart_order, team.
    Includes all 32 DEF teams with empty fields for status/years_exp/depth_chart_order.
    """
    filtered = {}

    for pid, p in players.items():
        if not p.get("active"):
            continue
        if p.get("sport") != "nfl":
            continue
        if p.get("position") not in VALID_POSITIONS:
            continue
        if (p.get("status") or "").lower() in EXCLUDED_STATUSES:
            continue

        player_id = str(pid)
        position = p.get("position")

        if position == "DEF":
            # Skip — we’ll handle defenses separately
            continue

        filtered[player_id] = {
            "player_id": player_id,
            "full_name": p.get("full_name"),
            "first_name": p.get("first_name"),
            "last_name": p.get("last_name"),
            "position": position,
            "status": p.get("status"),
            "years_exp": p.get("years_exp"),
            "depth_chart_order": p.get("depth_chart_order"),
            "team": p.get("team"),
        }

    # Add all 32 DEF teams
    for abbr, full_name in TEAM_MAP.items():
        first, last = full_name.split(" ", 1)
        filtered[abbr] = {
            "player_id": abbr,
            "full_name": full_name,
            "first_name": first,
            "last_name": last,
            "position": "DEF",
            "status": "",
            "years_exp": "",
            "depth_chart_order": "",
            "team": abbr,
        }

    return filtered


def main():
    # Fetch from Sleeper
    r = requests.get(SLEEPER_PLAYERS_URL, timeout=60)
    r.raise_for_status()
    all_players = r.json()

    # Filter + slim fields
    filtered = filter_players(all_players)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Write JSON (stable key order for clean diffs)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, sort_keys=True, ensure_ascii=False)

    print(
        f"Total players: {len(all_players)} | "
        f"Filtered: {len(filtered)} | "
        f"Saved to {OUTPUT_PATH} @ {datetime.now().isoformat(timespec='seconds')}"
    )


if __name__ == "__main__":
    main()
