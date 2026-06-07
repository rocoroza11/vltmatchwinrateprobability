import vlrdevapi as vlr
print(vlr.__version__)

# Optional: check site reachability (if using the status helper)
try:
    from vlrdevapi import status
    print(status.check_status())
except Exception:
    # status helper may not be available in all builds
    pass

# Get next 5 upcoming matches
matches = vlr.matches.upcoming(limit=5)

for m in matches:
    print(f"{m.event} - {m.event_phase}")
    print(f"  {m.team1.name} vs {m.team2.name}")
    print(f"  Time: {m.time}")

    