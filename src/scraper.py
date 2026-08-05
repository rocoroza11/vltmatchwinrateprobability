import vlrdevapi as vlr
import json
from dataclasses import asdict

team_id = 2593

team = vlr.teams.info(team_id=team_id)
completed = vlr.teams.completed_matches(team_id=team_id, limit=12)

matches_data = []
for match in completed:
    if not match.match_id:
        continue

    maps = vlr.series.matches(series_id=match.match_id)
    maps_data = []
    for map_data in maps:
        rounds_data = [asdict(r) for r in map_data.rounds] if map_data.rounds else []
        maps_data.append({
            "map_name": map_data.map_name,
            "rounds": rounds_data,
        })

    matches_data.append({
        "match_id": match.match_id,
        "team1": match.team1.name,
        "team2": match.team2.name,
        "maps": maps_data,
    })

output = {
    "team_id": team_id,
    "team_name": team.name,
    "team_tag": team.tag,
    "country": team.country,
    "matches": matches_data,
}

with open("rounds_raw.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(matches_data)} matches with round data to rounds_raw.json")