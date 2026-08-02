"""
Sketch: per-map partial pooling on top of the existing pistol-round pipeline.

Idea
----
Fitting an independent Beta-Binomial per (pistol_round, side, map) cell fails
because most maps will only have a handful of pistol rounds in the dataset.
Instead of fully independent fits, we do a TWO-STAGE cascade:

  Stage 1 (what you already have): pool across all maps to get a global
           posterior for each (pistol_round, side) cell. This uses your
           existing weak prior (alpha=8.98, beta=1.02).

  Stage 2 (new): treat that GLOBAL posterior as the informative prior for
           each individual map, then update it with just that map's data.

This is mathematically just chained conjugate updating, but it behaves like
partial pooling: maps with few pistol rounds barely move away from the
global estimate (shrinkage ~0), maps with lots of rounds pull toward their
own empirical rate (shrinkage ~1). No MCMC required, fits directly on top
of what you already built.

Required input columns (extend your existing per-round table with map_name):
    pistol_round, fnc_side, map_name, wins, losses
"""

import pandas as pd
import numpy as np
from scipy.stats import beta as beta_dist

# Same weak prior you're already using for the pooled fit
GLOBAL_PRIOR_ALPHA = 8.983050847457628
GLOBAL_PRIOR_BETA = 1.0169491525423724


def fit_global(df, round_col="pistol_round", side_col="fnc_side",
               wins_col="wins", losses_col="losses"):
    """Stage 1 — identical to your current pooled fit. Ignores map_name."""
    grp = df.groupby([round_col, side_col])[[wins_col, losses_col]].sum()
    grp["alpha_post"] = GLOBAL_PRIOR_ALPHA + grp[wins_col]
    grp["beta_post"] = GLOBAL_PRIOR_BETA + grp[losses_col]
    return grp


def fit_per_map(df, global_post, map_col="map_name",
                round_col="pistol_round", side_col="fnc_side",
                wins_col="wins", losses_col="losses", ci=0.95):
    """
    Stage 2 — cascade the global posterior down as each map's prior.

    shrinkage_weight tells you how much a map's estimate reflects its own
    data vs the pooled global estimate:
        weight = n_map / (n_map + alpha0 + beta0)
    weight -> 0  : estimate is basically the global rate (map has ~no data)
    weight -> 1  : estimate is basically the map's raw empirical rate
    """
    lo_q, hi_q = (1 - ci) / 2, 1 - (1 - ci) / 2
    rows = []
    for (rnd, side), sub in df.groupby([round_col, side_col]):
        a0 = global_post.loc[(rnd, side), "alpha_post"]
        b0 = global_post.loc[(rnd, side), "beta_post"]
        for map_name, m in sub.groupby(map_col):
            w, l = m[wins_col].sum(), m[losses_col].sum()
            n_map = w + l
            a_post, b_post = a0 + w, b0 + l
            rows.append({
                "pistol_round": rnd,
                "fnc_side": side,
                "map_name": map_name,
                "n_map_pistols": n_map,
                "posterior_mean": a_post / (a_post + b_post),
                "ci_lower": beta_dist.ppf(lo_q, a_post, b_post),
                "ci_upper": beta_dist.ppf(hi_q, a_post, b_post),
                "shrinkage_weight": n_map / (n_map + a0 + b0),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Example usage:
#
#   per_round_map_df = pd.read_csv("per_round_per_map.csv")  # you'd build this
#   global_post = fit_global(per_round_map_df)
#   map_results = fit_per_map(per_round_map_df, global_post)
#   print(map_results.sort_values("shrinkage_weight", ascending=False))
#
# Read shrinkage_weight alongside posterior_mean: a map showing an extreme
# posterior_mean but with shrinkage_weight near 0 just means "don't trust
# this yet, we've barely seen it" -- exactly the failure mode naive per-map
# splitting hides.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# UPGRADE PATH: full hierarchical model (only if the cascade above feels too
# ad hoc, e.g. you want the between-map variance itself to be estimated
# rather than fixed by the global prior's concentration). Sketch with PyMC:
#
#   import pymc as pm
#
#   with pm.Model():
#       mu = pm.Normal("mu", 0, 1.5)              # global logit-scale rate
#       sigma_map = pm.HalfNormal("sigma_map", 1) # between-map spread
#       map_offset = pm.Normal("map_offset", 0, 1, shape=n_maps)
#       p = pm.Deterministic("p", pm.math.sigmoid(mu + sigma_map * map_offset))
#       pm.Binomial("obs", n=n_pistols_per_map, p=p[map_idx], observed=wins_per_map)
#       trace = pm.sample(2000, tune=1000, target_accept=0.9)
#
# This lets sigma_map be small if maps barely differ (pooling everything)
# or large if they genuinely diverge (pooling less) -- the cascade version
# above assumes a fixed amount of pooling instead of learning it. Worth
# doing only once you have enough maps (5+) with reasonable pistol counts
# each to actually estimate sigma_map sensibly.
# ---------------------------------------------------------------------------
