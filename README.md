# Data Scientist Interviews Prep Guide

Interview preparation materials for Data Scientist roles across multiple companies. Combines technical reference documents, worked examples, and executable Jupyter notebooks.

## Company Prep

### CarMax — Sr. Data Scientist, Pricing Algorithms
- [`CarMax/00_case_study_battle_card.md`](CarMax/00_case_study_battle_card.md) — Night-before cheat sheet: solved cases, mental math, frameworks
- [`CarMax/01_behavioral_prep.md`](CarMax/01_behavioral_prep.md) — STAR stories mapped to CarMax 8 competencies
- [`CarMax/02_business_context.md`](CarMax/02_business_context.md) — Business model, metrics, tech stack, FY2026 priorities
- [`CarMax/03_technical_deep_dives.md`](CarMax/03_technical_deep_dives.md) — Pricing model design, A/B testing, ML evaluation
- [`CarMax/04_mock_cases_practice.md`](CarMax/04_mock_cases_practice.md) — 5 timed practice cases with solutions

### TikTok — Integrity & Safety Data Scientist
- [`interview_prep/tiktok_integrity_safety.md`](interview_prep/tiktok_integrity_safety.md) — 4-round interview guide

## Technical Notebooks

| # | Notebook | Topics |
|---|----------|--------|
| 01 | [A/B Testing Foundations](notebooks/01_ab_testing_foundations.ipynb) | Z-tests, t-tests, sample size/power, CUPED, sequential testing, Thompson sampling, multiple testing |
| 02 | [Causal Inference Methods](notebooks/02_causal_inference_methods.ipynb) | DID, RDD, IV/2SLS, propensity score matching, IPW, DAGs |
| 03 | [Safety Metrics Design](notebooks/03_safety_metrics_design.ipynb) | Violation rate, precision/recall, time-to-action, anomaly detection |
| 04 | [Experiment Design](notebooks/04_experiment_design.ipynb) | Cluster randomization, sample size, phased rollouts, SRM checks |

## Project Structure

```
├── CarMax/                # CarMax Sr. DS Pricing Algorithms prep
├── interview_prep/        # Company-specific markdown prep guides
├── notebooks/             # Jupyter notebooks (run end-to-end)
├── data/generators/       # Synthetic data generators
├── utils/                 # Reusable analysis modules
├── context/               # Private reference materials (gitignored)
└── figures/               # Output plots
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

## Key Features

- **All synthetic data** — seeded generators, no real user data
- **From-scratch implementations** — statistical tests and causal estimators
- **Multi-company prep** — reusable frameworks across different DS roles
