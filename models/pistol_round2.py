import pandas as pd

def pistol_round2_probabilities(rounds_df):
    # reshape: rows = (match_id, map_name), columns = round number, values = won_by_queried_team

    # pivot dataframe 
    pivot = rounds_df.pivot_table(
        index=["match_id", "map_name"],
        columns="number",
        values="won_by_queried_team",
    )

    
    results = []
    for pistol_round in [1, 13]:
        round2 = pistol_round + 1
        if pistol_round not in pivot.columns or round2 not in pivot.columns:
            continue

        # get only pistol round and 2nd round rows
        subset = pivot[[pistol_round, round2]].dropna()

        # categorise each element in each row by col
        subset.columns = ["won_pistol", "won_round2"]

        # make column for won pistol rounds 
        pistol_wins = subset[subset["won_pistol"] == True]
        if len(pistol_wins) == 0:
            continue

        # append probabilistic columns to dataframe 
        results.append({
            "pistol_round": pistol_round,
            "n_pistol_wins": len(pistol_wins),
            "p_win_round2_given_pistol": pistol_wins["won_round2"].mean(),
        })

    return pd.DataFrame(results)

