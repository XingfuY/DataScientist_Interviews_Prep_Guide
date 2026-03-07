"""Safety metrics dashboard components using Plotly.

Provides reusable Plotly figure builders for trust and safety metrics
visualization.  All figures use a consistent dark theme with the I&S
brand color palette.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, Union


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

SAFETY_COLORS = {
    "primary": "#E91E63",     # Crimson
    "secondary": "#1565C0",   # Blue
    "background": "#0A1628",  # Navy
    "card": "#111D32",        # Navy-light
    "border": "#1A2A45",      # Navy-lighter
    "success": "#4CAF50",
    "warning": "#FF9800",
    "danger": "#F44336",
    "neutral": "#9E9E9E",
    "text": "#E0E0E0",
    "text_muted": "#90A4AE",
}

_CATEGORY_PALETTE = [
    "#E91E63", "#1E88E5", "#4CAF50", "#FF9800",
    "#AB47BC", "#26C6DA", "#FDD835", "#8D6E63",
]


# ---------------------------------------------------------------------------
# Shared layout helpers
# ---------------------------------------------------------------------------

def _dark_layout(**overrides) -> dict:
    """Return base Plotly layout kwargs for the dark theme."""
    defaults = {
        "paper_bgcolor": SAFETY_COLORS["background"],
        "plot_bgcolor": SAFETY_COLORS["card"],
        "font": dict(color=SAFETY_COLORS["text"], family="Inter, sans-serif"),
        "margin": dict(l=60, r=30, t=50, b=50),
        "legend": dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=SAFETY_COLORS["border"],
            borderwidth=1,
        ),
    }
    defaults.update(overrides)
    return defaults


def _dark_axis(title: Optional[str] = None, **overrides) -> dict:
    """Return axis styling for dark theme.

    Parameters
    ----------
    title : str, optional
        Axis title text.  The title font color is set automatically.
    """
    defaults = {
        "gridcolor": SAFETY_COLORS["border"],
        "zerolinecolor": SAFETY_COLORS["border"],
        "tickfont": dict(color=SAFETY_COLORS["text_muted"]),
    }
    if title is not None:
        defaults["title"] = dict(text=title, font=dict(color=SAFETY_COLORS["text"]))
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# 1. VVR trend with confidence bands
# ---------------------------------------------------------------------------

def plot_vvr_trend(
    dates: Union[pd.Series, np.ndarray, list],
    vvr_values: Union[pd.Series, np.ndarray, list],
    ci_lower: Optional[Union[pd.Series, np.ndarray, list]] = None,
    ci_upper: Optional[Union[pd.Series, np.ndarray, list]] = None,
) -> go.Figure:
    """Plot Violating View Rate (VVR) over time with optional confidence bands.

    Parameters
    ----------
    dates : array-like
        Date or time index values.
    vvr_values : array-like
        VVR metric values (fraction, e.g. 0.003 = 0.3 %).
    ci_lower, ci_upper : array-like, optional
        Lower and upper confidence band values.

    Returns
    -------
    go.Figure
    """
    dates = np.asarray(dates)
    vvr_values = np.asarray(vvr_values)

    fig = go.Figure()

    # Confidence band (filled area)
    if ci_lower is not None and ci_upper is not None:
        ci_lower = np.asarray(ci_lower)
        ci_upper = np.asarray(ci_upper)
        fig.add_trace(go.Scatter(
            x=np.concatenate([dates, dates[::-1]]),
            y=np.concatenate([ci_upper, ci_lower[::-1]]),
            fill="toself",
            fillcolor="rgba(233,30,99,0.15)",
            line=dict(color="rgba(0,0,0,0)"),
            name="95% CI",
            showlegend=True,
            hoverinfo="skip",
        ))

    # Main VVR line
    fig.add_trace(go.Scatter(
        x=dates,
        y=vvr_values,
        mode="lines+markers",
        line=dict(color=SAFETY_COLORS["primary"], width=2.5),
        marker=dict(size=4),
        name="VVR",
    ))

    fig.update_layout(
        title="Violating View Rate (VVR) Trend",
        xaxis=_dark_axis(title="Date"),
        yaxis=_dark_axis(title="VVR", tickformat=".4f"),
        **_dark_layout(),
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Violation breakdown by category
# ---------------------------------------------------------------------------

def plot_violation_breakdown(
    categories: Union[pd.Series, np.ndarray, list],
    counts: Union[pd.Series, np.ndarray, list, pd.DataFrame],
    colors: Optional[list] = None,
) -> go.Figure:
    """Stacked bar chart of violations by category.

    If ``counts`` is a 2-D array or DataFrame (categories x time periods),
    each column becomes a stacked segment.  If 1-D, a simple bar chart is
    produced.

    Parameters
    ----------
    categories : array-like
        Category labels for the x-axis.
    counts : array-like or DataFrame
        Violation counts.  Shape ``(n_categories,)`` for simple bars or
        ``(n_categories, n_segments)`` for stacked bars.
    colors : list, optional
        Bar colors; defaults to the built-in palette.

    Returns
    -------
    go.Figure
    """
    categories = list(categories)
    colors = colors or _CATEGORY_PALETTE

    fig = go.Figure()

    if isinstance(counts, pd.DataFrame):
        for j, col in enumerate(counts.columns):
            fig.add_trace(go.Bar(
                x=categories,
                y=counts[col].values,
                name=str(col),
                marker_color=colors[j % len(colors)],
            ))
        fig.update_layout(barmode="stack")
    else:
        counts_arr = np.asarray(counts)
        if counts_arr.ndim == 2:
            for j in range(counts_arr.shape[1]):
                fig.add_trace(go.Bar(
                    x=categories,
                    y=counts_arr[:, j],
                    name=f"Segment {j + 1}",
                    marker_color=colors[j % len(colors)],
                ))
            fig.update_layout(barmode="stack")
        else:
            fig.add_trace(go.Bar(
                x=categories,
                y=counts_arr,
                marker_color=[
                    colors[i % len(colors)] for i in range(len(categories))
                ],
                showlegend=False,
            ))

    fig.update_layout(
        title="Violation Breakdown by Category",
        xaxis=_dark_axis(title="Category"),
        yaxis=_dark_axis(title="Count"),
        **_dark_layout(),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Precision-recall curve
# ---------------------------------------------------------------------------

def plot_precision_recall(
    precisions: Union[pd.Series, np.ndarray, list],
    recalls: Union[pd.Series, np.ndarray, list],
    thresholds: Union[pd.Series, np.ndarray, list],
) -> go.Figure:
    """Interactive precision-recall curve with threshold annotations.

    Parameters
    ----------
    precisions : array-like
        Precision values at each threshold.
    recalls : array-like
        Recall values at each threshold.
    thresholds : array-like
        Threshold values (same length as precisions and recalls).

    Returns
    -------
    go.Figure
    """
    precisions = np.asarray(precisions)
    recalls = np.asarray(recalls)
    thresholds = np.asarray(thresholds)

    # F1 score
    f1 = np.where(
        (precisions + recalls) > 0,
        2 * precisions * recalls / (precisions + recalls),
        0.0,
    )
    best_f1_idx = np.argmax(f1)

    fig = go.Figure()

    # PR curve
    fig.add_trace(go.Scatter(
        x=recalls,
        y=precisions,
        mode="lines",
        line=dict(color=SAFETY_COLORS["primary"], width=2.5),
        name="PR Curve",
        customdata=np.stack([thresholds, f1], axis=-1),
        hovertemplate=(
            "Recall: %{x:.3f}<br>"
            "Precision: %{y:.3f}<br>"
            "Threshold: %{customdata[0]:.3f}<br>"
            "F1: %{customdata[1]:.3f}<extra></extra>"
        ),
    ))

    # Best F1 marker
    fig.add_trace(go.Scatter(
        x=[recalls[best_f1_idx]],
        y=[precisions[best_f1_idx]],
        mode="markers+text",
        marker=dict(
            size=12, color=SAFETY_COLORS["success"],
            symbol="star", line=dict(width=1, color="white"),
        ),
        text=[f"Best F1={f1[best_f1_idx]:.3f}\nt={thresholds[best_f1_idx]:.3f}"],
        textposition="top right",
        textfont=dict(color=SAFETY_COLORS["success"], size=11),
        name="Best F1",
    ))

    # Annotate a few threshold points
    n_points = len(thresholds)
    annotation_indices = np.linspace(0, n_points - 1, min(6, n_points), dtype=int)
    for idx in annotation_indices:
        fig.add_annotation(
            x=recalls[idx],
            y=precisions[idx],
            text=f"t={thresholds[idx]:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=0.8,
            arrowcolor=SAFETY_COLORS["text_muted"],
            font=dict(size=9, color=SAFETY_COLORS["text_muted"]),
            ax=20,
            ay=-20,
        )

    fig.update_layout(
        title="Precision-Recall Curve",
        xaxis=_dark_axis(title="Recall", range=[0, 1.05]),
        yaxis=_dark_axis(title="Precision", range=[0, 1.05]),
        **_dark_layout(),
    )
    return fig


# ---------------------------------------------------------------------------
# 4. Time-to-action distribution
# ---------------------------------------------------------------------------

def plot_time_to_action(
    times: Union[pd.Series, np.ndarray, list],
    percentiles: Optional[list] = None,
) -> go.Figure:
    """Histogram of time-to-action with percentile markers.

    Parameters
    ----------
    times : array-like
        Time-to-action values (e.g. hours).
    percentiles : list of int, optional
        Percentiles to annotate.  Defaults to [50, 90, 95, 99].

    Returns
    -------
    go.Figure
    """
    if percentiles is None:
        percentiles = [50, 90, 95, 99]

    times = np.asarray(times, dtype=float)
    times = times[~np.isnan(times)]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=times,
        nbinsx=60,
        marker_color=SAFETY_COLORS["secondary"],
        opacity=0.85,
        name="Distribution",
    ))

    # Percentile lines
    pct_colors = {
        50: SAFETY_COLORS["success"],
        90: SAFETY_COLORS["warning"],
        95: SAFETY_COLORS["danger"],
        99: SAFETY_COLORS["primary"],
    }
    for pct in percentiles:
        val = float(np.percentile(times, pct))
        color = pct_colors.get(pct, SAFETY_COLORS["neutral"])
        fig.add_vline(
            x=val,
            line=dict(color=color, width=2, dash="dash"),
            annotation_text=f"P{pct}: {val:.1f}",
            annotation_font=dict(color=color, size=11),
            annotation_position="top right",
        )

    fig.update_layout(
        title="Time-to-Action Distribution",
        xaxis=_dark_axis(title="Time to Action (hours)"),
        yaxis=_dark_axis(title="Count"),
        **_dark_layout(),
    )
    return fig


# ---------------------------------------------------------------------------
# 5. Regional enforcement heatmap
# ---------------------------------------------------------------------------

def plot_regional_heatmap(
    regions: Union[pd.Series, np.ndarray, list],
    categories: Union[pd.Series, np.ndarray, list],
    rates: Union[pd.DataFrame, np.ndarray],
) -> go.Figure:
    """Heatmap of enforcement rates by region x category.

    Parameters
    ----------
    regions : array-like
        Row labels (region names).
    categories : array-like
        Column labels (violation categories).
    rates : DataFrame or 2-D array
        Enforcement rates matrix, shape ``(n_regions, n_categories)``.

    Returns
    -------
    go.Figure
    """
    regions = list(regions)
    categories = list(categories)

    if isinstance(rates, pd.DataFrame):
        z = rates.values
    else:
        z = np.asarray(rates)

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=categories,
        y=regions,
        colorscale=[
            [0.0, SAFETY_COLORS["card"]],
            [0.5, SAFETY_COLORS["secondary"]],
            [1.0, SAFETY_COLORS["primary"]],
        ],
        colorbar=dict(
            title=dict(text="Rate", font=dict(color=SAFETY_COLORS["text"])),
            tickfont=dict(color=SAFETY_COLORS["text_muted"]),
        ),
        text=np.round(z, 3).astype(str),
        texttemplate="%{text}",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "Region: %{y}<br>"
            "Category: %{x}<br>"
            "Rate: %{z:.4f}<extra></extra>"
        ),
    ))

    fig.update_layout(
        title="Regional Enforcement Rates",
        xaxis=_dark_axis(title="Violation Category"),
        yaxis=_dark_axis(title="Region"),
        **_dark_layout(),
    )
    return fig


# ---------------------------------------------------------------------------
# 6. Anomaly detection timeline
# ---------------------------------------------------------------------------

def plot_anomaly_timeline(
    dates: Union[pd.Series, np.ndarray, list],
    values: Union[pd.Series, np.ndarray, list],
    anomaly_flags: Union[pd.Series, np.ndarray, list],
    method: str = "ewma",
) -> go.Figure:
    """Time series with detected anomalies highlighted.

    Parameters
    ----------
    dates : array-like
        Date or time index values.
    values : array-like
        Metric values.
    anomaly_flags : array-like
        Boolean array where True marks an anomaly.
    method : str
        Detection method label (for display only).  One of
        ``'ewma'``, ``'isolation_forest'``, ``'zscore'``.

    Returns
    -------
    go.Figure
    """
    dates = np.asarray(dates)
    values = np.asarray(values, dtype=float)
    anomaly_flags = np.asarray(anomaly_flags, dtype=bool)

    fig = go.Figure()

    # Normal points
    normal_mask = ~anomaly_flags
    fig.add_trace(go.Scatter(
        x=dates[normal_mask],
        y=values[normal_mask],
        mode="lines+markers",
        line=dict(color=SAFETY_COLORS["secondary"], width=1.5),
        marker=dict(size=3),
        name="Normal",
    ))

    # Anomaly points
    if anomaly_flags.any():
        fig.add_trace(go.Scatter(
            x=dates[anomaly_flags],
            y=values[anomaly_flags],
            mode="markers",
            marker=dict(
                size=10,
                color=SAFETY_COLORS["danger"],
                symbol="x",
                line=dict(width=2, color=SAFETY_COLORS["danger"]),
            ),
            name=f"Anomaly ({anomaly_flags.sum()})",
        ))

    # EWMA baseline if method is ewma
    if method == "ewma" and len(values) > 1:
        span = max(5, len(values) // 10)
        ewma = pd.Series(values).ewm(span=span).mean().values
        ewma_std = pd.Series(values).ewm(span=span).std().values
        upper = ewma + 2 * ewma_std
        lower = ewma - 2 * ewma_std

        fig.add_trace(go.Scatter(
            x=dates,
            y=ewma,
            mode="lines",
            line=dict(color=SAFETY_COLORS["warning"], width=1.5, dash="dot"),
            name="EWMA",
        ))
        fig.add_trace(go.Scatter(
            x=np.concatenate([dates, dates[::-1]]),
            y=np.concatenate([upper, lower[::-1]]),
            fill="toself",
            fillcolor="rgba(255,152,0,0.10)",
            line=dict(color="rgba(0,0,0,0)"),
            name="2-sigma band",
            hoverinfo="skip",
        ))

    method_labels = {
        "ewma": "EWMA",
        "isolation_forest": "Isolation Forest",
        "zscore": "Z-Score",
    }
    method_label = method_labels.get(method, method)

    fig.update_layout(
        title=f"Anomaly Detection Timeline ({method_label})",
        xaxis=_dark_axis(title="Date"),
        yaxis=_dark_axis(title="Value"),
        **_dark_layout(),
    )
    return fig


# ---------------------------------------------------------------------------
# 7. Combined 6-panel dashboard
# ---------------------------------------------------------------------------

def create_safety_dashboard(metrics_df: pd.DataFrame) -> go.Figure:
    """Create a 6-panel safety metrics dashboard.

    Expects ``metrics_df`` to contain the following columns (all optional;
    panels with missing data are left blank):

    - ``date`` : datetime-like — time index
    - ``vvr`` : float — Violating View Rate
    - ``vvr_ci_lower``, ``vvr_ci_upper`` : float — VVR confidence bands
    - ``violation_category`` : str — category labels for breakdown
    - ``violation_count`` : int — counts per category
    - ``precision``, ``recall``, ``threshold`` : float — PR curve data
    - ``time_to_action`` : float — hours to moderation action
    - ``region`` : str, ``enforcement_category`` : str, ``enforcement_rate`` : float
    - ``anomaly_flag`` : bool — whether date is an anomaly

    Panels:
        1. VVR trend with confidence bands (top-left)
        2. Violation breakdown by category (top-right)
        3. Precision-recall curve (middle-left)
        4. Time-to-action distribution (middle-right)
        5. Regional enforcement heatmap (bottom-left)
        6. Anomaly detection timeline (bottom-right)

    Parameters
    ----------
    metrics_df : pd.DataFrame
        Combined metrics data.

    Returns
    -------
    go.Figure
        A 3x2 subplot figure.
    """
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[
            "VVR Trend", "Violation Breakdown",
            "Precision-Recall", "Time-to-Action",
            "Regional Enforcement", "Anomaly Timeline",
        ],
        specs=[
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "heatmap"}, {"type": "xy"}],
        ],
        vertical_spacing=0.10,
        horizontal_spacing=0.08,
    )

    # --- Panel 1: VVR trend ---
    if "date" in metrics_df.columns and "vvr" in metrics_df.columns:
        vvr_data = metrics_df.dropna(subset=["vvr"]).sort_values("date")
        dates = vvr_data["date"].values
        vvr = vvr_data["vvr"].values

        if "vvr_ci_lower" in vvr_data.columns and "vvr_ci_upper" in vvr_data.columns:
            ci_lo = vvr_data["vvr_ci_lower"].values
            ci_hi = vvr_data["vvr_ci_upper"].values
            fig.add_trace(go.Scatter(
                x=np.concatenate([dates, dates[::-1]]),
                y=np.concatenate([ci_hi, ci_lo[::-1]]),
                fill="toself",
                fillcolor="rgba(233,30,99,0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                hoverinfo="skip",
            ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=dates, y=vvr,
            mode="lines+markers",
            line=dict(color=SAFETY_COLORS["primary"], width=2),
            marker=dict(size=3),
            showlegend=False,
        ), row=1, col=1)

    # --- Panel 2: Violation breakdown ---
    if "violation_category" in metrics_df.columns and "violation_count" in metrics_df.columns:
        breakdown = (
            metrics_df
            .dropna(subset=["violation_category", "violation_count"])
            .groupby("violation_category")["violation_count"]
            .sum()
            .sort_values(ascending=False)
        )
        fig.add_trace(go.Bar(
            x=breakdown.index.tolist(),
            y=breakdown.values,
            marker_color=[
                _CATEGORY_PALETTE[i % len(_CATEGORY_PALETTE)]
                for i in range(len(breakdown))
            ],
            showlegend=False,
        ), row=1, col=2)

    # --- Panel 3: Precision-recall ---
    if all(c in metrics_df.columns for c in ["precision", "recall", "threshold"]):
        pr_data = metrics_df.dropna(subset=["precision", "recall"]).sort_values("recall")
        fig.add_trace(go.Scatter(
            x=pr_data["recall"].values,
            y=pr_data["precision"].values,
            mode="lines",
            line=dict(color=SAFETY_COLORS["primary"], width=2),
            showlegend=False,
        ), row=2, col=1)

    # --- Panel 4: Time-to-action ---
    if "time_to_action" in metrics_df.columns:
        tta = metrics_df["time_to_action"].dropna().values
        fig.add_trace(go.Histogram(
            x=tta,
            nbinsx=40,
            marker_color=SAFETY_COLORS["secondary"],
            opacity=0.85,
            showlegend=False,
        ), row=2, col=2)

    # --- Panel 5: Regional heatmap ---
    if all(c in metrics_df.columns for c in [
        "region", "enforcement_category", "enforcement_rate"
    ]):
        pivot = (
            metrics_df
            .dropna(subset=["region", "enforcement_category", "enforcement_rate"])
            .pivot_table(
                index="region",
                columns="enforcement_category",
                values="enforcement_rate",
                aggfunc="mean",
            )
        )
        fig.add_trace(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[
                [0.0, SAFETY_COLORS["card"]],
                [0.5, SAFETY_COLORS["secondary"]],
                [1.0, SAFETY_COLORS["primary"]],
            ],
            showscale=False,
        ), row=3, col=1)

    # --- Panel 6: Anomaly timeline ---
    if "date" in metrics_df.columns and "anomaly_flag" in metrics_df.columns:
        anom_data = metrics_df.dropna(subset=["anomaly_flag"]).sort_values("date")
        metric_col = "vvr" if "vvr" in anom_data.columns else None
        if metric_col:
            vals = anom_data[metric_col].values
            flags = anom_data["anomaly_flag"].astype(bool).values
            d = anom_data["date"].values

            fig.add_trace(go.Scatter(
                x=d[~flags], y=vals[~flags],
                mode="lines+markers",
                line=dict(color=SAFETY_COLORS["secondary"], width=1.5),
                marker=dict(size=3),
                showlegend=False,
            ), row=3, col=2)

            if flags.any():
                fig.add_trace(go.Scatter(
                    x=d[flags], y=vals[flags],
                    mode="markers",
                    marker=dict(
                        size=8, color=SAFETY_COLORS["danger"], symbol="x",
                    ),
                    showlegend=False,
                ), row=3, col=2)

    # --- Global layout ---
    fig.update_layout(
        height=900,
        width=1200,
        title=dict(
            text="Safety Metrics Dashboard",
            font=dict(size=18, color=SAFETY_COLORS["text"]),
        ),
        showlegend=False,
        **_dark_layout(),
    )

    # Apply dark axis styling to all subplots
    for i in range(1, 4):
        for j in range(1, 3):
            axis_suffix = "" if (i == 1 and j == 1) else str((i - 1) * 2 + j)
            x_key = f"xaxis{axis_suffix}"
            y_key = f"yaxis{axis_suffix}"
            fig.update_layout(**{
                x_key: _dark_axis(),
                y_key: _dark_axis(),
            })

    return fig
