# filter_players.py
import json
import os
from datetime import datetime

import requests

VALID_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DEF"}
EXCLUDED_STATUSES = {"injured_reserve", "non_football_injury", "physically_unable_to_perform"}

SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"
OUTPUT_PATH = "docs/players_2025.json"


def filter_players(players: dict) -> dict:
    """
    Return a dict keyed by player_id with only the fields:
    full_name, status, years_exp, player_id, team, position.
    Applies filters for active NFL players on valid positions, with allowed statuses.
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
        if not p.get("team"):
            continue

        filtered[pid] = {
            "player_id": str(pid),
            "full_name": p.get("full_name"),
            "status": p.get("status"),
            "years_exp": p.get("years_exp"),
            "team": p.get("team"),
            "position": p.get("position"),
        }
    return filtered


def main():
    # Fetch
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
