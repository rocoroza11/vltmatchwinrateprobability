import vlrdevapi as vlr 
import json 

completed = vlr.teams.completed_matches(team_id = 2593, limit=10)

team = vlr.teams.info(team_id=2593)
print(f"{team.name} ({team.tag}) - {team.country}")

matches = []
for match in completed:
    team1 = match.team1.name
    team2 = match.team2.name
    score = f"{match.team1.score}-{match.team2.score}"
    matches.append({
        "team1": team1,
        "team2": team2,
        "score": score
    })

output = {
    "team_id": 2593,
    "team_name": team.name,
    "team_tag": team.tag,
    "country": team.country,
    "matches": matches
}

with open("matches.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(matches)} matches to matches.json")

