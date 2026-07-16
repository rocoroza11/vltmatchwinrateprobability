from pipeline.pandasfile import load_rounds_dataframe
from models.pistol_round2 import pistol_round2_probabilities
from interface import file_load

from scipy.stats import beta
import pandas as pd


def beta_posterior(wins, losses, prior_alpha, prior_beta):

    alpha_post = prior_alpha + wins
    beta_post = prior_beta + losses
    
    return beta(alpha_post, beta_post)


def analyze_pistol_conversions(game_file, prior_alpha=None, prior_beta=None, n0=10):
    """
    Compute Beta posteriors for pistol-round -> round-2 conversion.

    game_file: path to the raw rounds JSON.
    prior_alpha, prior_beta: optional explicit prior. Must be supplied together.
        If omitted, a shrinkage prior is derived from the pooled global mean
        across all cells, weighted by n0 pseudo-observations.
    n0: pseudo-observation count for the derived shrinkage prior. Ignored if
        prior_alpha/prior_beta are supplied explicitly.

    Returns the result_dataframe enriched with wins, losses, prior_alpha,
    prior_beta, posterior mean, and 95% credible interval bounds/width.
    """

    file_loaded = file_load(game_file)
    if not file_loaded:
        raise FileNotFoundError(f"Could not load game file: {game_file}")

    rounds_df = load_rounds_dataframe(game_file)
    result_dataframe = pistol_round2_probabilities(rounds_df)

    wins = result_dataframe["n_win_round2"]
    losses = result_dataframe["n_pistol_wins"] - wins

    if (prior_alpha is None) != (prior_beta is None):
        raise ValueError("prior_alpha and prior_beta must be supplied together, or not at all.")

    if prior_alpha is None and prior_beta is None:
        total_wins = wins.sum()
        total_trials = (wins + losses).sum()
        global_mean = total_wins / total_trials

        prior_alpha = global_mean * n0
        prior_beta = (1 - global_mean) * n0

    posterior = beta_posterior(wins, losses, prior_alpha, prior_beta)

    result_dataframe["wins"] = wins
    result_dataframe["losses"] = losses
    result_dataframe["prior_alpha"] = prior_alpha
    result_dataframe["prior_beta"] = prior_beta
    result_dataframe["posterior_mean"] = posterior.mean()
    result_dataframe["ci_lower"] = posterior.ppf(0.025)
    result_dataframe["ci_upper"] = posterior.ppf(0.975)
    result_dataframe["ci_width"] = result_dataframe["ci_upper"] - result_dataframe["ci_lower"]

    return result_dataframe


if __name__ == "__main__":
    game_file = input("Enter filepath: ").strip()
    result_dataframe = analyze_pistol_conversions(game_file)
    print("The file loaded successfully.")
    print(result_dataframe)