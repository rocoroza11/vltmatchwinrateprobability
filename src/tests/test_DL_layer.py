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

"""
Tau2=0 forcing fixture -- companion to the canonical Ascent/Bind fixture,
exercises the fit_global() fallback branch in estimate_hyperprior()
instead of the moment-inversion branch.

Two maps, same pistol_round/side, deliberately near-identical raw win
rates (0.8 vs 0.8) so between-map dispersion (Q) can't clear the df
floor -- tau2 collapses to 0.0 and the cell falls back to fit_global's
posterior as its hyperprior, per the module docstring's documented
fallback behavior.

Expected (hand-verified against fit_global(per_map_df) directly):
    tau2 == 0.0
    alpha_hyper == global_post.loc[(1, "Attacker"), "alpha_post"]  == 20.983050847457626
    beta_hyper  == global_post.loc[(1, "Attacker"), "beta_post"]   ==  4.016949152542372
"""


def test_tau2_zero():

    EXPECTED_TAU2 = 0.0
    EXPECTED_ALPHA_HYPER = 20.983050847457626
    EXPECTED_BETA_HYPER = 4.016949152542372
    
    data = pd.DataFrame([
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Ascent", "wins": 8, "losses": 2},  # rate 0.800, n=10
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Bind",   "wins": 4, "losses": 1},  # rate 0.800, n=5
    ])

    global_post = fit_global(data)
    stage_a_df = fit_per_map_jeffreys(data)
    stage_b_df = estimate_hyperprior(stage_a_df, global_post)

    print(stage_b_df["tau2"])
    tau2_val = stage_b_df.loc[(1, "Attacker"), "tau2"]
    assert tau2_val == EXPECTED_TAU2

    assert round(stage_b_df.loc[(1, "Attacker"), "alpha_hyper"], 6) == round(EXPECTED_ALPHA_HYPER, 6)
    assert round(stage_b_df.loc[(1, "Attacker"), "beta_hyper"], 6) == round(EXPECTED_BETA_HYPER, 6)

    stage_c_df = fit_per_map_final(stage_a_df, stage_b_df) 

    result_dict = {
        row.map_name: (round(row.alpha_final, 4), round(row.beta_final, 4))
        for row in stage_c_df.itertuples()
    }

    assert tau2_val == EXPECTED_TAU2

    assert result_dict == {
        ("Ascent") : (28.9831, 6.0169),
        ("Bind") : (24.9831, 5.0169)
    }

"""
Tau2 >= ceiling forcing fixture -- exercises the clipping branch in
estimate_hyperprior(): two maps with tight individual precision (large n)
but extreme, opposite raw rates, so the DL tau2 estimate overshoots what
p_hat_star's own variance ceiling (p*(1-p)) can support.
 
Expected (hand-verified):
    tau2 ~= 0.396515          (uncapped DL estimate)
    ceiling == 0.25            (p_hat_star lands at exactly 0.5 here)
    tau2 >= ceiling  -> True   (clipping branch triggers)
    tau2_used ~= 0.24975       (0.999 * ceiling)
    alpha_hyper ~= 0.000501, beta_hyper ~= 0.000501  (near-flat hyperprior --
        maps disagree so much the shared prior barely constrains either one)
"""


def test_tau_above_ceiling():

    EXPECTED_TAU2_UNCLIPPED = 0.39651509559808623
    EXPECTED_P_HAT_STAR = 0.5
    EXPECTED_CEILING = 0.25
    EXPECTED_TAU2_USED = 0.24975

    data = pd.DataFrame([
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Ascent", "wins": 95, "losses": 5},  # rate 0.95, n=100
        {"pistol_round": 1, "fnc_side": "Attacker", "map_name": "Bind",   "wins": 5,  "losses": 95},  # rate 0.05, n=100
    ])

    global_post = fit_global(data)
    stage_a_df = fit_per_map_jeffreys(data)
    stage_b_df = estimate_hyperprior(stage_a_df, global_post)

    tau2_val = stage_b_df.loc[(1, "Attacker"), "tau2"]
    p_hat_star_val = stage_b_df.loc[(1, "Attacker"), "p_hat_star"]
    ceiling_val = p_hat_star_val * (1 - p_hat_star_val)

    assert round(tau2_val, 6) == round(EXPECTED_TAU2_UNCLIPPED, 6)
    assert round(p_hat_star_val, 6) == EXPECTED_P_HAT_STAR
    assert round(ceiling_val, 6) == EXPECTED_CEILING
    assert tau2_val >= ceiling_val

    assert stage_b_df.loc[(1, "Attacker"), "tau2_clipped"] == True
    assert round(stage_b_df.loc[(1, "Attacker"), "tau2_used"], 6) == round(EXPECTED_TAU2_USED, 6)
    
    print(stage_b_df)
    print(tau2_val)
    print(p_hat_star_val)
    print(ceiling_val)

