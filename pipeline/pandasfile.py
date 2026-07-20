import json
import pandas as pd

def load_rounds_dataframe(json_path="rounds_raw.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    team_tag = data["team_tag"]
    team_id = data["team_id"]
    rows = []

    for match in data["matches"]:
        for map_data in match["maps"]:
            for r in map_data["rounds"]:
                row = {
                    "match_id": match["match_id"],
                    "map_name": map_data["map_name"],
                    **r,  # number, winner_team_short, method, score, + anything else found
                }
                row["won_by_queried_team"] = r.get("winner_team_short") == team_tag
                row["fnc_side"] = fnc_side(r, team_id)
                rows.append(row)

    return pd.DataFrame(rows)

def fnc_side(round_, fnc_team_id):
    if round_["winner_team_id"] == fnc_team_id:
        return round_["winner_side"]
    else:
        return "Defender" if round_["winner_side"] == "Attacker" else "Attacker"