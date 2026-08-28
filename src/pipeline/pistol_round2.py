import pandas as pd

PISTOL_ROUNDS = [1, 13]


def _pistol_round2_subset(rounds_df, pistol_round):

    """
    Reshapes rounds_df (rows = individual rounds) into one row per
    (match_id, map_name) with a won_pistol / won_round2 / fnc_side triple
    for the given pistol_round. Returns None if this pistol_round doesn't
    appear in the data (e.g. no overtime rounds for round 13).
    """

    round2 = pistol_round + 1

    # rows = (match_id, map_name), columns = round number, values = won_by_queried_team
    pivot = rounds_df.pivot_table(
        index=["match_id", "map_name"],
        columns="number",
        values="won_by_queried_team",
        aggfunc="first",
    )

    # same reshape, but tracking which side FNC was on for each round number
    side_pivot = rounds_df.pivot_table(
        index=["match_id", "map_name"],
        columns="number",
        values="fnc_side",
        aggfunc="first",
    )

    if pistol_round not in pivot.columns or round2 not in pivot.columns:
        return None

    # get only pistol round and 2nd round rows
    subset = pivot[[pistol_round, round2]].dropna()
    subset = subset.astype(bool)

    # categorise each element in each row by col
    subset = subset.rename(columns={pistol_round: "won_pistol", round2: "won_round2"})

    # attach the side FNC played on during the pistol round itself
    subset["fnc_side"] = side_pivot[pistol_round]
    subset = subset.dropna(subset=["fnc_side"])

    return subset.reset_index()


def _summarise(group):
    
    """Turn a subset of rows sharing a conditioning key into one result row."""

    pistol_wins = group[group["won_pistol"] == True]
    if len(pistol_wins) == 0:
        return None

    n_win_round2 = pistol_wins["won_round2"].sum()
    n_pistol_wins = len(pistol_wins)
    return {
        "n_pistol_wins": n_pistol_wins,
        "n_win_round2": n_win_round2,
        "p_win_round2_given_pistol": n_win_round2 / n_pistol_wins,
    }


def pistol_round2_probabilities(rounds_df):

    """
    Side+map conditioned: P(win round 2 | won pistol, side, map).
    pool_by_side() and split_by_map() project this single computation
    down to the side-only and per-map views respectively — this function
    is the one place rounds_df actually gets walked.
    """
    
    results = []
    for pistol_round in PISTOL_ROUNDS:
        subset = _pistol_round2_subset(rounds_df, pistol_round)
        if subset is None:
            continue

        for (side, map_name), group in subset.groupby(["fnc_side", "map_name"]):
            row = _summarise(group)
            if row is None:
                continue
            row.update({"pistol_round": pistol_round, "map_name": map_name, "fnc_side": side})
            results.append(row)

    return pd.DataFrame(results)

def pool_by_side(results_df):

    """
    Collapse the per-map rows from pistol_round2_probabilities() down to
    the 4 canonical (pistol_round x fnc_side) cells, by summing raw counts
    — never averaging rates. This is the side-only view: call as
    pool_by_side(pistol_round2_probabilities(rounds_df)).
    """

    pooled = (
        results_df
        .groupby(["pistol_round", "fnc_side"])[["n_pistol_wins", "n_win_round2"]]
        .sum()
        .reset_index()
    )
    pooled["p_win_round2_given_pistol"] = pooled["n_win_round2"] / pooled["n_pistol_wins"]
    return pooled

def split_by_map(results_df):
    
    """
    Reshape the per-map rows from pistol_round2_probabilities() into raw
    wins/losses per (pistol_round, fnc_side, map_name) cell — the format
    a Beta-Binomial fit expects (successes and trials), rather than the
    pre-divided p_win_round2_given_pistol rate.
    """

    out = results_df[["pistol_round", "fnc_side", "map_name", "n_pistol_wins", "n_win_round2"]].copy()
    out = out.rename(columns={"n_win_round2" : "wins"})
    out["losses"] = out["n_pistol_wins"] - out["wins"]
    return out[["pistol_round", "fnc_side", "map_name", "wins", "losses"]]