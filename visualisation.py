import numpy as np 
import pandas as pd
from scipy.stats import beta 
import matplotlib.pyplot as plt 
from main import mc_draws


one_cell = mc_draws[(mc_draws["pistol_round"] == 1) & (mc_draws["fnc_side"] == "Attacker")]
values = one_cell["sampled_p"]
plt.hist(values, density=True)

x = np.linspace(0, 1, 200)
plt.plot(x, beta(18, 1).pdf(x))  

plt.show() 