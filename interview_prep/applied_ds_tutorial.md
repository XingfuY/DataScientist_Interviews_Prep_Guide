# Applied Data Science Tutorial — TikTok Integrity & Safety

> **Companion to**: `tiktok_integrity_safety.md` (main guide), `statistical_foundations.md`
>
> **Purpose**: Hands-on code-first walkthrough of every DS skill tested in the Peer (Round 1) interview.
> Each part follows: **Concept → TikTok Context → Code → Interview Tip**.
>
> **Prerequisites**: Python 3.10+, pandas, numpy, scipy, plotly, scikit-learn, xgboost, statsmodels

---

## Table of Contents

1. [Metric Definition & Decomposition](#part-1-metric-definition--decomposition)
2. [Data Collection & Quality](#part-2-data-collection--quality)
3. [Dashboarding](#part-3-dashboarding)
4. [A/B Testing Walkthrough](#part-4-ab-testing-walkthrough)
5. [Causal Inference Walkthrough](#part-5-causal-inference-walkthrough)
6. [Data Mining & Pattern Discovery](#part-6-data-mining--pattern-discovery)
7. [ML for Safety](#part-7-ml-for-safety)
8. [Experimental Flaws & Solutions](#part-8-experimental-flaws--solutions)

---

## Part 1: Metric Definition & Decomposition

### 1.1 Concept

A good safety metric must be:
- **Actionable**: changes when you intervene
- **Sensitive**: detects meaningful shifts quickly
- **Interpretable**: stakeholders can act on it
- **Robust**: not easily gamed or inflated by composition shifts

The key technique is **metric decomposition** — breaking an aggregate metric into components
to diagnose *where* a change comes from.

### 1.2 TikTok Context: Violation View Rate (VVR)

VVR is the fraction of content views that land on policy-violating content:

$$\text{VVR} = \frac{\text{Views on Violating Content}}{\text{Total Views}}$$

VVR can change because of:
1. **Volume shift** — more violating content is created
2. **Distribution shift** — recommendation serves violating content more often
3. **Detection lag** — violations are caught later, accumulating views
4. **Policy expansion** — new policy labels more content as violating

### 1.3 Code: VVR Decomposition

```python
import pandas as pd
import numpy as np

def decompose_vvr(df: pd.DataFrame, period_col: str = "week",
                  view_col: str = "views", violated_col: str = "is_violated") -> pd.DataFrame:
    """Decompose VVR into volume, distribution, and detection components.

    Parameters
    ----------
    df : DataFrame with columns [period_col, view_col, violated_col,
         'time_to_detect_hours', 'content_category']
    """
    results = []
    for period, grp in df.groupby(period_col):
        total_views = grp[view_col].sum()
        violated_views = grp.loc[grp[violated_col], view_col].sum()
        vvr = violated_views / total_views if total_views > 0 else 0

        # Volume: fraction of content items that are violating
        n_content = len(grp)
        n_violated = grp[violated_col].sum()
        violation_prevalence = n_violated / n_content if n_content > 0 else 0

        # Distribution: avg views per violating item / avg views per clean item
        avg_views_violated = grp.loc[grp[violated_col], view_col].mean() if n_violated > 0 else 0
        avg_views_clean = grp.loc[~grp[violated_col], view_col].mean() if (n_content - n_violated) > 0 else 0
        distribution_ratio = (avg_views_violated / avg_views_clean
                              if avg_views_clean > 0 else np.nan)

        # Detection lag: median hours to first enforcement action
        if "time_to_detect_hours" in grp.columns and n_violated > 0:
            median_detect = grp.loc[grp[violated_col], "time_to_detect_hours"].median()
        else:
            median_detect = np.nan

        results.append({
            "period": period,
            "vvr": round(vvr, 6),
            "violation_prevalence": round(violation_prevalence, 4),
            "distribution_ratio": round(distribution_ratio, 3) if not np.isnan(distribution_ratio) else None,
            "median_detection_hours": round(median_detect, 1) if not np.isnan(median_detect) else None,
            "total_views": total_views,
            "violated_views": violated_views,
        })

    return pd.DataFrame(results)
```

### 1.4 Code: Metric Decomposition by Category

```python
def category_mix_decomposition(df: pd.DataFrame, baseline_period: int,
                                current_period: int) -> pd.DataFrame:
    """Decompose VVR change into within-category vs. mix-shift effects.

    Uses the Kitagawa-Oaxaca-Blinder decomposition:
      ΔM = Σ_c [w_c1 * (m_c1 - m_c0)]   +  Σ_c [(w_c1 - w_c0) * m_c0]
           --------- within effect --------    ------- mix-shift effect ------
    """
    def _category_stats(period_df):
        total = period_df["views"].sum()
        stats = (period_df.groupby("content_category")
                 .agg(views=("views", "sum"),
                      violated_views=("views", lambda x: x[period_df.loc[x.index, "is_violated"]].sum()))
                 .assign(weight=lambda x: x["views"] / total,
                         rate=lambda x: x["violated_views"] / x["views"]))
        return stats

    base = _category_stats(df[df["week"] == baseline_period])
    curr = _category_stats(df[df["week"] == current_period])

    merged = base.join(curr, lsuffix="_base", rsuffix="_curr", how="outer").fillna(0)

    merged["within_effect"] = merged["weight_curr"] * (merged["rate_curr"] - merged["rate_base"])
    merged["mix_effect"] = (merged["weight_curr"] - merged["weight_base"]) * merged["rate_base"]

    total_within = merged["within_effect"].sum()
    total_mix = merged["mix_effect"].sum()
    total_change = total_within + total_mix

    print(f"Total VVR change: {total_change:+.6f}")
    print(f"  Within-category: {total_within:+.6f} ({total_within/total_change*100:.1f}%)")
    print(f"  Mix-shift:       {total_mix:+.6f} ({total_mix/total_change*100:.1f}%)")

    return merged[["within_effect", "mix_effect"]]
```

### 1.5 North Star vs. Guardrail vs. Diagnostic Metrics

| Layer | Purpose | Example (Safety) | Alert Threshold |
|-------|---------|-------------------|-----------------|
| **North Star** | Measures mission success | VVR (Violation View Rate) | >5% week-over-week increase |
| **Guardrail** | Prevents harm from optimizing north star | FPR (False Positive Rate), Creator Appeal Rate | >2% absolute increase |
| **Diagnostic** | Explains *why* north star moved | Detection latency, category-level VVR, model precision | Informational |

**Interview Tip**: When asked "how would you measure success?", always propose metrics at all three layers.
A candidate who only gives the north star metric looks shallow. One who also names guardrails and
diagnostics demonstrates systems thinking.

---

## Part 2: Data Collection & Quality

### 2.1 Concept

Data quality issues are the #1 silent killer of experiment validity. The interviewer
may present a scenario with a subtle data quality issue to test whether you investigate
data health *before* jumping to analysis.

### 2.2 Common Data Quality Issues in Safety

| Issue | Description | Detection Method |
|-------|-------------|-----------------|
| **Label noise** | Human reviewers disagree on policy labels | Inter-rater reliability (Cohen's κ) |
| **Selection bias** | Only flagged content gets reviewed | Compare flagged vs. random-sample audits |
| **Survivorship bias** | Deleted content absent from analytics | Track content lifecycle events |
| **Delayed labeling** | Ground truth arrives days after content posted | Time-to-label distribution analysis |
| **Instrumentation change** | Logging format changes mid-experiment | Count nulls / schema drift checks |
| **Bot contamination** | Non-human traffic inflates engagement metrics | Session-level bot detection features |

### 2.3 Code: Data Quality Audit

```python
def data_quality_audit(df: pd.DataFrame) -> dict:
    """Run standard data quality checks on an experiment dataset.

    Returns a dict of check_name -> {status, detail}.
    """
    checks = {}

    # 1. Null rate by column
    null_rates = df.isnull().mean()
    bad_nulls = null_rates[null_rates > 0.05]
    checks["null_rate"] = {
        "status": "FAIL" if len(bad_nulls) > 0 else "PASS",
        "detail": bad_nulls.to_dict() if len(bad_nulls) > 0 else "All columns < 5% null",
    }

    # 2. Duplicate rows
    n_dupes = df.duplicated().sum()
    checks["duplicates"] = {
        "status": "FAIL" if n_dupes > 0 else "PASS",
        "detail": f"{n_dupes} duplicate rows ({n_dupes/len(df)*100:.2f}%)",
    }

    # 3. Date range continuity (if 'date' column exists)
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"])
        date_range = pd.date_range(dates.min(), dates.max())
        missing_dates = set(date_range) - set(dates.dt.normalize().unique())
        checks["date_continuity"] = {
            "status": "WARN" if len(missing_dates) > 0 else "PASS",
            "detail": f"{len(missing_dates)} missing dates" if missing_dates else "Continuous",
        }

    # 4. Cardinality check (detect ID columns with suspiciously low cardinality)
    for col in df.select_dtypes(include=["object"]).columns:
        nunique = df[col].nunique()
        if nunique < 5 and len(df) > 1000:
            checks[f"low_cardinality_{col}"] = {
                "status": "WARN",
                "detail": f"{col} has only {nunique} unique values in {len(df)} rows",
            }

    # 5. Numeric outliers (IQR method)
    for col in df.select_dtypes(include=[np.number]).columns:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        outlier_frac = ((df[col] < q1 - 3 * iqr) | (df[col] > q3 + 3 * iqr)).mean()
        if outlier_frac > 0.01:
            checks[f"outliers_{col}"] = {
                "status": "WARN",
                "detail": f"{outlier_frac*100:.2f}% extreme outliers",
            }

    return checks
```

### 2.4 Code: Inter-Rater Reliability

```python
from itertools import combinations

def cohens_kappa(rater1: np.ndarray, rater2: np.ndarray) -> float:
    """Compute Cohen's kappa for two binary raters."""
    n = len(rater1)
    observed_agree = np.mean(rater1 == rater2)
    p1 = np.mean(rater1)
    p2 = np.mean(rater2)
    expected_agree = p1 * p2 + (1 - p1) * (1 - p2)
    if expected_agree == 1.0:
        return 1.0
    return (observed_agree - expected_agree) / (1 - expected_agree)

def label_quality_report(labels_df: pd.DataFrame, rater_cols: list[str]) -> pd.DataFrame:
    """Compute pairwise Cohen's kappa for multiple raters.

    labels_df: each row is a content item, each rater_col is binary label.
    """
    pairs = list(combinations(rater_cols, 2))
    results = []
    for r1, r2 in pairs:
        valid = labels_df[[r1, r2]].dropna()
        kappa = cohens_kappa(valid[r1].values, valid[r2].values)
        results.append({"rater_1": r1, "rater_2": r2, "kappa": round(kappa, 3),
                        "n_items": len(valid)})

    result_df = pd.DataFrame(results)
    avg_kappa = result_df["kappa"].mean()
    interpretation = ("Poor" if avg_kappa < 0.40
                      else "Moderate" if avg_kappa < 0.60
                      else "Good" if avg_kappa < 0.80
                      else "Excellent")
    print(f"Average kappa: {avg_kappa:.3f} ({interpretation})")
    return result_df
```

### 2.5 Code: Sample Ratio Mismatch (SRM) Detection

```python
from scipy.stats import chi2_contingency

def check_srm(n_control: int, n_treatment: int,
              expected_ratio: float = 1.0) -> dict:
    """Check for Sample Ratio Mismatch in an A/B test.

    SRM indicates a bug in the randomization or data pipeline — any
    analysis result is unreliable until the root cause is found.
    """
    total = n_control + n_treatment
    expected_control = total * (1 / (1 + expected_ratio))
    expected_treatment = total * (expected_ratio / (1 + expected_ratio))

    chi2_stat = ((n_control - expected_control) ** 2 / expected_control
                 + (n_treatment - expected_treatment) ** 2 / expected_treatment)

    from scipy.stats import chi2
    p_value = 1 - chi2.cdf(chi2_stat, df=1)

    actual_ratio = n_treatment / n_control if n_control > 0 else float("inf")

    return {
        "actual_ratio": round(actual_ratio, 4),
        "expected_ratio": expected_ratio,
        "chi2_stat": round(chi2_stat, 2),
        "p_value": round(p_value, 6),
        "srm_detected": p_value < 0.001,
        "interpretation": (
            "SRM DETECTED — do NOT trust experiment results. "
            "Investigate: logging bugs, bot filtering, bucketing errors."
            if p_value < 0.001
            else "No SRM detected — ratio consistent with expected."
        ),
    }
```

**Interview Tip**: If presented with an experiment result, ask about data quality *first*.
"Before I analyze the results, I'd want to verify there's no SRM, check for
instrumentation changes during the experiment window, and confirm the randomization
unit matches the analysis unit."

---

## Part 3: Dashboarding

### 3.1 Concept

The Round 1 interviewer may ask you to design a monitoring dashboard for a safety metric.
A strong answer covers:

1. **Layout** — what panels, how arranged, what resolution (hourly/daily/weekly)
2. **Interactivity** — filters (region, policy type, content category), drill-down
3. **Alerting** — anomaly thresholds, on-call escalation
4. **Stakeholder mapping** — who uses this dashboard and what decisions they make

### 3.2 TikTok Safety Dashboard: 6-Panel Design

| Panel | Chart Type | Metric | Audience |
|-------|-----------|--------|----------|
| 1. VVR Trend | Time series + control limits | Daily VVR with 7-day MA | Safety leadership |
| 2. Violation Breakdown | Stacked bar | Volume by policy category | Policy team |
| 3. Precision-Recall | Dual axis | Classifier performance over time | ML team |
| 4. Time-to-Action | Histogram + percentiles | Hours from post to enforcement | Ops team |
| 5. Regional Heatmap | Choropleth | VVR by country/region | Regional leads |
| 6. Anomaly Alerts | Table + status | Active anomalies with severity | On-call DS |

### 3.3 Code: Building a Safety Dashboard with Plotly

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_safety_dashboard(df: pd.DataFrame) -> go.Figure:
    """Create a 6-panel safety metrics dashboard.

    Parameters
    ----------
    df : DataFrame with columns:
        date, vvr, violation_count, policy_category, precision, recall,
        time_to_action_hours, region
    """
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[
            "VVR Trend with Control Limits",
            "Violations by Policy Category",
            "Classifier Precision & Recall",
            "Time-to-Action Distribution",
            "VVR by Region",
            "Active Anomalies",
        ],
        specs=[
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "histogram"}],
            [{"type": "bar"}, {"type": "table"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
    )

    # --- Panel 1: VVR Trend ---
    daily = df.groupby("date").agg(vvr=("vvr", "mean")).reset_index()
    daily["ma7"] = daily["vvr"].rolling(7, min_periods=1).mean()
    mu = daily["vvr"].mean()
    sigma = daily["vvr"].std()

    fig.add_trace(go.Scatter(x=daily["date"], y=daily["vvr"],
                             mode="lines", name="Daily VVR",
                             line=dict(color="#1E88E5", width=1)),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["ma7"],
                             mode="lines", name="7-day MA",
                             line=dict(color="#E91E63", width=2)),
                  row=1, col=1)
    # Upper control limit (3σ)
    fig.add_hline(y=mu + 3 * sigma, line_dash="dash",
                  line_color="red", row=1, col=1,
                  annotation_text="UCL (3σ)")

    # --- Panel 2: Violations by Category ---
    cat_counts = (df.groupby(["date", "policy_category"])["violation_count"]
                  .sum().reset_index())
    for cat in df["policy_category"].unique():
        subset = cat_counts[cat_counts["policy_category"] == cat]
        fig.add_trace(go.Bar(x=subset["date"], y=subset["violation_count"],
                             name=cat), row=1, col=2)
    fig.update_layout(barmode="stack")

    # --- Panel 3: Precision & Recall ---
    pr = df.groupby("date").agg(precision=("precision", "mean"),
                                 recall=("recall", "mean")).reset_index()
    fig.add_trace(go.Scatter(x=pr["date"], y=pr["precision"],
                             mode="lines+markers", name="Precision",
                             line=dict(color="#4CAF50")),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=pr["date"], y=pr["recall"],
                             mode="lines+markers", name="Recall",
                             line=dict(color="#FF9800")),
                  row=2, col=1)

    # --- Panel 4: Time-to-Action ---
    fig.add_trace(go.Histogram(x=df["time_to_action_hours"],
                               nbinsx=50, name="Time to Action",
                               marker_color="#1565C0"),
                  row=2, col=2)
    p50 = df["time_to_action_hours"].median()
    p95 = df["time_to_action_hours"].quantile(0.95)
    fig.add_vline(x=p50, line_dash="dash", line_color="green",
                  row=2, col=2, annotation_text=f"P50={p50:.1f}h")
    fig.add_vline(x=p95, line_dash="dash", line_color="red",
                  row=2, col=2, annotation_text=f"P95={p95:.1f}h")

    # --- Panel 5: VVR by Region ---
    region_vvr = (df.groupby("region")["vvr"].mean()
                  .sort_values(ascending=True).reset_index())
    fig.add_trace(go.Bar(x=region_vvr["vvr"], y=region_vvr["region"],
                         orientation="h", name="Regional VVR",
                         marker_color="#E91E63"),
                  row=3, col=1)

    # --- Panel 6: Anomaly Table ---
    # Detect anomalies: days where VVR > UCL
    anomalies = daily[daily["vvr"] > mu + 3 * sigma].tail(5)
    fig.add_trace(go.Table(
        header=dict(values=["Date", "VVR", "Deviation"],
                    fill_color="#0A1628", font=dict(color="white")),
        cells=dict(values=[
            anomalies["date"].dt.strftime("%Y-%m-%d") if len(anomalies) > 0 else ["—"],
            anomalies["vvr"].round(6) if len(anomalies) > 0 else ["—"],
            ((anomalies["vvr"] - mu) / sigma).round(2).astype(str) + "σ" if len(anomalies) > 0 else ["—"],
        ]),
    ), row=3, col=2)

    fig.update_layout(
        height=900, width=1200,
        title_text="Safety Metrics Dashboard",
        template="plotly_dark",
        showlegend=False,
    )

    return fig
```

### 3.4 Dashboard Design Principles

1. **Start with the decision**: "What action will the viewer take based on this chart?"
   If no action → remove the chart.
2. **Progressive disclosure**: Summary metrics at top, drill-down below.
   VVR trend first, category breakdown on click.
3. **Consistent time axis**: All panels share the same date range.
   Comparing a weekly chart with a monthly chart is confusing.
4. **Control limits over arbitrary thresholds**: Use statistical process control
   (Shewhart 3σ, CUSUM, EWMA) rather than business-rule thresholds.
5. **Distinguish signal from noise**: Use 7-day moving averages for trend,
   raw daily for anomaly detection.

### 3.5 Code: Anomaly Detection for Dashboard Alerts

```python
def shewhart_control_chart(values: np.ndarray, window: int = 30,
                           n_sigma: float = 3.0) -> pd.DataFrame:
    """Shewhart control chart with rolling baseline.

    Returns DataFrame with columns: value, center, ucl, lcl, is_anomaly.
    """
    series = pd.Series(values)
    center = series.rolling(window, min_periods=window // 2).mean()
    spread = series.rolling(window, min_periods=window // 2).std()

    ucl = center + n_sigma * spread
    lcl = center - n_sigma * spread

    return pd.DataFrame({
        "value": values,
        "center": center,
        "ucl": ucl,
        "lcl": lcl,
        "is_anomaly": (series > ucl) | (series < lcl),
    })


def cusum_detector(values: np.ndarray, target: float = None,
                   threshold: float = 5.0, drift: float = 0.5) -> pd.DataFrame:
    """CUSUM (Cumulative Sum) change detector.

    More sensitive to sustained small shifts than Shewhart charts.

    Parameters
    ----------
    target : baseline mean (estimated from data if None)
    threshold : decision interval (h * σ, typically 4-5)
    drift : allowance parameter (k * σ, typically 0.5-1.0)
    """
    if target is None:
        target = np.mean(values[:min(30, len(values))])

    sigma = np.std(values[:min(30, len(values))])
    k = drift * sigma
    h = threshold * sigma

    s_pos = np.zeros(len(values))
    s_neg = np.zeros(len(values))
    alerts = np.zeros(len(values), dtype=bool)

    for i in range(1, len(values)):
        s_pos[i] = max(0, s_pos[i - 1] + (values[i] - target) - k)
        s_neg[i] = max(0, s_neg[i - 1] - (values[i] - target) - k)
        if s_pos[i] > h or s_neg[i] > h:
            alerts[i] = True

    return pd.DataFrame({
        "value": values,
        "cusum_pos": s_pos,
        "cusum_neg": s_neg,
        "alert": alerts,
    })
```

**Interview Tip**: When asked to "design a dashboard," don't just list charts. Structure your
answer: (1) who is the audience, (2) what decisions do they make, (3) what metrics inform those
decisions, (4) what visualization best encodes each metric, (5) how do you handle alerting.
Then sketch the layout with panel descriptions.

---

## Part 4: A/B Testing Walkthrough

### 4.1 End-to-End A/B Testing Lifecycle

```
Business Question → Metric Selection → Power Analysis → Experiment Design
→ Pre-Experiment Validation → Experiment Execution → Analysis → Decision
→ Post-Launch Monitoring
```

### 4.2 Code: Power Analysis

```python
from scipy.stats import norm

def power_analysis(baseline_rate: float, mde: float,
                   alpha: float = 0.05, power: float = 0.80,
                   ratio: float = 1.0) -> dict:
    """Two-sample proportion test power analysis.

    Parameters
    ----------
    baseline_rate : current metric value (e.g., 0.05 for 5% VVR)
    mde : minimum detectable effect (relative, e.g., 0.10 for 10% reduction)
    alpha : significance level
    power : desired statistical power
    ratio : treatment/control size ratio

    Returns
    -------
    dict with n_control, n_treatment, total_n
    """
    p0 = baseline_rate
    p1 = p0 * (1 - mde)  # expected treatment rate

    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)

    # Pooled variance under H0 and H1
    p_bar = (p0 + ratio * p1) / (1 + ratio)
    se_h0 = np.sqrt(p_bar * (1 - p_bar) * (1 + 1 / ratio))
    se_h1 = np.sqrt(p0 * (1 - p0) + p1 * (1 - p1) / ratio)

    n_control = ((z_alpha * se_h0 + z_beta * se_h1) / (p0 - p1)) ** 2
    n_treatment = n_control * ratio

    return {
        "n_control": int(np.ceil(n_control)),
        "n_treatment": int(np.ceil(n_treatment)),
        "total_n": int(np.ceil(n_control + n_treatment)),
        "baseline_rate": p0,
        "expected_treatment_rate": round(p1, 6),
        "absolute_effect": round(p0 - p1, 6),
        "relative_effect": f"{mde * 100:.1f}%",
        "runtime_days": None,  # fill in with daily traffic estimate
    }


def estimate_runtime(total_n: int, daily_traffic: int,
                     fraction_eligible: float = 1.0) -> float:
    """Estimate experiment runtime in days."""
    eligible_per_day = daily_traffic * fraction_eligible
    days = total_n / eligible_per_day if eligible_per_day > 0 else float("inf")
    return round(days, 1)

# Example: detecting a 10% relative reduction in 5% VVR
result = power_analysis(baseline_rate=0.05, mde=0.10)
# result["total_n"] ≈ 57,000 per arm → with 10M daily views, ~1 day runtime
```

### 4.3 Code: CUPED Variance Reduction

```python
def cuped_adjustment(y_post: np.ndarray, y_pre: np.ndarray) -> np.ndarray:
    """Apply CUPED (Controlled-experiment Using Pre-Experiment Data).

    Subtracts the component of post-experiment variance explained by
    pre-experiment data.

    y_adjusted = y_post - θ * (y_pre - mean(y_pre))
    where θ = Cov(y_post, y_pre) / Var(y_pre)
    """
    theta = np.cov(y_post, y_pre)[0, 1] / np.var(y_pre)
    y_adjusted = y_post - theta * (y_pre - np.mean(y_pre))
    return y_adjusted


def cuped_experiment_analysis(df: pd.DataFrame, metric_col: str,
                               pre_metric_col: str, group_col: str = "group",
                               control_label: str = "control",
                               treatment_label: str = "treatment") -> dict:
    """Run CUPED-adjusted analysis on an A/B test.

    Parameters
    ----------
    df : DataFrame with one row per user
    metric_col : post-experiment metric column
    pre_metric_col : pre-experiment metric column
    group_col : column indicating treatment/control
    """
    from scipy.stats import ttest_ind

    ctrl = df[df[group_col] == control_label]
    treat = df[df[group_col] == treatment_label]

    # Unadjusted analysis
    raw_diff = treat[metric_col].mean() - ctrl[metric_col].mean()
    raw_t, raw_p = ttest_ind(treat[metric_col], ctrl[metric_col])
    raw_se = np.sqrt(treat[metric_col].var() / len(treat)
                     + ctrl[metric_col].var() / len(ctrl))

    # CUPED-adjusted analysis
    all_pre = df[pre_metric_col].values
    all_post = df[metric_col].values
    theta = np.cov(all_post, all_pre)[0, 1] / np.var(all_pre)

    ctrl_adj = ctrl[metric_col] - theta * (ctrl[pre_metric_col] - all_pre.mean())
    treat_adj = treat[metric_col] - theta * (treat[pre_metric_col] - all_pre.mean())

    adj_diff = treat_adj.mean() - ctrl_adj.mean()
    adj_t, adj_p = ttest_ind(treat_adj, ctrl_adj)
    adj_se = np.sqrt(treat_adj.var() / len(treat_adj)
                     + ctrl_adj.var() / len(ctrl_adj))

    variance_reduction = 1 - (adj_se ** 2) / (raw_se ** 2)

    return {
        "raw_diff": round(raw_diff, 6),
        "raw_se": round(raw_se, 6),
        "raw_p_value": round(raw_p, 6),
        "cuped_diff": round(adj_diff, 6),
        "cuped_se": round(adj_se, 6),
        "cuped_p_value": round(adj_p, 6),
        "variance_reduction": f"{variance_reduction * 100:.1f}%",
        "theta": round(theta, 4),
    }
```

### 4.4 Code: Sequential Testing with mSPRT

```python
def msprt_boundary(n: int, alpha: float = 0.05, tau: float = None,
                   sigma: float = 1.0) -> float:
    """Compute the mSPRT (mixture Sequential Probability Ratio Test) boundary.

    The mSPRT allows continuous monitoring without inflating Type I error.

    Parameters
    ----------
    n : current sample size (per arm)
    alpha : overall significance level
    tau : mixing parameter (default: sigma, i.e., unit prior)
    sigma : known/estimated standard deviation
    """
    if tau is None:
        tau = sigma

    # Log-likelihood ratio boundary
    v = sigma ** 2 / n
    boundary = np.sqrt((v + tau ** 2) / tau ** 2 * np.log((v + tau ** 2) / (alpha ** 2 * v)))

    return boundary


def sequential_test(cumulative_means_ctrl: np.ndarray,
                    cumulative_means_treat: np.ndarray,
                    cumulative_n: np.ndarray,
                    alpha: float = 0.05) -> pd.DataFrame:
    """Monitor an experiment with mSPRT sequential testing.

    Parameters
    ----------
    cumulative_means_ctrl : array of running mean for control group
    cumulative_means_treat : array of running mean for treatment group
    cumulative_n : array of cumulative sample sizes (per arm)

    Returns
    -------
    DataFrame with columns: n, diff, boundary, significant
    """
    results = []
    sigma_est = None
    for i in range(len(cumulative_n)):
        n = cumulative_n[i]
        diff = cumulative_means_treat[i] - cumulative_means_ctrl[i]

        if sigma_est is None:
            sigma_est = abs(diff) * 5 if abs(diff) > 0 else 1.0  # rough initial estimate

        boundary = msprt_boundary(n, alpha=alpha, sigma=sigma_est)

        results.append({
            "n_per_arm": n,
            "observed_diff": round(diff, 6),
            "boundary": round(boundary, 6),
            "significant": abs(diff) > boundary,
        })

    return pd.DataFrame(results)
```

### 4.5 Code: Subgroup Analysis (Heterogeneous Treatment Effects)

```python
def subgroup_analysis(df: pd.DataFrame, metric_col: str,
                      group_col: str, subgroup_cols: list[str],
                      control_label: str = "control",
                      treatment_label: str = "treatment") -> pd.DataFrame:
    """Analyze treatment effects across subgroups.

    Includes Bonferroni correction for multiple comparisons.
    """
    from scipy.stats import ttest_ind

    results = []
    n_tests = 0

    for sg_col in subgroup_cols:
        for sg_val in df[sg_col].unique():
            subset = df[df[sg_col] == sg_val]
            ctrl = subset[subset[group_col] == control_label][metric_col]
            treat = subset[subset[group_col] == treatment_label][metric_col]

            if len(ctrl) < 30 or len(treat) < 30:
                continue

            diff = treat.mean() - ctrl.mean()
            t_stat, p_val = ttest_ind(treat, ctrl)
            n_tests += 1

            results.append({
                "subgroup": sg_col,
                "value": sg_val,
                "n_control": len(ctrl),
                "n_treatment": len(treat),
                "ctrl_mean": round(ctrl.mean(), 6),
                "treat_mean": round(treat.mean(), 6),
                "diff": round(diff, 6),
                "relative_diff": round(diff / ctrl.mean() * 100, 2) if ctrl.mean() != 0 else None,
                "p_value": round(p_val, 6),
            })

    result_df = pd.DataFrame(results)

    # Bonferroni correction
    if len(result_df) > 0:
        result_df["p_adjusted"] = np.minimum(result_df["p_value"] * n_tests, 1.0)
        result_df["significant"] = result_df["p_adjusted"] < 0.05

    return result_df
```

### 4.6 Decision Framework

After analysis, present results using this structure:

```
1. PRIMARY METRIC: [name] changed by [X]% (p = [Y], 95% CI: [a, b])
   → Statistically significant? [Yes/No]
   → Practically significant (exceeds MDE)? [Yes/No]

2. GUARDRAIL METRICS: [list each with direction and significance]
   → Any guardrail violations? [Yes/No]

3. SUBGROUP EFFECTS: [any heterogeneity worth noting]
   → Consistent across regions/segments? [Yes/No]

4. RECOMMENDATION: [Ship / Don't Ship / Iterate]
   → Rationale: [1-2 sentences connecting metrics to business impact]
```

**Interview Tip**: End every experiment analysis with a clear recommendation.
"Based on a 12% reduction in VVR (p<0.001) with no significant impact on
creator posting rate (our guardrail), I recommend launching this policy change.
The expected annual impact is ~X million fewer violating views."
The "so what?" — translating statistics into business action — is what separates
a strong candidate from an average one.

---

## Part 5: Causal Inference Walkthrough

### 5.1 When You Can't Run an A/B Test

Many safety interventions cannot be randomized:
- **Policy changes** apply to all users simultaneously
- **Ethical constraints** prevent withholding safety protections
- **Network effects** make user-level randomization invalid (bad actors affect neighbors)
- **Platform-wide rollouts** already happened — you need to evaluate *post hoc*

The interviewer may ask: "We launched a new content moderation policy 3 months ago.
How would you evaluate whether it worked?" This requires causal inference.

### 5.2 Method Selection Decision Tree

```
Can you randomize?
├── Yes → A/B Test (Part 4)
└── No
    ├── Is there a clear before/after + control group?
    │   └── Yes → Difference-in-Differences (DID)
    ├── Is treatment assigned by a threshold on a continuous variable?
    │   └── Yes → Regression Discontinuity Design (RDD)
    ├── Is there an instrument (something that affects treatment but not outcome)?
    │   └── Yes → Instrumental Variables (IV / 2SLS)
    ├── Can you find untreated units similar to treated ones?
    │   └── Yes → Propensity Score Matching (PSM) / IPW
    └── Do you have few treated units with many controls and long pre-treatment data?
        └── Yes → Synthetic Control
```

### 5.3 Code: Difference-in-Differences

```python
import statsmodels.formula.api as smf

def did_analysis(df: pd.DataFrame, outcome: str = "gmv",
                 treatment_col: str = "is_bad_seller",
                 post_col: str = "post_treatment") -> dict:
    """Difference-in-Differences estimation with fixed effects.

    Parameters
    ----------
    df : panel data with one row per unit-period
    outcome : dependent variable
    treatment_col : binary indicator for treatment group
    post_col : binary indicator for post-treatment period
    """
    df = df.copy()
    df["treat_post"] = df[treatment_col].astype(int) * df[post_col].astype(int)

    # Basic DID
    formula = f"{outcome} ~ {treatment_col} + {post_col} + treat_post"
    model = smf.ols(formula, data=df).fit(cov_type="cluster",
                                           cov_kwds={"groups": df["seller_id"]})

    att = model.params["treat_post"]
    se = model.bse["treat_post"]
    ci = model.conf_int().loc["treat_post"]
    p = model.pvalues["treat_post"]

    return {
        "att": round(att, 4),
        "se": round(se, 4),
        "ci_lower": round(ci[0], 4),
        "ci_upper": round(ci[1], 4),
        "p_value": round(p, 6),
        "interpretation": (
            f"The treatment {'decreased' if att < 0 else 'increased'} "
            f"{outcome} by {abs(att):.2f} units (p={p:.4f}). "
            f"95% CI: [{ci[0]:.2f}, {ci[1]:.2f}]."
        ),
    }


def parallel_trends_test(df: pd.DataFrame, outcome: str,
                          treatment_col: str, time_col: str,
                          treatment_time: int) -> pd.DataFrame:
    """Test parallel trends assumption by estimating period-specific effects.

    Estimates: Y = α + Σ_t [β_t × Treat × 1(t)] + γ_t + δ_i + ε
    Pre-treatment β_t should be ≈ 0 (parallel trends hold).
    """
    pre = df[df[time_col] < treatment_time].copy()
    pre["time_factor"] = pre[time_col].astype(str)

    # Event study: interaction of treatment with each time period
    periods = sorted(pre[time_col].unique())
    ref_period = periods[-1]  # last pre-treatment period as reference
    pre = pre[pre[time_col] != ref_period]

    formula = f"{outcome} ~ C({treatment_col}):C(time_factor)"
    model = smf.ols(formula, data=pre).fit()

    # Extract treatment × period coefficients
    results = []
    for param, coef in model.params.items():
        if f"C({treatment_col})" in param and "C(time_factor)" in param:
            period = param.split("T.")[-1].rstrip("]")
            results.append({
                "period": period,
                "coefficient": round(coef, 4),
                "se": round(model.bse[param], 4),
                "p_value": round(model.pvalues[param], 4),
            })

    result_df = pd.DataFrame(results)
    # If all pre-treatment coefficients are insignificant, parallel trends hold
    max_p = result_df["p_value"].min()
    print(f"Parallel trends test: min p-value = {max_p:.4f}")
    print("  ✓ Parallel trends supported" if max_p > 0.05
          else "  ✗ Parallel trends may be violated — consider alternative methods")
    return result_df
```

### 5.4 Code: Regression Discontinuity Design

```python
def rdd_estimate(df: pd.DataFrame, running_var: str, outcome: str,
                 cutoff: float, bandwidth: float = None) -> dict:
    """Local linear RDD estimation.

    Parameters
    ----------
    df : one row per unit, observed at the cutoff
    running_var : the variable that determines treatment assignment
    outcome : dependent variable
    cutoff : treatment threshold
    bandwidth : window around cutoff (auto-selected if None)
    """
    df = df.copy()
    df["centered"] = df[running_var] - cutoff
    df["treated"] = (df[running_var] >= cutoff).astype(int)

    # Auto bandwidth: Imbens-Kalyanaraman optimal (simplified)
    if bandwidth is None:
        bandwidth = 1.06 * df["centered"].std() * len(df) ** (-1 / 5)

    local = df[df["centered"].abs() <= bandwidth]

    if len(local) < 50:
        return {"error": f"Too few observations within bandwidth ({len(local)})"}

    # Local linear regression: Y = α + τ*D + β₁*X + β₂*D*X + ε
    formula = f"{outcome} ~ treated + centered + treated:centered"
    model = smf.ols(formula, data=local).fit(cov_type="HC1")

    tau = model.params["treated"]
    se = model.bse["treated"]
    ci = model.conf_int().loc["treated"]

    return {
        "tau": round(tau, 4),
        "se": round(se, 4),
        "ci_lower": round(ci[0], 4),
        "ci_upper": round(ci[1], 4),
        "p_value": round(model.pvalues["treated"], 6),
        "bandwidth": round(bandwidth, 4),
        "n_local": len(local),
        "n_below": (local["treated"] == 0).sum(),
        "n_above": (local["treated"] == 1).sum(),
    }


def mccrary_density_test(running_var: np.ndarray, cutoff: float,
                          n_bins: int = 50) -> dict:
    """McCrary density test for manipulation of the running variable.

    If units can manipulate their score to avoid/receive treatment,
    the density will show a discontinuity at the cutoff.
    """
    below = running_var[running_var < cutoff]
    above = running_var[running_var >= cutoff]

    # Simple binned density comparison near cutoff
    near_below = running_var[(running_var >= cutoff - 0.1) & (running_var < cutoff)]
    near_above = running_var[(running_var >= cutoff) & (running_var < cutoff + 0.1)]

    density_below = len(near_below) / len(running_var)
    density_above = len(near_above) / len(running_var)
    ratio = density_above / density_below if density_below > 0 else float("inf")

    return {
        "density_below_cutoff": round(density_below, 4),
        "density_above_cutoff": round(density_above, 4),
        "ratio": round(ratio, 3),
        "manipulation_suspected": abs(ratio - 1.0) > 0.3,
        "interpretation": (
            "No evidence of manipulation — density is approximately continuous."
            if abs(ratio - 1.0) <= 0.3
            else "Possible manipulation — density discontinuity detected. "
                 "RDD estimates may be biased."
        ),
    }
```

### 5.5 Code: Propensity Score Matching

```python
from sklearn.linear_model import LogisticRegression
from scipy.spatial.distance import cdist

def propensity_score_matching(df: pd.DataFrame, treatment_col: str,
                                covariates: list[str], outcome_col: str,
                                n_matches: int = 1, caliper: float = 0.05
                                ) -> dict:
    """Estimate ATT using nearest-neighbor propensity score matching.

    Parameters
    ----------
    df : one row per unit
    treatment_col : binary treatment indicator
    covariates : list of covariate columns for propensity model
    outcome_col : outcome variable
    n_matches : number of control matches per treated unit
    caliper : maximum propensity score distance for a valid match
    """
    X = df[covariates].values
    t = df[treatment_col].values.astype(int)

    # Estimate propensity scores
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X, t)
    ps = lr.predict_proba(X)[:, 1]
    df = df.copy()
    df["propensity_score"] = ps

    treated = df[df[treatment_col] == 1]
    control = df[df[treatment_col] == 0]

    # Nearest-neighbor matching
    matched_outcomes_treat = []
    matched_outcomes_ctrl = []

    for _, row in treated.iterrows():
        ps_treat = row["propensity_score"]
        distances = np.abs(control["propensity_score"].values - ps_treat)
        nearest_idx = np.argsort(distances)[:n_matches]

        if distances[nearest_idx[0]] > caliper:
            continue  # no match within caliper

        matched_outcomes_treat.append(row[outcome_col])
        matched_outcomes_ctrl.append(control.iloc[nearest_idx][outcome_col].mean())

    att = np.mean(matched_outcomes_treat) - np.mean(matched_outcomes_ctrl)
    se = np.sqrt(np.var(matched_outcomes_treat) / len(matched_outcomes_treat)
                 + np.var(matched_outcomes_ctrl) / len(matched_outcomes_ctrl))

    return {
        "att": round(att, 4),
        "se": round(se, 4),
        "ci_lower": round(att - 1.96 * se, 4),
        "ci_upper": round(att + 1.96 * se, 4),
        "n_matched": len(matched_outcomes_treat),
        "n_unmatched": len(treated) - len(matched_outcomes_treat),
        "mean_ps_treated": round(treated["propensity_score"].mean(), 4),
        "mean_ps_control": round(control["propensity_score"].mean(), 4),
    }
```

**Interview Tip**: When the interviewer describes a policy evaluation scenario, don't jump
straight to DID. Walk through the decision tree aloud: "Can we randomize? No, because...
Is there a clear pre/post? Yes. Is there a control group? Yes, the unaffected region.
So DID is appropriate, provided parallel trends hold. Let me verify that first."

---

## Part 6: Data Mining & Pattern Discovery

### 6.1 Concept

Safety DS teams need to discover emerging threats *before* they become widespread.
This involves pattern mining, anomaly detection, and exploratory analysis at scale.

### 6.2 Code: Sessionization for Behavior Analysis

```python
def sessionize(df: pd.DataFrame, user_col: str = "user_id",
               time_col: str = "timestamp",
               gap_minutes: int = 30) -> pd.DataFrame:
    """Assign session IDs based on inactivity gaps.

    Two events from the same user are in the same session if
    the gap between them is ≤ gap_minutes.
    """
    df = df.sort_values([user_col, time_col]).copy()
    df[time_col] = pd.to_datetime(df[time_col])

    df["time_diff"] = df.groupby(user_col)[time_col].diff()
    df["new_session"] = (df["time_diff"] > pd.Timedelta(minutes=gap_minutes)) | df["time_diff"].isna()
    df["session_id"] = df.groupby(user_col)["new_session"].cumsum()
    df["session_id"] = df[user_col].astype(str) + "_" + df["session_id"].astype(str)

    df.drop(columns=["time_diff", "new_session"], inplace=True)
    return df


def session_features(df: pd.DataFrame, session_col: str = "session_id",
                     time_col: str = "timestamp") -> pd.DataFrame:
    """Compute session-level features for behavior analysis."""
    df[time_col] = pd.to_datetime(df[time_col])

    features = df.groupby(session_col).agg(
        n_events=(time_col, "count"),
        duration_minutes=(time_col, lambda x: (x.max() - x.min()).total_seconds() / 60),
        start_time=(time_col, "min"),
    )
    features["events_per_minute"] = (
        features["n_events"] / features["duration_minutes"].clip(lower=1/60)
    )
    return features
```

### 6.3 Code: Anomaly Detection in Time Series

```python
def stl_anomaly_detection(series: pd.Series, period: int = 7,
                           threshold: float = 3.0) -> pd.DataFrame:
    """Detect anomalies using STL decomposition.

    Decomposes time series into trend + seasonal + residual,
    then flags residuals > threshold * σ.
    """
    from statsmodels.tsa.seasonal import STL

    stl = STL(series, period=period, robust=True)
    result = stl.fit()

    residual = result.resid
    mu = residual.mean()
    sigma = residual.std()

    return pd.DataFrame({
        "observed": series.values,
        "trend": result.trend,
        "seasonal": result.seasonal,
        "residual": residual,
        "z_score": (residual - mu) / sigma,
        "is_anomaly": np.abs(residual - mu) > threshold * sigma,
    }, index=series.index)


def ewma_detector(values: np.ndarray, span: int = 20,
                   n_sigma: float = 3.0) -> pd.DataFrame:
    """Exponentially Weighted Moving Average anomaly detector.

    More responsive to recent changes than Shewhart charts.
    Suitable for metrics with changing baselines.
    """
    series = pd.Series(values)
    ewma = series.ewm(span=span).mean()
    ewma_std = series.ewm(span=span).std()

    ucl = ewma + n_sigma * ewma_std
    lcl = ewma - n_sigma * ewma_std

    return pd.DataFrame({
        "value": values,
        "ewma": ewma.values,
        "ucl": ucl.values,
        "lcl": lcl.values,
        "is_anomaly": (series > ucl) | (series < lcl),
    })
```

### 6.4 Code: Coordinated Behavior Detection

```python
def detect_coordinated_activity(df: pd.DataFrame, user_col: str,
                                 time_col: str, content_col: str,
                                 time_window_minutes: int = 5,
                                 min_cluster_size: int = 5) -> pd.DataFrame:
    """Detect coordinated inauthentic behavior.

    Flags groups of users who engage with the same content within
    a narrow time window — a signal of bot networks or coordinated campaigns.
    """
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])

    # Group by content and find users acting within the time window
    clusters = []
    for content_id, group in df.groupby(content_col):
        group = group.sort_values(time_col)
        times = group[time_col].values
        users = group[user_col].values

        # Sliding window: find bursts
        window = pd.Timedelta(minutes=time_window_minutes)
        for i in range(len(times)):
            burst_mask = (times >= times[i]) & (times <= times[i] + window)
            burst_users = set(users[burst_mask])
            if len(burst_users) >= min_cluster_size:
                clusters.append({
                    "content_id": content_id,
                    "burst_start": times[i],
                    "n_users": len(burst_users),
                    "users": burst_users,
                })

    if not clusters:
        return pd.DataFrame(columns=["content_id", "burst_start", "n_users"])

    result = pd.DataFrame(clusters)
    # Deduplicate overlapping bursts for same content
    result = (result.sort_values(["content_id", "n_users"], ascending=[True, False])
              .drop_duplicates(subset=["content_id"], keep="first")
              .reset_index(drop=True))

    return result
```

### 6.5 Code: Metric Decomposition by Funnel Stage

```python
def funnel_decomposition(df: pd.DataFrame, stages: list[str],
                          period_col: str = "week") -> pd.DataFrame:
    """Decompose an end-to-end metric into funnel stage conversion rates.

    Example stages for content safety:
    ['content_created', 'flagged_by_model', 'sent_to_review',
     'reviewer_confirmed', 'action_taken']
    """
    results = []
    for period, grp in df.groupby(period_col):
        row = {"period": period}
        for i, stage in enumerate(stages):
            count = grp[stage].sum()
            row[f"{stage}_count"] = count
            if i > 0:
                prev_count = grp[stages[i - 1]].sum()
                conversion = count / prev_count if prev_count > 0 else 0
                row[f"{stages[i-1]}_to_{stage}"] = round(conversion, 4)
        results.append(row)

    return pd.DataFrame(results)
```

**Interview Tip**: When asked "How would you detect emerging safety threats?", structure
your answer around three signals: (1) volumetric anomalies (sudden spikes in violation
volume), (2) behavioral patterns (coordinated activity, new-account bursts), and
(3) content signals (new keywords, formats, or distribution patterns not in training data).
Connect each signal to a specific detection method.

---

## Part 7: ML for Safety

### 7.1 XGBoost Pipeline for Content Safety Classification

XGBoost is the workhorse for tabular safety classification at scale. The interview
may ask you to design a classification pipeline, discuss feature engineering,
or handle class imbalance.

### 7.2 Code: End-to-End XGBoost Safety Classifier

```python
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (classification_report, precision_recall_curve,
                              roc_auc_score, average_precision_score)

def train_safety_classifier(X: pd.DataFrame, y: pd.Series,
                             imbalance_ratio: float = None) -> dict:
    """Train an XGBoost classifier for safety content detection.

    Handles class imbalance via scale_pos_weight.
    Returns model, cross-validated predictions, and evaluation metrics.
    """
    if imbalance_ratio is None:
        imbalance_ratio = (y == 0).sum() / max((y == 1).sum(), 1)

    params = {
        "objective": "binary:logistic",
        "eval_metric": "aucpr",  # area under precision-recall curve
        "scale_pos_weight": imbalance_ratio,
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 200,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "random_state": 42,
        "n_jobs": -1,
    }

    model = xgb.XGBClassifier(**params)

    # Cross-validated predictions for evaluation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    y_proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]

    # Fit final model on all data
    model.fit(X, y)

    # Metrics
    auc_roc = roc_auc_score(y, y_proba)
    auc_pr = average_precision_score(y, y_proba)

    # Find optimal threshold (maximize F1)
    precisions, recalls, thresholds = precision_recall_curve(y, y_proba)
    f1_scores = 2 * precisions * recalls / (precisions + recalls + 1e-8)
    best_idx = np.argmax(f1_scores)
    optimal_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5

    y_pred = (y_proba >= optimal_threshold).astype(int)

    return {
        "model": model,
        "y_proba": y_proba,
        "optimal_threshold": round(optimal_threshold, 3),
        "auc_roc": round(auc_roc, 4),
        "auc_pr": round(auc_pr, 4),
        "best_f1": round(f1_scores[best_idx], 4),
        "classification_report": classification_report(y, y_pred, output_dict=True),
    }
```

### 7.3 Code: Feature Importance and SHAP Analysis

```python
def feature_importance_analysis(model: xgb.XGBClassifier,
                                 feature_names: list[str],
                                 top_k: int = 20) -> pd.DataFrame:
    """Extract and rank feature importances from XGBoost model.

    Uses gain-based importance (how much each feature improves the
    objective when used in splits).
    """
    importances = model.feature_importances_
    fi = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    }).sort_values("importance", ascending=False).head(top_k)

    fi["cumulative_importance"] = fi["importance"].cumsum() / fi["importance"].sum()
    fi["rank"] = range(1, len(fi) + 1)

    return fi


def plot_precision_recall_tradeoff(y_true: np.ndarray, y_proba: np.ndarray,
                                    operating_points: dict = None):
    """Plot precision-recall curve with operating point annotations.

    operating_points: dict of {label: threshold} for marking on the curve.
    Example: {"conservative": 0.9, "balanced": 0.5, "aggressive": 0.3}
    """
    import plotly.graph_objects as go
    from sklearn.metrics import precision_recall_curve

    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recalls, y=precisions, mode="lines",
                             name="PR Curve", line=dict(color="#1565C0")))

    if operating_points:
        for label, thresh in operating_points.items():
            idx = np.argmin(np.abs(thresholds - thresh))
            fig.add_trace(go.Scatter(
                x=[recalls[idx]], y=[precisions[idx]], mode="markers+text",
                name=label, text=[f"{label} (t={thresh})"],
                textposition="top right",
                marker=dict(size=12),
            ))

    fig.update_layout(
        xaxis_title="Recall", yaxis_title="Precision",
        title="Precision-Recall Tradeoff",
        template="plotly_dark",
    )
    return fig
```

### 7.4 Threshold Selection for Safety

In safety, the precision-recall tradeoff maps directly to business decisions:

| Operating Point | Threshold | Precision | Recall | Use Case |
|----------------|-----------|-----------|--------|----------|
| **Conservative** | 0.90 | Very high | Lower | Auto-remove content (no human review) |
| **Balanced** | 0.50 | Medium | Medium | Send to human review queue |
| **Aggressive** | 0.20 | Lower | High | Flag for monitoring, don't action |

The right threshold depends on:
- **Cost of false positives**: wrongly removing legitimate content → creator churn, appeal volume
- **Cost of false negatives**: missing violating content → user harm, regulatory risk
- **Review capacity**: how many items can human reviewers process per day

```python
def threshold_cost_analysis(y_true: np.ndarray, y_proba: np.ndarray,
                             cost_fp: float = 1.0, cost_fn: float = 10.0,
                             thresholds: np.ndarray = None) -> pd.DataFrame:
    """Find the threshold that minimizes total cost.

    cost_fp: cost per false positive (e.g., wrongly removing content)
    cost_fn: cost per false negative (e.g., missing a violation)
    """
    if thresholds is None:
        thresholds = np.arange(0.05, 0.96, 0.05)

    results = []
    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        fp = ((y_pred == 1) & (y_true == 0)).sum()
        fn = ((y_pred == 0) & (y_true == 1)).sum()
        tp = ((y_pred == 1) & (y_true == 1)).sum()
        tn = ((y_pred == 0) & (y_true == 0)).sum()

        total_cost = fp * cost_fp + fn * cost_fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        results.append({
            "threshold": round(t, 2),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "fp": fp, "fn": fn, "tp": tp, "tn": tn,
            "total_cost": round(total_cost, 2),
        })

    result_df = pd.DataFrame(results)
    min_cost_idx = result_df["total_cost"].idxmin()
    optimal = result_df.loc[min_cost_idx]
    print(f"Cost-optimal threshold: {optimal['threshold']:.2f} "
          f"(P={optimal['precision']:.3f}, R={optimal['recall']:.3f}, "
          f"Cost={optimal['total_cost']:.0f})")

    return result_df
```

### 7.5 Code: Class Imbalance Strategies

```python
def compare_imbalance_strategies(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """Compare different class imbalance strategies for safety classification.

    Strategies: baseline, scale_pos_weight, downsampling, SMOTE-like upsampling.
    """
    from sklearn.model_selection import cross_val_score

    ratio = (y == 0).sum() / max((y == 1).sum(), 1)
    results = []

    # Strategy 1: Baseline (no adjustment)
    model_base = xgb.XGBClassifier(n_estimators=100, random_state=42)
    auc = cross_val_score(model_base, X, y, cv=5, scoring="average_precision").mean()
    results.append({"strategy": "baseline", "auc_pr": round(auc, 4)})

    # Strategy 2: scale_pos_weight
    model_spw = xgb.XGBClassifier(n_estimators=100, scale_pos_weight=ratio,
                                   random_state=42)
    auc = cross_val_score(model_spw, X, y, cv=5, scoring="average_precision").mean()
    results.append({"strategy": "scale_pos_weight", "auc_pr": round(auc, 4)})

    # Strategy 3: Downsampling majority class
    n_minority = (y == 1).sum()
    majority_idx = y[y == 0].sample(n=n_minority, random_state=42).index
    minority_idx = y[y == 1].index
    balanced_idx = majority_idx.append(minority_idx)
    X_bal, y_bal = X.loc[balanced_idx], y.loc[balanced_idx]

    model_down = xgb.XGBClassifier(n_estimators=100, random_state=42)
    auc = cross_val_score(model_down, X_bal, y_bal, cv=5,
                          scoring="average_precision").mean()
    results.append({"strategy": "downsampling", "auc_pr": round(auc, 4)})

    # Strategy 4: Focal loss (XGBoost custom objective)
    def focal_loss_obj(y_pred, dtrain):
        y_true = dtrain.get_label()
        gamma = 2.0
        p = 1.0 / (1.0 + np.exp(-y_pred))
        grad = p - y_true  # simplified gradient
        hess = p * (1 - p)  # simplified hessian
        # Apply focal weighting
        focal_weight = np.where(y_true == 1, (1 - p) ** gamma, p ** gamma)
        grad *= focal_weight
        hess *= focal_weight
        return grad, hess

    model_focal = xgb.XGBClassifier(n_estimators=100, random_state=42,
                                     objective=focal_loss_obj)
    auc = cross_val_score(model_focal, X, y, cv=5,
                          scoring="average_precision").mean()
    results.append({"strategy": "focal_loss", "auc_pr": round(auc, 4)})

    return pd.DataFrame(results).sort_values("auc_pr", ascending=False)
```

**Interview Tip**: When discussing ML for safety, always connect model metrics to business
outcomes. "Improving recall from 0.85 to 0.90 means catching 5,000 more violating posts
per day, but the 2% precision drop adds 3,000 items to the human review queue. Given our
review capacity of 50K items/day, this tradeoff is worthwhile." This is product sense
applied to ML.

---

## Part 8: Experimental Flaws & Solutions

### 8.1 Common Experimental Flaws in Safety Experiments

| # | Flaw | Description | Detection | Fix |
|---|------|-------------|-----------|-----|
| 1 | **Network effects / SUTVA violation** | Treated user's behavior affects control users (e.g., hiding bad content from treatment group pushes bad actors to target control) | Compare within-cluster vs. across-cluster effects | Cluster randomization (randomize by region/creator network) |
| 2 | **Novelty / Hawthorne effect** | Users change behavior because they notice the change, not because of the intervention itself | Run longer; compare week 1 vs. week 4+ effects | Extended experiment duration; look for effect decay |
| 3 | **Sample Ratio Mismatch (SRM)** | Unequal group sizes indicate a logging or assignment bug | Chi-square test on group sizes | Fix the pipeline bug before analyzing |
| 4 | **Simpson's Paradox** | Aggregate effect reverses when segmented | Segment analysis by key dimensions | Analyze at the right granularity; weight appropriately |
| 5 | **Peeking / repeated significance testing** | Checking results early inflates false positive rate | Track how many times results were checked | Use sequential testing (mSPRT) or pre-register analysis time |
| 6 | **Survivorship bias** | Only analyzing users who stayed (ignoring churn caused by treatment) | Compare retention rates between groups first | Intent-to-treat analysis |
| 7 | **Interference between experiments** | Multiple concurrent experiments interact | Check overlap matrix; test for interactions | Isolation layers; stratified randomization |
| 8 | **Metric gaming** | Optimizing the metric rather than the underlying objective | Monitor proxy metrics and leading indicators | Use metric bundles; track guardrails |
| 9 | **Carryover effects** | Previous treatment affects current period in crossover designs | Include washout periods | Use parallel-group design instead |
| 10 | **Low statistical power** | Sample too small to detect real effects | Post-hoc power analysis; MDE calculation | Increase sample size; use CUPED; run longer |

### 8.2 Code: Detecting Experimental Flaws

```python
def experiment_health_check(df: pd.DataFrame, group_col: str = "group",
                             metric_cols: list[str] = None,
                             covariate_cols: list[str] = None) -> dict:
    """Comprehensive health check for an A/B experiment.

    Checks: SRM, covariate balance, novelty effects, and multiple testing.
    """
    from scipy.stats import chi2, ttest_ind, ks_2samp

    checks = {}
    groups = df[group_col].unique()
    if len(groups) != 2:
        return {"error": f"Expected 2 groups, found {len(groups)}"}

    ctrl = df[df[group_col] == groups[0]]
    treat = df[df[group_col] == groups[1]]

    # --- SRM Check ---
    n_ctrl, n_treat = len(ctrl), len(treat)
    total = n_ctrl + n_treat
    expected = total / 2
    chi2_stat = (n_ctrl - expected) ** 2 / expected + (n_treat - expected) ** 2 / expected
    srm_p = 1 - chi2.cdf(chi2_stat, df=1)
    checks["srm"] = {
        "n_control": n_ctrl, "n_treatment": n_treat,
        "ratio": round(n_treat / n_ctrl, 4),
        "p_value": round(srm_p, 6),
        "status": "FAIL" if srm_p < 0.001 else "PASS",
    }

    # --- Covariate Balance ---
    if covariate_cols:
        balance_checks = {}
        for col in covariate_cols:
            if df[col].dtype in ["float64", "int64"]:
                t_stat, p_val = ttest_ind(ctrl[col].dropna(), treat[col].dropna())
                balance_checks[col] = {
                    "ctrl_mean": round(ctrl[col].mean(), 4),
                    "treat_mean": round(treat[col].mean(), 4),
                    "p_value": round(p_val, 4),
                    "balanced": p_val > 0.05,
                }
        imbalanced = [c for c, v in balance_checks.items() if not v["balanced"]]
        checks["covariate_balance"] = {
            "details": balance_checks,
            "status": "FAIL" if len(imbalanced) > 0 else "PASS",
            "imbalanced_covariates": imbalanced,
        }

    # --- Novelty Effect Detection ---
    if "day" in df.columns and metric_cols:
        metric = metric_cols[0]
        early = df[df["day"] <= 3]
        late = df[df["day"] >= df["day"].max() - 3]

        early_effect = (early[early[group_col] == groups[1]][metric].mean()
                       - early[early[group_col] == groups[0]][metric].mean())
        late_effect = (late[late[group_col] == groups[1]][metric].mean()
                      - late[late[group_col] == groups[0]][metric].mean())

        checks["novelty_effect"] = {
            "early_effect": round(early_effect, 6),
            "late_effect": round(late_effect, 6),
            "effect_decay": round((early_effect - late_effect) / abs(early_effect) * 100, 1)
                           if early_effect != 0 else 0,
            "status": "WARN" if abs(early_effect) > 2 * abs(late_effect) else "PASS",
        }

    return checks
```

### 8.3 Code: Network Effect / SUTVA Violation Detection

```python
def detect_sutva_violation(df: pd.DataFrame, metric_col: str,
                            group_col: str, cluster_col: str) -> dict:
    """Detect SUTVA violations by comparing within-cluster vs. across-cluster effects.

    If SUTVA holds, the treatment effect should be similar whether we estimate
    it within clusters (some treated, some control) or across clusters.

    A large divergence suggests spillover / network effects.
    """
    from scipy.stats import ttest_ind

    # Overall treatment effect
    ctrl_all = df[df[group_col] == "control"][metric_col]
    treat_all = df[df[group_col] == "treatment"][metric_col]
    overall_effect = treat_all.mean() - ctrl_all.mean()

    # Within-cluster effects
    cluster_effects = []
    for cluster, grp in df.groupby(cluster_col):
        ctrl = grp[grp[group_col] == "control"][metric_col]
        treat = grp[grp[group_col] == "treatment"][metric_col]
        if len(ctrl) > 5 and len(treat) > 5:
            cluster_effects.append(treat.mean() - ctrl.mean())

    if len(cluster_effects) < 5:
        return {"error": "Too few clusters with both groups for analysis"}

    within_effect = np.mean(cluster_effects)
    within_se = np.std(cluster_effects) / np.sqrt(len(cluster_effects))

    divergence = abs(overall_effect - within_effect) / max(abs(within_se), 1e-6)

    return {
        "overall_effect": round(overall_effect, 4),
        "within_cluster_effect": round(within_effect, 4),
        "divergence_z": round(divergence, 2),
        "sutva_likely_violated": divergence > 2.0,
        "recommendation": (
            "Consider cluster-randomized design to account for spillovers."
            if divergence > 2.0
            else "No strong evidence of SUTVA violation."
        ),
    }
```

### 8.4 Summary: Experimental Flaw Playbook

When presented with an experiment in an interview, run through this mental checklist:

```
1. ASSIGNMENT: Is the randomization unit correct?
   □ SRM check (chi-square on group sizes)
   □ Covariate balance (t-tests on pre-experiment features)
   □ Are there concurrent experiments interfering?

2. MEASUREMENT: Are we measuring the right thing?
   □ Is the metric well-defined and consistently logged?
   □ Are there survivorship bias issues?
   □ Is the analysis unit = randomization unit?

3. VALIDITY: Are the results trustworthy?
   □ Novelty/Hawthorne effects (compare early vs. late treatment effect)
   □ SUTVA violations (within-cluster vs. overall effect)
   □ Multiple testing corrections applied?

4. INTERPRETATION: What do the results mean?
   □ Statistical vs. practical significance
   □ Simpson's paradox (check subgroup effects)
   □ Guardrail metrics all clear?

5. DECISION: What should we do?
   □ Clear recommendation with rationale
   □ Impact quantification (annual scale)
   □ Risks and monitoring plan for launch
```

**Interview Tip**: The strongest signal in a DS interview is catching a flaw that the
interviewer *embedded on purpose*. When given experiment results, don't immediately
interpret the treatment effect. Instead, walk through the checklist: "First, let me
check for SRM... next, covariate balance... is there evidence of novelty effects?"
This systematic approach demonstrates both rigor and experience.

---

## Quick Reference: When to Use What

| Scenario | Primary Method | Backup Method | Key Assumption |
|----------|---------------|---------------|----------------|
| Test a new feature | A/B Test | Quasi-experiment | SUTVA, no interference |
| Evaluate a launched policy | DID | Synthetic Control | Parallel trends |
| Threshold-based treatment | RDD | DID | No manipulation of running variable |
| Observational treatment | PSM / IPW | Doubly Robust | No unobserved confounders |
| Few treated units, long data | Synthetic Control | DID | Convex hull of donors |
| Detect behavior shifts | STL Anomaly Detection | CUSUM / EWMA | Stationary baseline |
| Classify content | XGBoost | Neural network | Labeled training data |
| Reduce experiment runtime | CUPED | Stratification | Strong pre/post correlation |
| Monitor during experiment | mSPRT | Alpha spending | Known variance |

---

## Cross-References

- **Statistical Foundations**: `statistical_foundations.md` — theory behind every method here
- **Product Sense**: `product_sense.md` — how to frame analysis results as product decisions
- **Main Guide**: `tiktok_integrity_safety.md` — Section 6 (A/B Testing), Section 7 (Causal Inference)
- **Notebook 05**: `../notebooks/05_ab_testing_lifecycle.ipynb` — full A/B test worked example
- **Notebook 06**: `../notebooks/06_causal_inference_lifecycle.ipynb` — full causal inference worked example
- **Notebook 07**: `../notebooks/07_metrics_experiment_design_lifecycle.ipynb` — metrics design + anomaly detection
