from beta_dist import beta_posterior

"""
Per-map partial pooling on top of the existing pistol-round pipeline.

Symbols below match project_notes_map_pooling.md exactly -- check there if
a name looks unfamiliar. In short: theta_i/v_i (per-map), p_hat (naive,
intermediate only), tau2, p_hat_star (the real pooled mean, formerly
called theta_RE), M/alpha_hyper/beta_hyper (the hyperprior).

Pipeline (three stages):
    Stage A: fit_per_map_jeffreys   -> per-map theta_i, v_i (Jeffreys prior)
    Stage B: estimate_hyperprior    -> per-cell tau2, p_hat_star, hyperprior
    Stage C: fit_per_map_final      -> per-map final Beta posterior

fit_global (Stage-0, no map conditioning) is UNCHANGED from before -- kept
as the existing baseline for comparison, not touched by any of this.

Required input columns (per-round-per-map table you build upstream):
    pistol_round, fnc_side, map_name, wins, losses

Open items not yet resolved here (see project_notes_map_pooling.md Sec 4):
    - min-k gate is a soft FLAG only right now, not a suppression
    - tau2==0 fallback: uses fit_global's posterior for that cell (one
      option from the notes doc -- revisit if a different fallback is
      preferred)
    - tau2 > ceiling fallback: clips tau2 just under the ceiling and flags
      the row; does not silently produce invalid negative alpha/beta
"""

import pandas as pd
import numpy as np
from scipy.stats import beta as beta_dist

# ---------------------------------------------------------------------------
# Stage 0 (existing, unchanged) -- plain (round, side) pooled fit, no map
# conditioning. Kept as the baseline everything else compares against.
# ---------------------------------------------------------------------------

GLOBAL_PRIOR_ALPHA = 8.983050847457628
GLOBAL_PRIOR_BETA = 1.0169491525423724


def fit_global(df, round_col="pistol_round", side_col="fnc_side",
               wins_col="wins", losses_col="losses"):
    
    """Identical to your current pooled fit. Ignores map_name."""
    grp = df.groupby([round_col, side_col])[[wins_col, losses_col]].sum()
    grp["alpha_post"] = GLOBAL_PRIOR_ALPHA + grp[wins_col]
    grp["beta_post"] = GLOBAL_PRIOR_BETA + grp[losses_col]
    return grp


# ---------------------------------------------------------------------------
# Stage A -- per-map Jeffreys fit. Replaces the old cascading fit_per_map.
# Jeffreys (0.5, 0.5) is used specifically because its posterior variance
# is never exactly zero, which the next stage's weights (1/v_i) require.
# ---------------------------------------------------------------------------

JEFFREYS_ALPHA = 0.5
JEFFREYS_BETA = 0.5


def fit_per_map_jeffreys(df, active_maps=None, map_col="map_name", round_col="pistol_round", side_col="fnc_side", wins_col="wins", losses_col="losses"):
    """
    Stage A: independent Jeffreys-prior fit per map, per (round, side) cell.

    active_maps: optional list/set of map names currently in competitive
    rotation. If given, retired maps are dropped before fitting -- their
    old-meta data shouldn't feed the current hyperprior. Newly-added maps
    need no special handling here; they're naturally down-weighted later
    by their own small sample size.

    Returns one row per (pistol_round, fnc_side, map_name) with raw counts
    kept alongside theta_i/v_i, per the "never reconstruct counts from a
    rate" rule.
    """
    work = df if active_maps is None else df[df[map_col].isin(active_maps)]

    rows = []
    for (rnd, side), sub in work.groupby([round_col, side_col]):
        for map_name, m in sub.groupby(map_col):
            wins_i = m[wins_col].sum()
            losses_i = m[losses_col].sum()

            a_i, b_i, posterior_i = beta_posterior(wins_i, losses_i, JEFFREYS_ALPHA, JEFFREYS_BETA)
            theta_i = posterior_i.mean()
            v_i = posterior_i.var()
            
            rows.append({
                "pistol_round": rnd,
                "fnc_side": side,
                "map_name": map_name,
                "wins_i": wins_i,
                "losses_i": losses_i,
                "n_i": wins_i + losses_i,
                "theta_i": theta_i,
                "v_i": v_i,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Stage B -- DerSimonian-Laird hyperprior estimation, per (round, side) cell.
# ---------------------------------------------------------------------------

def estimate_hyperprior(stage_a_df, global_post, min_k=5, round_col="pistol_round", side_col="fnc_side"):

    """
    Stage B: turn Stage A's per-map (theta_i, v_i) into ONE shared hyperprior
    per (round, side) cell, via DerSimonian-Laird tau2 estimation.

    global_post: the fit_global() output -- used as the tau2==0 fallback
    (see module docstring; this specific fallback choice is not finalized,
    revisit if needed).

    min_k: below this many maps in a cell, tau2 is flagged as unreliable
    (soft flag only -- row is still returned, just marked low_k_flag=True).
    """

    rows = []
    for (rnd, side), cell in stage_a_df.groupby([round_col, side_col]):
        theta = cell["theta_i"].to_numpy()
        v = cell["v_i"].to_numpy()
        k = len(cell)

        # --- naive (fixed-effect) pooling: intermediate only, feeds Q ---
        w = 1 / v
        p_hat = np.sum(w * theta) / np.sum(w)
        Q = np.sum(w * (theta - p_hat) ** 2)
        df_ = k - 1

        if df_ <= 0:
            # single map in this cell -- no basis for a tau2 estimate at all
            tau2 = 0.0
        else:
            C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
            tau2 = max(0.0, (Q - df_) / C) if C > 0 else 0.0

        # --- random-effects (final) pooling: the real pooled mean ---
        w_star = 1 / (v + tau2)
        p_hat_star = np.sum(w_star * theta) / np.sum(w_star)

        ceiling = p_hat_star * (1 - p_hat_star)
        tau2_clipped = False
        tau2_used = tau2

        g_alpha = global_post.loc[(rnd, side), "alpha_post"]
        g_beta = global_post.loc[(rnd, side), "beta_post"]

        if tau2 == 0.0:

            # No detectable between-map heterogeneity. M is undefined
            # (division by zero) -- fall back to fit_global's posterior
            # for this cell as the hyperprior. See module docstring: this
            # fallback choice is one option from the notes, not finalized.

            alpha_hyper, beta_hyper = g_alpha, g_beta
            M = alpha_hyper + beta_hyper
        else:
            if tau2 >= ceiling:
                tau2_used = 0.999 * ceiling
                tau2_clipped = True
            M = p_hat_star * (1 - p_hat_star) / tau2_used - 1
            alpha_hyper = p_hat_star * M
            beta_hyper = (1 - p_hat_star) * M

        rows.append({
            "pistol_round": rnd,
            "fnc_side": side,
            "k": k,
            "df": df_,
            "Q": Q,
            "tau2": tau2,
            "tau2_used": tau2_used,
            "tau2_clipped": tau2_clipped,
            "p_hat_star": p_hat_star,
            "M": M,
            "alpha_hyper": alpha_hyper,
            "beta_hyper": beta_hyper,
            "low_k_flag": k < min_k,
        })

    return pd.DataFrame(rows).set_index([round_col, side_col])


# ---------------------------------------------------------------------------
# Stage C -- final per-map posterior, using the Stage B hyperprior.
# ---------------------------------------------------------------------------

def fit_per_map_final(stage_a_df, hyperprior_df, ci=0.95, round_col="pistol_round", side_col="fnc_side"):

    """
    Stage C: ordinary conjugate update per map, using the SHARED hyperprior
    from Stage B as the prior, and that map's own raw wins_i/losses_i as
    the data. This -- not the BLUP formula -- is the actual final per-map
    number that should feed montecarlo.py / visualize.py.
    """

    lo_q, hi_q = (1 - ci) / 2, 1 - (1 - ci) / 2
    rows = []
    for _, row in stage_a_df.iterrows():
        key = (row[round_col], row[side_col])
        h = hyperprior_df.loc[key]

        alpha_hyper = h["alpha_hyper"]
        beta_hyper = h["beta_hyper"]
        wins_i = row["wins_i"]
        losses_i = row["losses_i"]

        a_final, b_final, posterior_i = beta_posterior(wins_i, losses_i, alpha_hyper, beta_hyper)
        posterior_mean = posterior_i.mean()

        rows.append({
            "pistol_round": row[round_col],
            "fnc_side": row[side_col],
            "map_name": row["map_name"],
            "n_i": row["n_i"],
            "alpha_final": a_final,
            "beta_final": b_final,
            "posterior_mean": posterior_mean,
            "ci_lower": beta_dist.ppf(lo_q, a_final, b_final),
            "ci_upper": beta_dist.ppf(hi_q, a_final, b_final),
            "low_k_flag": h["low_k_flag"],
            "tau2_clipped": h["tau2_clipped"],
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Example usage:
#
#   per_round_map_df = pd.read_csv("per_round_per_map.csv")
#   global_post   = fit_global(per_round_map_df)
#   stage_a       = fit_per_map_jeffreys(per_round_map_df, active_maps=ACTIVE_MAPS)
#   hyperprior    = estimate_hyperprior(stage_a, global_post)
#   final_results = fit_per_map_final(stage_a, hyperprior)
#
# Read low_k_flag and tau2_clipped alongside posterior_mean -- either one
# being True means "treat this cell's map-level split with extra caution,"
# the same spirit as ci_width flagging thin cells elsewhere in the pipeline.
# ---------------------------------------------------------------------------
