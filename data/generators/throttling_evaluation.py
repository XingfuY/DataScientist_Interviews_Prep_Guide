"""Synthetic data generator for seller throttling causal inference analysis.

Generates panel data (seller x week) for a marketplace throttling scenario
where bad sellers are throttled after a policy change at week 26.  The data
supports difference-in-differences (DID), regression discontinuity design
(RDD), and seller displacement analysis.

All data is synthetic.  Seeds are fixed for reproducibility.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REGIONS = ["US", "EU", "SEA", "LATAM"]
_REGION_WEIGHTS = [0.30, 0.25, 0.25, 0.20]

_SELLER_CATEGORIES = [
    "electronics", "fashion", "home_garden", "health_beauty",
    "sports", "toys", "automotive",
]
_CATEGORY_WEIGHTS = [0.20, 0.25, 0.15, 0.15, 0.10, 0.08, 0.07]

_THROTTLE_WEEK = 26
_RISK_THRESHOLD = 0.7


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_risk_scores(rng: np.random.Generator, n: int) -> np.ndarray:
    """Generate risk scores with a density suitable for RDD analysis.

    Creates a bimodal distribution with a clear density discontinuity
    around the threshold (0.7).  Good sellers cluster in [0.0, 0.5]
    and bad sellers cluster in [0.6, 1.0], with enough density near
    the cutoff for local polynomial RDD estimation.
    """
    # Mixture of two Beta distributions
    # Component 1 (good sellers): Beta(2, 5) -> mode near 0.2
    # Component 2 (bad sellers):  Beta(5, 2) -> mode near 0.8
    mix_prob = rng.random(n)
    good_scores = rng.beta(2, 5, size=n)
    bad_scores = rng.beta(5, 2, size=n)

    # 25 % of sellers are inherently "bad"
    risk_score = np.where(mix_prob < 0.75, good_scores, bad_scores)

    # Add noise near the threshold to ensure density around cutoff
    near_threshold = np.abs(risk_score - _RISK_THRESHOLD) < 0.15
    risk_score[near_threshold] += rng.normal(0, 0.03, near_threshold.sum())
    risk_score = np.clip(risk_score, 0.0, 1.0)

    return np.round(risk_score, 4)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_throttling_data(
    n_sellers: int = 10_000,
    n_time_periods: int = 52,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate panel data for a seller throttling causal inference study.

    Sellers are observed weekly over ``n_time_periods`` weeks.  At week 26,
    sellers with ``risk_score > 0.7`` are throttled (reduced marketplace
    visibility and transaction limits).

    Treatment effects:
        - GMV decreases ~25 % for throttled bad sellers.
        - Dispute rate decreases ~20 % for throttled bad sellers.

    The pre-treatment period exhibits approximately parallel trends between
    bad and good sellers (suitable for DID).  The risk score distribution
    has a density discontinuity suitable for RDD analysis.

    A small fraction of throttled sellers create new accounts, modeled
    as new seller entries appearing after week 26 (for displacement analysis).

    Parameters
    ----------
    n_sellers : int
        Number of original sellers.
    n_time_periods : int
        Number of weekly observation periods (1 through ``n_time_periods``).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        One row per seller-week with columns:
        - seller_id : str
        - week : int (1 to n_time_periods)
        - is_bad_seller : bool (risk_score > 0.7)
        - risk_score : float (0-1, continuous)
        - throttled : bool (risk_score > 0.7 and week > 26)
        - gmv : float (gross merchandise value)
        - dispute_rate : float (fraction of orders disputed)
        - return_rate : float (fraction of orders returned)
        - review_sentiment : float (0-5 scale)
        - new_listings_count : int
        - buyer_satisfaction_score : float (0-10 scale)
        - region : str
        - seller_category : str
    """
    rng = np.random.default_rng(seed)

    # --- Seller-level attributes (time-invariant) ---
    seller_ids = np.array([f"S{i:05d}" for i in range(1, n_sellers + 1)])
    risk_scores = _generate_risk_scores(rng, n_sellers)
    is_bad = risk_scores > _RISK_THRESHOLD
    regions = rng.choice(_REGIONS, size=n_sellers, p=_REGION_WEIGHTS)
    categories = rng.choice(
        _SELLER_CATEGORIES, size=n_sellers, p=_CATEGORY_WEIGHTS
    )

    # Seller-level latent quality (affects all outcomes)
    seller_quality = rng.normal(0, 1, n_sellers)

    # Base GMV per week (log-normal, varies by seller)
    base_log_gmv = 7.5 + 0.5 * seller_quality - 0.8 * risk_scores
    base_gmv_sigma = 0.3

    # --- Build panel ---
    records = []
    for week in range(1, n_time_periods + 1):
        is_post_throttle = week > _THROTTLE_WEEK
        throttled = is_bad & is_post_throttle

        # --- GMV ---
        # Shared time trend (slight upward drift)
        time_trend = 0.003 * (week - 1)
        # Seasonal effect (Q4 bump)
        seasonal = 0.05 * np.sin(2 * np.pi * (week - 40) / 52)

        log_gmv = (
            base_log_gmv
            + time_trend
            + seasonal
            + rng.normal(0, base_gmv_sigma, n_sellers)
        )

        # Treatment effect: ~25 % GMV reduction for throttled sellers
        # Gradual ramp: full effect by 4 weeks after throttle start
        if is_post_throttle:
            weeks_since_throttle = week - _THROTTLE_WEEK
            ramp = min(1.0, weeks_since_throttle / 4.0)
            # On log scale: log(1 - 0.25) ~ -0.29
            gmv_reduction = -0.29 * ramp
            # Add individual-level noise to treatment effect
            individual_reduction = gmv_reduction + rng.normal(
                0, 0.05, n_sellers
            )
            log_gmv[throttled] += individual_reduction[throttled]

        gmv = np.round(np.exp(log_gmv), 2)
        gmv = np.maximum(0.0, gmv)

        # --- Dispute rate ---
        # Bad sellers have higher baseline dispute rate
        base_dispute = np.clip(
            0.03 + 0.06 * risk_scores + rng.normal(0, 0.008, n_sellers),
            0.005,
            0.25,
        )
        # Parallel trend component
        dispute_trend = base_dispute + 0.0002 * (week - 1)

        dispute_rate = dispute_trend.copy()
        if is_post_throttle:
            # Throttling reduces dispute rate by ~20 %
            dispute_reduction = 0.20 * ramp
            dispute_rate[throttled] *= (1.0 - dispute_reduction)
        dispute_rate = np.round(np.clip(dispute_rate, 0.0, 1.0), 4)

        # --- Return rate ---
        base_return = np.clip(
            0.05 + 0.04 * risk_scores + rng.normal(0, 0.01, n_sellers),
            0.01,
            0.30,
        )
        return_rate = base_return + 0.0001 * (week - 1)
        if is_post_throttle:
            # Slight decrease in return rate for throttled (fewer total sales)
            return_rate[throttled] *= (1.0 - 0.10 * ramp)
        return_rate = np.round(np.clip(return_rate, 0.0, 1.0), 4)

        # --- Review sentiment (0-5) ---
        base_sentiment = np.clip(
            3.8 - 1.2 * risk_scores + 0.3 * seller_quality
            + rng.normal(0, 0.3, n_sellers),
            0.0,
            5.0,
        )
        review_sentiment = base_sentiment + 0.001 * (week - 1)
        if is_post_throttle:
            # Throttled sellers: remaining transactions may be slightly
            # better quality (worst products removed)
            review_sentiment[throttled] += 0.15 * ramp
        review_sentiment = np.round(np.clip(review_sentiment, 0.0, 5.0), 2)

        # --- New listings count ---
        base_listings = rng.poisson(
            lam=np.clip(5 + 3 * seller_quality - 2 * risk_scores, 0.5, 20),
        )
        new_listings = base_listings.copy()
        if is_post_throttle:
            # Throttled sellers list fewer items
            listing_reduction = rng.binomial(
                new_listings[throttled],
                np.full(throttled.sum(), 0.40 * ramp),
            )
            new_listings[throttled] = np.maximum(
                0, new_listings[throttled] - listing_reduction
            )

        # --- Buyer satisfaction (0-10) ---
        base_satisfaction = np.clip(
            6.5 - 2.5 * risk_scores + 0.5 * seller_quality
            + rng.normal(0, 0.5, n_sellers),
            0.0,
            10.0,
        )
        buyer_satisfaction = base_satisfaction + 0.002 * (week - 1)
        if is_post_throttle:
            # Market-level improvement as bad sellers throttled
            buyer_satisfaction += 0.05 * ramp
            # Throttled sellers' remaining buyers slightly happier
            buyer_satisfaction[throttled] += 0.20 * ramp
        buyer_satisfaction = np.round(np.clip(buyer_satisfaction, 0.0, 10.0), 2)

        week_df = pd.DataFrame(
            {
                "seller_id": seller_ids,
                "week": week,
                "is_bad_seller": is_bad,
                "risk_score": risk_scores,
                "throttled": throttled,
                "gmv": gmv,
                "dispute_rate": dispute_rate,
                "return_rate": return_rate,
                "review_sentiment": review_sentiment,
                "new_listings_count": new_listings,
                "buyer_satisfaction_score": buyer_satisfaction,
                "region": regions,
                "seller_category": categories,
            }
        )
        records.append(week_df)

    df = pd.concat(records, ignore_index=True)

    # --- Displacement: new accounts from throttled sellers ---
    # ~5 % of throttled sellers create a new account post-throttle
    throttled_sellers = seller_ids[is_bad]
    n_displaced = max(1, int(len(throttled_sellers) * 0.05))
    displaced_original = rng.choice(throttled_sellers, size=n_displaced, replace=False)

    displacement_records = []
    for i, orig_id in enumerate(displaced_original):
        new_id = f"S{n_sellers + i + 1:05d}"
        # New account appears 2-10 weeks after throttle start
        start_week = _THROTTLE_WEEK + rng.integers(2, 11)
        if start_week > n_time_periods:
            continue

        # New accounts have artificially low risk scores initially
        new_risk = np.round(rng.uniform(0.1, 0.45), 4)
        new_region = rng.choice(_REGIONS, p=_REGION_WEIGHTS)
        new_category = rng.choice(_SELLER_CATEGORIES, p=_CATEGORY_WEIGHTS)
        new_quality = rng.normal(-0.5, 0.8)

        for week in range(start_week, n_time_periods + 1):
            weeks_active = week - start_week + 1
            # GMV ramps up as new account builds reputation
            ramp_factor = min(1.0, weeks_active / 8.0)
            log_gmv_new = (
                6.5 + 0.3 * new_quality + rng.normal(0, 0.3)
            ) * ramp_factor + 0.003 * (week - 1)
            gmv_new = round(max(0, np.exp(log_gmv_new)), 2)

            displacement_records.append(
                {
                    "seller_id": new_id,
                    "week": week,
                    "is_bad_seller": True,
                    "risk_score": new_risk,
                    "throttled": False,  # New account not yet flagged
                    "gmv": gmv_new,
                    "dispute_rate": round(
                        max(0, 0.06 + rng.normal(0, 0.01)), 4
                    ),
                    "return_rate": round(
                        max(0, 0.07 + rng.normal(0, 0.01)), 4
                    ),
                    "review_sentiment": round(
                        np.clip(3.2 + rng.normal(0, 0.3), 0, 5), 2
                    ),
                    "new_listings_count": max(
                        0, int(3 * ramp_factor + rng.poisson(2))
                    ),
                    "buyer_satisfaction_score": round(
                        np.clip(5.0 + rng.normal(0, 0.5), 0, 10), 2
                    ),
                    "region": new_region,
                    "seller_category": new_category,
                }
            )

    if displacement_records:
        df_displacement = pd.DataFrame(displacement_records)
        df = pd.concat([df, df_displacement], ignore_index=True)

    df = df.sort_values(["week", "seller_id"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating throttling evaluation data...\n")

    df = generate_throttling_data()
    n_sellers = df["seller_id"].nunique()
    n_weeks = df["week"].nunique()
    print(f"Shape: {df.shape[0]:,} rows, {df.shape[1]} cols")
    print(f"Sellers: {n_sellers:,}  |  Weeks: {n_weeks}")

    bad = df[df.is_bad_seller]
    good = df[~df.is_bad_seller]
    print(f"\nBad sellers:  {bad['seller_id'].nunique():,}")
    print(f"Good sellers: {good['seller_id'].nunique():,}")

    # Pre-throttle parallel trends
    pre = df[df.week <= 26]
    post = df[(df.week > 26) & (df.seller_id.str.startswith("S0"))]
    print("\nPre-throttle GMV trends (mean per week):")
    for label, subset in [("Bad", pre[pre.is_bad_seller]),
                          ("Good", pre[~pre.is_bad_seller])]:
        w1 = subset[subset.week <= 13]["gmv"].mean()
        w2 = subset[(subset.week > 13) & (subset.week <= 26)]["gmv"].mean()
        print(f"  {label}: weeks 1-13 = {w1:,.0f}, weeks 14-26 = {w2:,.0f}")

    # Treatment effects
    print("\nPost-throttle effects (weeks 30-52, original sellers):")
    post_late = post[post.week >= 30]
    for var in ["gmv", "dispute_rate"]:
        bad_val = post_late[post_late.is_bad_seller][var].mean()
        good_val = post_late[~post_late.is_bad_seller][var].mean()
        print(f"  {var}: bad = {bad_val:.4f}, good = {good_val:.4f}")

    # Displacement
    new_accounts = df[~df.seller_id.isin(
        [f"S{i:05d}" for i in range(1, 10001)]
    )]
    print(f"\nDisplacement accounts: {new_accounts['seller_id'].nunique()}")

    # RDD density around cutoff
    original = df[df.week == 1]
    near_cutoff = original[
        (original.risk_score >= 0.6) & (original.risk_score <= 0.8)
    ]
    print(f"Sellers near RDD cutoff (0.6-0.8): {len(near_cutoff):,}")

    print("\nDone.")
