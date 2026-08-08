import pandas as pd 
from hierarchical_map_model_sketch import fit_global, fit_per_map_jeffreys, estimate_hyperprior, fit_per_map_final

def test_stage_a(): 

    data = pd.DataFrame([
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Ascent", "wins": 8, "losses": 2},
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Bind",   "wins": 3, "losses": 7},
    ])

    result_df = fit_per_map_jeffreys(data) 

    result_dict = {
        (row.map_name):
        (
            round(row.theta_i, 4), 
            round(row.v_i, 4) 
        )
        for row in result_df.itertuples()
    }

    assert result_dict == {
        ("Ascent") : (0.7727, 0.0146),
        ("Bind") : (0.3182, 0.0181)
    }

    print (result_df)


def test_stage_b():

    data = pd.DataFrame([
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Ascent", "wins": 8, "losses": 2},
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Bind",   "wins": 3, "losses": 7},
    ])

    global_post = fit_global(data)
    stage_a_df = fit_per_map_jeffreys(data)
    stage_b_df = estimate_hyperprior(stage_a_df,global_post)

    assert round(stage_b_df.loc[(1, "Attacker"), "Q"], 3) == 6.316
    assert round(stage_b_df.loc[(1, "Attacker"), "tau2"], 3) == 0.087
    assert round(stage_b_df.loc[(1, "Attacker"), "p_hat_star"], 4) == 0.5492
    assert round(stage_b_df.loc[(1, "Attacker"), "M"], 4) == 1.8474 
    assert round(stage_b_df.loc[(1, "Attacker"), "alpha_hyper"], 4) == 1.0146
    assert round(stage_b_df.loc[(1, "Attacker"), "beta_hyper"], 4) == 0.8327
    assert stage_b_df.loc[(1, "Attacker"), "tau2_clipped"] == False

def test_stage_c(): 

    data = pd.DataFrame([
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Ascent", "wins": 8, "losses": 2},
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Bind",   "wins": 3, "losses": 7},
    ])

    global_post = fit_global(data)
    stage_a_df = fit_per_map_jeffreys(data)
    stage_b_df = estimate_hyperprior(stage_a_df, global_post)

    stage_c_df = fit_per_map_final(stage_a_df, stage_b_df) 

    print(stage_c_df)

    result_dict = {
        (row.map_name):
        (
            round(row.alpha_final,3),
            round(row.beta_final,3), 
            round(row.posterior_mean,3)
        )
        for row in stage_c_df.itertuples()
    }

    assert result_dict == { 
        ("Ascent") : (9.015, 2.833, 0.761),
        ("Bind") : (4.015, 7.833, 0.339)
    }

