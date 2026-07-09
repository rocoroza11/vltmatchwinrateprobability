from pipeline.pandasfile import load_rounds_dataframe
from models.pistol_round2 import pistol_round2_probabilities
from interface import file_load

from scipy.stats import beta 
import pandas as pd 

game_file = input("Enter filepath: ").strip()
file_content, file_loaded = file_load(game_file)
 
if not file_loaded:
    raise FileNotFoundError(f"Could not load game file: {game_file}")
 
rounds_df = load_rounds_dataframe(game_file)
print("The file loaded successfully.")
 
result_dataframe = pistol_round2_probabilities(rounds_df)

wins = (result_dataframe["n_pistol_wins"]  * result_dataframe["p_win_round2_given_pistol"]).round().astype(int)
losses = (result_dataframe["n_pistol_wins"] - wins)

total_wins = wins.sum()
total_trials = (wins + losses).sum()
global_mean = total_wins / total_trials

n0 = 10
prior_alpha = global_mean * n0
prior_beta = (1 - global_mean) * n0

def beta_posterior(wins, losses, prior_alpha, prior_beta):

    alpha_post = prior_alpha + wins 
    beta_post = prior_beta + losses 

    return beta(alpha_post, beta_post)

posterior = beta_posterior(wins, losses, prior_alpha, prior_beta)

print(wins)
print(losses)

print(prior_alpha)
print(prior_beta)

mean = posterior.mean()
ci_lower = posterior.ppf(0.025)
ci_upper = posterior.ppf(0.975)
ci_width = ci_upper - ci_lower


print(mean)
print(ci_lower)
print(ci_upper)
print(ci_width)
