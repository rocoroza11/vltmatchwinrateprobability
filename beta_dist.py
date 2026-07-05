from pipeline.pandasfile import load_rounds_dataframe
from models.pistol_round2 import pistol_round2_probabilities

from scipy.stats import beta 
import pandas as pd 

json_file_loaded = ("rounds_raw.json")
rounds_df = load_rounds_dataframe(json_file_loaded)

result_dataframe = pistol_round2_probabilities(rounds_df)

wins = (result_dataframe["n_pistol_wins"]   * result_dataframe["p_win_round2_given_pistol"]).round().astype(int)
losses = (result_dataframe["n_pistol_wins"] - wins)

def beta_posterior(wins, losses, prior_alpha, prior_beta):

    alpha_post = prior_alpha + wins 
    beta_post = prior_beta + losses 

    return beta(alpha_post, beta_post)

posterior = beta_posterior(wins, losses, prior_alpha = 1 , prior_beta= 1 )


mean = posterior.mean()
ci_lower = posterior.ppf(0.025)
ci_upper = posterior.ppf(0.975)
ci_width = ci_upper - ci_lower
 
print(mean)
print(ci_lower)
print(ci_upper)
print(ci_width)
