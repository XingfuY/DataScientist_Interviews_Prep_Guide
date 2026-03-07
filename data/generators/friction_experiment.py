"""Synthetic data generator for a friction warning A/B test experiment.

Generates user-level data for a large-scale friction intervention where
treatment users receive an interstitial warning before posting content that
a lightweight classifier flags as potentially violating.  Designed for
CUPED variance reduction analysis with pre-experiment covariates and
heterogeneous treatment effects across regions and content types.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REGIONS = ["US", "EU", "SEA", "LATAM"]
_REGION_WEIGHTS = [0.35, 0.25, 0.25, 0.15]

_CONTENT_TYPES = ["video", "live", "comment"]
_CONTENT_TYPE_WEIGHTS = [0.55, 0.15, 0.30]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assign_covariates(rng: np.random.Generator, n: int) -> dict:
    """Generate user-level covariates shared across treatment arms."""
    region = rng.choice(_REGIONS, size=n, p=_REGION_WEIGHTS)
    content_type_primary = rng.choice(
        _CONTENT_TYPES, size=n, p=_CONTENT_TYPE_WEIGHTS
    )
    account_age_days = rng.lognormal(mean=5.8, sigma=1.1, size=n).astype(int)
    account_age_days = np.clip(account_age_days, 7, 3650)

    follower_count = np.maximum(
        0, np.round(np.exp(rng.normal(6.0, 2.0, size=n)))
    ).astype(int)

    return {
        "region": region,
        "content_type_primary": content_type_primary,
        "account_age_days": account_age_days,
        "follower_count": follower_count,
    }


def _region_effect_multiplier(region: np.ndarray) -> np.ndarray:
    """Return per-user treatment effect multiplier based on region.

    SEA has the strongest effect, EU the weakest.
    """
    multipliers = {
        "US": 1.0,
        "EU": 0.6,
        "SEA": 1.5,
        "LATAM": 1.1,
    }
    return np.array([multipliers[r] for r in region])


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_friction_experiment(
    n_users: int = 50_000,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic data for a friction warning A/B test.

    Treatment users see a warning interstitial ("This may violate community
    guidelines") before their post is published when a lightweight classifier
    flags the content.  The experiment measures the trade-off between
    violation reduction and posting friction.

    Treatment effects (average):
        - Violation rate reduced by ~8 % relative.
        - Posting completion rate decreased by ~3 %.
    Heterogeneity:
        - Stronger violation reduction in SEA (~12 % relative).
        - Weaker violation reduction in EU (~5 % relative).

    Parameters
    ----------
    n_users : int
        Total number of users, split 50/50 between control and treatment.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        One row per user with columns:
        - user_id : int
        - treatment : int (0 = control, 1 = treatment)
        - pre_violation_rate : float (covariate for CUPED)
        - post_violations : int
        - post_content_count : int
        - post_violation_rate : float
        - warned_count : int (treatment only; 0 for control)
        - warning_dismissed : int (treatment only; 0 for control)
        - posting_completion_rate : float
        - days_active_post : int
        - region : str
        - content_type_primary : str
        - account_age_days : int
        - follower_count : int
    """
    rng = np.random.default_rng(seed)

    # --- Treatment assignment (balanced 50/50) ---
    treatment = np.zeros(n_users, dtype=int)
    treatment[: n_users // 2] = 1
    rng.shuffle(treatment)
    is_treat = treatment == 1

    covariates = _assign_covariates(rng, n_users)
    region = covariates["region"]
    account_age_days = covariates["account_age_days"]

    # --- Latent user propensity ---
    # Higher propensity -> more likely to post violating content
    user_propensity = rng.normal(0, 1, n_users)

    # --- Pre-experiment violation rate (CUPED covariate) ---
    # Correlated with latent propensity so CUPED can reduce variance
    pre_violation_rate = np.clip(
        0.04 + 0.015 * user_propensity + rng.normal(0, 0.01, n_users),
        0.005,
        0.25,
    )

    # --- Post-experiment content volume ---
    # Base posting volume: Poisson with mean influenced by account age
    age_factor = np.clip(np.log1p(account_age_days) / 8.0, 0.3, 1.5)
    base_content_count = rng.poisson(lam=25 * age_factor)
    base_content_count = np.maximum(base_content_count, 1)

    # --- Warning mechanism (treatment only) ---
    # Fraction of posts flagged for warning depends on user propensity
    flag_rate = np.clip(
        0.12 + 0.04 * user_propensity + rng.normal(0, 0.02, n_users),
        0.02,
        0.40,
    )

    warned_count = np.zeros(n_users, dtype=int)
    warned_count[is_treat] = rng.binomial(
        base_content_count[is_treat], flag_rate[is_treat]
    )

    # Warning dismissal: ~60 % of warnings are dismissed (user posts anyway)
    dismiss_rate = np.clip(rng.normal(0.60, 0.12, n_users), 0.20, 0.95)
    warning_dismissed = np.zeros(n_users, dtype=int)
    warning_dismissed[is_treat] = rng.binomial(
        warned_count[is_treat], dismiss_rate[is_treat]
    )

    # Posts abandoned due to warning
    posts_abandoned = warned_count - warning_dismissed

    # --- Posting completion ---
    # Total posts started = base_content_count for everyone
    # Posts completed = started - abandoned (treatment) or started (control)
    posts_started = base_content_count.copy()
    post_content_count = posts_started.copy()
    post_content_count[is_treat] = np.maximum(
        1, posts_started[is_treat] - posts_abandoned[is_treat]
    )

    # Posting completion rate
    posting_completion_rate = post_content_count / np.maximum(posts_started, 1)
    posting_completion_rate = np.round(np.clip(posting_completion_rate, 0.0, 1.0), 4)

    # --- Post-experiment violations ---
    # Base violation rate (post) correlated with pre-violation rate
    base_post_viol_rate = np.clip(
        pre_violation_rate + rng.normal(0, 0.005, n_users),
        0.005,
        0.25,
    )

    # Treatment effect on violation rate: ~8 % relative reduction on average
    # with regional heterogeneity
    region_mult = _region_effect_multiplier(region)
    # Base relative reduction for treatment is ~8 %
    relative_reduction = 0.08 * region_mult
    # Add individual-level noise
    individual_reduction = np.clip(
        relative_reduction + rng.normal(0, 0.02, n_users),
        0.0,
        0.30,
    )

    treat_post_viol_rate = base_post_viol_rate * (1.0 - individual_reduction)
    post_viol_rate = np.where(is_treat, treat_post_viol_rate, base_post_viol_rate)

    # Draw violation counts from Poisson
    post_violations = rng.poisson(
        lam=np.clip(post_viol_rate * post_content_count, 0.01, 100)
    )

    # Actual post violation rate (realised)
    post_violation_rate = np.round(
        post_violations / np.maximum(post_content_count, 1), 6
    )

    # --- Days active in post-experiment period ---
    # 28-day observation window; treatment may slightly reduce activity
    base_active = rng.binomial(28, np.clip(0.6 + 0.05 * age_factor, 0.2, 0.95))
    base_active = np.maximum(base_active, 1)
    # Treatment has negligible effect on days active (< 1 % reduction)
    days_active_post = base_active.copy()
    tiny_churn = rng.binomial(1, 0.008, n_users)
    days_active_post[is_treat] = np.maximum(
        1, days_active_post[is_treat] - tiny_churn[is_treat]
    )

    # --- Assemble DataFrame ---
    df = pd.DataFrame(
        {
            "user_id": np.arange(1, n_users + 1),
            "treatment": treatment,
            "pre_violation_rate": np.round(pre_violation_rate, 6),
            "post_violations": post_violations,
            "post_content_count": post_content_count,
            "post_violation_rate": post_violation_rate,
            "warned_count": warned_count,
            "warning_dismissed": warning_dismissed,
            "posting_completion_rate": posting_completion_rate,
            "days_active_post": days_active_post,
            "region": region,
            "content_type_primary": covariates["content_type_primary"],
            "account_age_days": account_age_days,
            "follower_count": covariates["follower_count"],
        }
    )
    return df


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating friction experiment data...\n")

    df = generate_friction_experiment()
    print(f"Shape: {df.shape[0]:,} rows, {df.shape[1]} cols\n")

    ctrl = df[df.treatment == 0]
    treat = df[df.treatment == 1]

    ctrl_vr = ctrl["post_violation_rate"].mean()
    treat_vr = treat["post_violation_rate"].mean()
    print(f"Post violation rate (control):   {ctrl_vr:.5f}")
    print(f"Post violation rate (treatment): {treat_vr:.5f}")
    print(f"Relative reduction:              {1 - treat_vr / ctrl_vr:.2%}")

    ctrl_pc = ctrl["posting_completion_rate"].mean()
    treat_pc = treat["posting_completion_rate"].mean()
    print(f"\nPosting completion (control):    {ctrl_pc:.4f}")
    print(f"Posting completion (treatment):  {treat_pc:.4f}")
    print(f"Absolute change:                 {treat_pc - ctrl_pc:.4f}")

    print("\nPre-violation rate correlation with post (CUPED check):")
    corr = df["pre_violation_rate"].corr(df["post_violation_rate"])
    print(f"  Pearson r = {corr:.3f}")

    print("\nRegional treatment effects (relative violation reduction):")
    for r in _REGIONS:
        c = ctrl[ctrl.region == r]["post_violation_rate"].mean()
        t = treat[treat.region == r]["post_violation_rate"].mean()
        print(f"  {r:>5s}: {1 - t / c:.2%}")

    print("\nDone.")
