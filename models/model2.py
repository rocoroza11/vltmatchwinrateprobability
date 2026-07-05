##INCOMPLETE## 

import pandas as pd 

def pistol_round2_half_probabilities(rounds_df): 

    pivot = rounds_df.pivot_table(
        index=["match_id", "map_name"],
        columns = "number",
        values = "won_by_queried_team",
    )

    results = [] 
    for pistol_round in [1,13]: 
        round2 = pistol_round + 1
        if pistol_round not in pivot.columns or round2 not in pivot.columns:
            continue 

        