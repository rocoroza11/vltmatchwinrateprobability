import vlrdevapi as vlr 

completed = vlr.matches.completed(team_id = 2593, limit=10)

teams = vlr.search.search_teams("sentinels")

team = vlr.teams.info(team_id=2593)
print(f"{team.name} ({team.tag}) - {team.country}")

for match in completed:
    score = f"{match.team1.score}-{match.team2.score}"
    print(f"{match.team1.name} vs {match.team2.name}: {score}")