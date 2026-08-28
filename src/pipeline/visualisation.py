import numpy as np 
import pandas as pd
from scipy.stats import beta 
import matplotlib.pyplot as plt 

def draw_dist(beta_result, mc_draws): #df

    fig, axes = plt.subplots(2, 2)  # 2x2 grid of Axes objects
    axes = axes.flatten()           # so you can index them 0,1,2,3 instead of [row][col]


    cells = mc_draws.groupby(["pistol_round", "fnc_side"])

    for ax, ((pistol_round, fnc_side), group) in zip(axes, cells):
        ax.hist(group["sampled_p"], density=True)

        cell_row = beta_result[
            (beta_result["pistol_round"] == pistol_round) &
            (beta_result["fnc_side"] == fnc_side)
        ]

        alpha = cell_row["alpha_post"].iloc[0]
        beta_param = cell_row["beta_post"].iloc[0]

        x = np.linspace(0, 1, 200)
        ax.plot(x, beta(alpha, beta_param).pdf(x))

        ax.set_title(f"Round {pistol_round}, {fnc_side}")

    plt.show()



