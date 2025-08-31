# filter_players.py
import requests
import json
from datetime import datetime

VALID_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DEF"}
EXCLUDED_STATUSES = {"injured_reserve", "non_football_injury", "physically_unable_to_perform"}

def filter_players(players):
    return {
        pid: {
            "player_id": pid,
            "full_name": p.get("full_name"),
            "status": p.get("status"),
            "years_exp": p.get("years_exp"),
            "team": p.get("team"),
            "position": p.get("position"),
        }
        for pid, p in players.items()
        if p.get("active")
        and p.get("position") in VALID_POSITIONS
        and (p.get("status") or "").lower() not in EXCLUDED_STATUSES
        and p.get("team")
        and p.get("sport") == "nfl"
    }


if __name__ == "__main__":
    r = requests.get("https://api.sleeper.app/v1/players/nfl")
    all_players = r.json()
    filtered = filter_players(all_players)

    output_path = "docs/players_2025.json"
    with open(output_path, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"Filtered {len(filtered)} players @ {datetime.now()}")
