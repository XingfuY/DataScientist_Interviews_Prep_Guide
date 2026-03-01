# Data

All data used in this project is **synthetically generated** — no real user data, no PII, no proprietary datasets.

## Generators (`generators/`)

| Module | Purpose |
|--------|---------|
| `content_moderation.py` | Content stream with violations, classifier predictions, moderation actions |
| `user_behavior.py` | User cohorts with engagement metrics, risk scores, demographics |
| `policy_experiments.py` | A/B test data with treatment effects and covariates (for CUPED) |
| `safety_incidents.py` | Time series with anomalies (spikes, drift, change points) |

## Usage

```python
from data.generators import content_moderation as cm

df = cm.generate_content_stream(n_items=50000, violation_rate=0.03)
```
