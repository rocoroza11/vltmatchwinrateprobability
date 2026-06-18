from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Literal

import vlrdevapi as vlr
print(vlr.__version__)

# Optional: check site reachability (if using the status helper)
try:
    from vlrdevapi import status
    print(status.check_status())
except Exception:
    # status helper may not be available in all builds
    pass


results = vlr.search.search("nrg")
print(f"Found {results.total_results} results")

for team in results.teams: 
    status = "inactive" if team.is_inactive else "active"
    print(f"Team: {team.name} ({status}) - {team.country}")


@dataclass(frozen=True)
class TeamInfo:
    """Team information in a series."""

    name: str
    id: int | None = None
    short: str | None = None
    country: str | None = None
    country_code: str | None = None
    score: int | None = None


@dataclass(frozen=True)
class RoundResult:
    """Single round result."""

    number: int
    winner_side: str | None = None
    method: str | None = None
    score: tuple[int, int] | None = None
    winner_team_id: int | None = None
    winner_team_short: str | None = None
    winner_team_name: str | None = None

@dataclass(frozen=True)
class SearchSeriesResult:
    """Series search result."""

    series_id: int
    url: str
    name: str | None = None
    image_url: str | None = None
    result_type: Literal["series"] = "series"#

