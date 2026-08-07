import os
from beta_dist import analyze_pistol_conversions
from montecarlo import simulate_round2_wins, melt_mc_draws, validate_mc_against_posterior, Pr1_Pr13
from interface import file_write
from visualisation import draw_dist

HERE = os.path.dirname(__file__)
game_file = os.path.join(HERE, "rounds_raw.json")

beta_result = analyze_pistol_conversions(game_file) #beta-dist pipeline
mc_result = simulate_round2_wins(beta_result) #monte-carlo pipeline
mc_draws = melt_mc_draws(mc_result)  #write results into cells 
res_tuple = Pr1_Pr13(mc_draws)

sanity_check = validate_mc_against_posterior(mc_draws, beta_result)

file_write(beta_result, "pistol_side_conditioned_results.csv")
file_write(mc_draws, "mc_draws.csv")
file_write(sanity_check, "sanity_check.csv")

print(f"The ATK-side and Def-side mean for Pr1_ Pr13 is {res_tuple}")
draw_dist(beta_result, mc_draws)
