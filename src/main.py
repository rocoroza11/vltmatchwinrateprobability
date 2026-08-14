import os 
import pandas as pd
from beta_dist import analyze_pistol_conversions, build_per_map_table, load_pistol_results
from hierarchical_map_model_sketch import fit_global, fit_per_map_jeffreys, estimate_hyperprior, fit_per_map_final
from montecarlo import simulate_round2_wins, melt_mc_draws, validate_mc_against_posterior, Pr1_Pr13
from interface import file_write
from visualisation import draw_dist

HERE = os.path.dirname(__file__)
game_file = os.path.join(HERE, "rounds_raw.json")

results_df = load_pistol_results(game_file)

beta_result = analyze_pistol_conversions(results_df) #beta-dist pipeline
per_map_df = build_per_map_table(results_df)   

global_post = fit_global(per_map_df) # Stage 0 
stage_a = fit_per_map_jeffreys(per_map_df) 
hyperprior = estimate_hyperprior(stage_a, global_post)

print(hyperprior["tau2_used"])
print(hyperprior["k"])
print(hyperprior["M"])

final_priors = fit_per_map_final(stage_a, hyperprior)

mc_result = simulate_round2_wins(beta_result) #monte-carlo pipeline
mc_draws = melt_mc_draws(mc_result)  #write results into cells 
res_tuple = Pr1_Pr13(mc_draws)

sanity_check = validate_mc_against_posterior(mc_draws, beta_result)

file_write(final_priors, "pistol_per_map_results.csv")
file_write(beta_result, "pistol_side_conditioned_results.csv")
file_write(mc_draws, "mc_draws.csv")
file_write(sanity_check, "sanity_check.csv")

print(f"The ATK-side and Def-side mean for Pr1_ Pr13 is {res_tuple}")
draw_dist(beta_result, mc_draws)
