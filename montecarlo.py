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