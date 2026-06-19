import vlrdevapi as vlr

team_id = 2593  # FNATIC
matches = vlr.teams.completed_matches(team_id=team_id, limit=2)

for match in matches:
    print(f"\n=== {match.team1.name} vs {match.team2.name} (match_id={match.match_id}) ===")
    maps = vlr.series.matches(series_id=match.match_id)
    for map_data in maps:
        print(f"\n  Map: {map_data.map_name}")
        if map_data.rounds:
            for r in map_data.rounds[:3]:
                print(f"Round {r.number}: winner={r.winner_team_short}, method={r.method}, score={r.score}")
        else:
            print("No round data available")


            