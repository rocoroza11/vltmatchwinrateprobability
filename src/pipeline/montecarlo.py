from scipy.stats import beta
import numpy as np
import pandas as pd

def simulate_round2_wins(result_dataframe, n_trials=10_000, random_state=None):

    """
    For each cell (row) in result_dataframe, draw n_trials samples from its
    posterior Beta(alpha_post, beta_post), then simulate a round-2 win/loss
    per trial using that sampled probability.

    Returns result_dataframe with an added 'simulated_p_win_round2' column
    containing an (n_trials,) array of sampled win probabilities per cell.
    """
    
    rng = np.random.default_rng(random_state)

    simulated = []
    for _, row in result_dataframe.iterrows():
        p_samples = beta(row["alpha_post"], row["beta_post"]).rvs(
            size=n_trials, random_state=rng
        )
        simulated.append(p_samples)

    result_dataframe = result_dataframe.copy()
    result_dataframe["simulated_p_win_round2"] = simulated
    
    return result_dataframe


def melt_mc_draws(mc_result, id_cols=("pistol_round", "fnc_side"), value_col="simulated_p_win_round2"):
    """
    Explode the per-cell array of Monte Carlo draws into long format:
    one row per (id_cols..., trial_id, sampled_p).

    Only id_cols + value_col are carried through -- posterior parameters
    (prior_alpha, alpha_post, ci_width, etc.) are intentionally dropped here;
    join back to beta_result on id_cols if they're needed alongside a draw.
    """
    
    id_cols = list(id_cols)
    n_trials = len(mc_result[value_col].iloc[0])

    lengths = mc_result[value_col].apply(len)
    if not (lengths == n_trials).all():
        raise ValueError(f"Inconsistent draw counts per cell: {lengths.unique()}")

    narrow = mc_result[id_cols + [value_col]].copy()
    narrow["trial_id"] = [list(range(n_trials))] * len(narrow)

    long_df = narrow.explode([value_col, "trial_id"], ignore_index=True)
    long_df["trial_id"] = long_df["trial_id"].astype(int)
    long_df = long_df.rename(columns={value_col: "sampled_p"})

    return long_df[id_cols + ["trial_id", "sampled_p"]]


def validate_mc_against_posterior(mc_draws, beta_result): 
    id_cols = ["pistol_round", "fnc_side"]

    empirical = (
        mc_draws.groupby(id_cols)["sampled_p"]
        .agg(
            mc_mean="mean",
            mc_ci_lower=lambda s: s.quantile(0.025),
            mc_ci_upper=lambda s: s.quantile(0.975),
        )
        .reset_index()
    )

    comparison = beta_result[id_cols + ["posterior_mean", "ci_lower", "ci_upper"]].merge(
        empirical, on=id_cols
    )

    comparison["mean_diff"] = comparison["mc_mean"] - comparison["posterior_mean"]
    comparison["ci_lower_diff"] = comparison["mc_ci_lower"] - comparison["ci_lower"]
    comparison["ci_upper_diff"] = comparison["mc_ci_upper"] - comparison["ci_upper"]

    return comparison



"""Mechanically it's simple given what you already have: 
- draw n_trials samples from Beta(alpha_post_r1, beta_post_r1), 
- draw the same count from Beta(alpha_post_r13, ...), 
-then (samples_r1 > samples_r13).mean(). """

# take a random sample of 10k from round 1->2 and round 13->14 (from the dataframe i presume)
# take the mean of all round 1 samples and mean of all round 13 samples and compare (?)
# or do a direct 1:1 comparison 
# return a dataframe of the results 

def Pr1_Pr13(mc_result):
    # Filter sides
    atk_side = mc_result[mc_result["fnc_side"] == "Attacker"]
    def_side = mc_result[mc_result["fnc_side"] == "Defender"]

    # Merge round 1 and round 13 on trial_id
    atk_merged = pd.merge(
        atk_side[atk_side["pistol_round"] == 1],
        atk_side[atk_side["pistol_round"] == 13],
        on="trial_id",
        suffixes=("_r1", "_r13")
    )
    atk_result = (atk_merged["sampled_p_r1"] > atk_merged["sampled_p_r13"]).mean()

    def_merged = pd.merge(
        def_side[def_side["pistol_round"] == 1],
        def_side[def_side["pistol_round"] == 13],
        on="trial_id",
        suffixes=("_r1", "_r13")
    )
    def_result = (def_merged["sampled_p_r1"] > def_merged["sampled_p_r13"]).mean()

    return atk_result, def_result

