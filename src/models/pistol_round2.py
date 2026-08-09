import pandas as pd

def pistol_round2_probabilities(rounds_df):
    # reshape: rows = (match_id, map_name), columns = round number, values = won_by_queried_team

    # pivot dataframe 
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

    results = []
    for pistol_round in [1, 13]:
        round2 = pistol_round + 1
        if pistol_round not in pivot.columns or round2 not in pivot.columns:
            continue

        # get only pistol round and 2nd round rows
        subset = pivot[[pistol_round, round2]].dropna()
        subset = subset.astype(bool) 

        # categorise each element in each row by col
        subset = subset.rename(columns={pistol_round: "won_pistol", round2: "won_round2"})

        # attach the side FNC played on during the pistol round itself
        subset["fnc_side"] = side_pivot[pistol_round]
        subset = subset.dropna(subset=["fnc_side"])

        subset = subset.reset_index()

        # condition on side: split the pistol-round cell in two

        # so group per side, like originally 
        for (side, map_name), group in subset.groupby(["fnc_side", "map_name"]):
            
            pistol_wins = group[group["won_pistol"] == True]
            if len(pistol_wins) == 0:
                continue
#

            # nest a groupby().sum() here? 
            n_win_round2 = pistol_wins["won_round2"].sum()
            n_pistol_wins = len(pistol_wins)

            results.append({
                "pistol_round": pistol_round,
                "map_name" : map_name,
                "fnc_side": side,
                "n_pistol_wins": n_pistol_wins,
                "n_win_round2": n_win_round2,
                "p_win_round2_given_pistol": n_win_round2 / n_pistol_wins
            })

            results_df = pd.DataFrame(results)
            
    return results_df

def pool_by_side(results_df):
    """
        Collapse the per-map diagnostic rows into the 4 canonical cells
        (pistol_round x fnc_side), by summing raw counts — never averaging rates.
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
    splits by map (help me write something more accurate here)
    """

    out = results_df[["pistol_round", "fnc_side", "map_name", "n_pistol_wins", "n_win_round2"]].copy()
    out = out.rename(columns={"n_win_round2" : "wins"})
    out["losses"] = out["n_pistol_wins"] - out["wins"]
    return out[["pistol_round", "fnc_side", "map_name", "wins", "losses"]]