from __future__ import annotations

import datetime
from dataclasses import dataclass, field

import vlrdevapi as vlr
print(vlr.__version__)

# Optional: check site reachability (if using the status helper)
try:
    from vlrdevapi import status
    print(status.check_status())
except Exception:
    # status helper may not be available in all builds
    pass


@dataclass(frozen=True)
class TeamInfo:
    """Team information in a series."""

    name: str
    id: int | None = None
    short: str | None = None
    country: str | None = None
    country_code: str | None = None
    score: int | None = None

nrg = TeamInfo(
    name="NRG",
    id=123,
    short="NRG",
    country="United States",
    country_code="US",
    score=2
)

print(nrg)

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

