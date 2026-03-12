# CarMax Sr. Data Scientist (Pricing Algorithms) — Technical Deep Dives

**Purpose**: Super Day / later-round preparation. Comprehensive technical material for
system design, modeling, experimentation, and coding questions specific to CarMax's
pricing domain.

---

## 1. PRICING MODEL DESIGN — FROM SCRATCH

**Prompt to anticipate**: "Walk me through how you would build CarMax's vehicle pricing model from the ground up."

This is the flagship question. It tests breadth (do you understand the full ML lifecycle?)
and depth (can you handle the gnarly details of vehicle pricing specifically?).

### 1.1 Problem Framing

**Core formulation**: regression problem predicting the optimal retail price for each
individual vehicle in CarMax's inventory.

But "optimal" is the tricky word. Naive framing: predict the transaction price a vehicle
will sell at. Better framing: predict the price that maximizes expected gross profit
considering both margin and time-to-sale.

**Objective function**:

```
maximize E[Gross Profit] = E[(Price - Cost - Reconditioning - Holding Cost) * P(sale within T days | Price)]
```

This is NOT standard regression. You are jointly modeling:
1. The price a customer is willing to pay (demand curve)
2. The cost of holding inventory (financing, depreciation, lot space)
3. The probability of sale at any given price point within a time window

**Key insight for the interview**: the objective is total portfolio profit, not per-unit
profit. A car priced $200 below maximum extractable value but selling 10 days faster
may generate more profit after accounting for holding costs and capital freed up to
acquire the next vehicle.

**Constraints**:
- **Fairness / brand consistency**: CarMax's entire brand is "no-haggle, fair price."
  Prices must feel fair to customers — no predatory pricing on low-information buyers.
  This is a real constraint, not just marketing. If a customer finds the same car $3K
  cheaper at a competitor, brand trust erodes.
- **Competitive positioning**: prices must be within a reasonable band of KBB, Edmunds,
  and local competitor listings. Persistent overpricing kills traffic.
- **Profitability floor**: minimum gross profit per unit (GPPU) to cover overhead. This
  floor varies by vehicle segment.
- **Regulatory**: some states have pricing disclosure requirements. Equal credit
  opportunity considerations if pricing interacts with financing.

**Practical simplification**: in practice, most teams decompose this into:
1. A market value model (what is this car worth?)
2. A pricing strategy layer (given market value, what should we list at?)
3. A markdown policy (how should we adjust price over time?)

### 1.2 Feature Engineering

This is where domain knowledge separates a good answer from a great one. The features
below are organized by category with CarMax-specific considerations.

#### Vehicle Attributes (structured, well-defined)

| Feature | Notes |
|---------|-------|
| Make / Model / Year | Categorical — use target encoding or embeddings, NOT one-hot (too many levels) |
| Trim level | Critical — a fully loaded trim can be 30-40% more than base |
| Mileage | Non-linear effect — 30K to 60K is a smaller penalty than 90K to 120K |
| Exterior color | Affects resale: white/black/silver are neutral; orange/yellow carry discounts |
| Interior color | Tan/black preferred; unusual colors reduce demand |
| Engine type | V6 vs V8, turbo, hybrid, EV — each has different demand curve |
| Transmission | Manual vs automatic (manuals are niche — lower demand but dedicated buyers) |
| Drivetrain | AWD/4WD premium in northern markets, less in southern |
| Body style | Sedan vs SUV vs truck — macro demand shifts matter here |
| Number of previous owners | Each additional owner reduces value |
| VIN-decoded features | Factory options, packages — decoded from VIN using third-party API |

**Encoding strategy for make/model/year**: these interact heavily. A 2020 Toyota Camry
and a 2020 BMW 3-series have completely different depreciation curves. Options:
- Concatenate into a single high-cardinality feature, use target encoding
- Hierarchical encoding: make-level embedding + model-level embedding + year
- Learn embeddings in a neural network and extract for use in gradient boosting

#### Condition Features (partially structured, noisy)

| Feature | Notes |
|---------|-------|
| Reconditioning cost estimate | Strong signal — high recon cost = problems |
| Accident history (CarFax) | Number of accidents, severity, which panels |
| Title status | Clean, salvage, rebuilt, lemon — massive price impact |
| Inspection grade | Internal grading from CarMax inspection |
| Tire condition | Remaining tread depth — signals overall maintenance |
| Paint condition | Chips, scratches, fading |
| Interior wear | Stains, tears, odor — hard to quantify |
| Mechanical issues | Engine codes, transmission health, suspension |

**NLP opportunity**: inspection notes are often free-text. Extract features via:
- Keyword matching for common issues ("timing belt," "brake pads," "AC not blowing cold")
- Sentiment/severity scoring
- Named entity recognition for parts mentioned

#### Market Features (external, time-varying)

| Feature | Notes |
|---------|-------|
| KBB / Edmunds fair market value | Baseline benchmark — feature, not target |
| Auction prices (Manheim index) | Wholesale market signal |
| Local competitor listings | Same make/model/year within radius |
| Number of comparable listings | Supply signal |
| Fuel prices | Affects SUV/truck vs sedan demand |
| Interest rates | Higher rates suppress demand for expensive vehicles |
| Consumer confidence index | Macro demand signal |
| New vehicle inventory levels | Chip shortage era proved this matters enormously |

**Competitor price features** require careful engineering:
- Median competitor price for same make/model/year/trim within 50-mile radius
- Percentile rank of CarMax price vs competitors
- Number of competitors with same vehicle
- Days-on-market for competitor listings (if available)

#### Temporal Features

| Feature | Notes |
|---------|-------|
| Day of week | Weekend traffic is higher — affects demand, not necessarily optimal price |
| Month / season | Tax refund season (Feb-Apr) spikes demand, especially for cheaper vehicles |
| Days since acquisition | Holding cost increases; urgency to sell rises |
| Days since last price change | Staleness signal |
| Market trend (7-day, 30-day) | Is the market for this segment rising or falling? |
| Holiday proximity | Memorial Day, July 4th, Black Friday — known demand events |

**Critical time-based leakage warning**: if you train on historical transactions, the
actual days-on-lot at time of sale is a label, not a feature. At prediction time you
only know days-on-lot so far. Use acquisition date and current date, not sale date.

#### Geographic Features

| Feature | Notes |
|---------|-------|
| Store market (DMA) | Different price levels by metro |
| Zip code median income | Proxy for willingness to pay |
| Local unemployment rate | Economic health |
| Urban vs suburban vs rural | Different vehicle preferences |
| Climate / weather patterns | AWD premium in snow states; convertible premium in warm |
| State tax and registration | Affects total cost of ownership |
| Proximity to competing dealers | Competition density |

#### Derived / Interaction Features

These are often the most powerful and show the interviewer you think beyond raw columns:

| Feature | Formula / Logic |
|---------|----------------|
| Mileage per year | `mileage / (current_year - model_year)` — high = harder use |
| Price-to-market ratio | `our_price / market_avg_price` — competitive position |
| Demand velocity | Rate of inquiries/test drives for comparable vehicles |
| Depreciation curve position | Where on the typical 5-year curve is this vehicle? |
| Segment popularity trend | Is this segment gaining or losing share? (EV trend, SUV shift) |
| Recon cost as % of expected price | Flags "not worth reconditioning" vehicles |
| Local supply-demand ratio | `n_comparable_listings / n_recent_comparable_sales` |
| Make reliability score | Consumer Reports / JD Power — proxy for maintenance anxiety |

### 1.3 Model Selection

**Primary model: gradient boosted trees (LightGBM or XGBoost)**

Why this is the right starting point:
- Tabular data with mixed types (numeric + high-cardinality categorical) — this is
  exactly the domain where GBTs dominate. Every Kaggle benchmark confirms it.
- Handles missing values natively (LightGBM especially).
- Captures non-linear relationships and interactions without explicit feature crossing.
  Example: mileage impact depends on vehicle age — a 2-year-old car with 80K miles is
  penalized much more than a 10-year-old car with 80K miles. GBTs learn this naturally.
- Fast training and inference — important for real-time pricing at scale.
- Highly interpretable via SHAP values — critical for explaining prices to business
  stakeholders and regulators.

**Why NOT linear regression alone**:
- The relationship between features and price is deeply non-linear. A Corolla with 50K
  miles is not worth exactly twice a Corolla with 100K miles minus a constant.
- Interaction effects are everywhere. Color matters more for sports cars than minivans.
  AWD premium is geography-dependent.
- You would need hundreds of hand-crafted polynomial and interaction terms to approximate
  what a GBT learns automatically.
- That said, linear regression is useful as a baseline and for interpretability in
  sub-segments.

**When to consider neural networks**:
- If you have massive data (tens of millions of transactions) and want to learn
  embeddings for make/model/trim that capture latent similarity.
- If you want to incorporate unstructured data (vehicle images, listing descriptions,
  inspection notes) alongside structured features — multimodal models.
- TabNet or similar architectures that compete with GBTs on tabular data while providing
  attention-based feature selection.
- For the demand model component, where you need to model a distribution, not just a
  point estimate — mixture density networks.

**Ensemble strategies**:
- Blend a GBT and a neural network (simple weighted average of predictions).
- Train separate models per vehicle segment (luxury, economy, truck, SUV, EV) and route
  at inference time. This lets each model specialize.
- Stack: use GBT predictions as a feature in a second-level model.

**Models to avoid (and why)**:
- Random forest alone: GBTs consistently outperform on structured tabular data.
- SVM: doesn't scale, poor with mixed feature types.
- K-nearest neighbors: tempting for "find similar cars" but doesn't generalize well,
  and inference cost is O(n) with the dataset.

### 1.4 Training Strategy

**Data split: time-based, not random**

Random splitting causes temporal leakage. If you randomly mix January and June transactions,
the model can "peek" at future market conditions when predicting January prices.

Correct approach:
- Train: all transactions before date T1 (e.g., 18 months of history)
- Validation: transactions from T1 to T2 (e.g., next 3 months)
- Test: transactions from T2 to T3 (e.g., most recent 3 months)

For cross-validation, use expanding window or sliding window:
- Fold 1: train on months 1-12, validate on 13-15
- Fold 2: train on months 1-15, validate on 16-18
- Fold 3: train on months 1-18, validate on 19-21

**Handling rare vehicles (cold-start problem)**:

Some vehicles appear rarely in the training data: exotic brands, unusual trims, very old
or very new models. Strategies:
- Hierarchical smoothing: for a rare trim, blend the trim-level estimate with the
  model-level estimate. For a rare model, blend with the make-level estimate.
- Use vehicle similarity embeddings — a rare Maserati Ghibli can borrow signal from
  other luxury sport sedans.
- Augment with auction data (Manheim, ADESA) which has broader coverage.
- Set a minimum confidence threshold — below it, flag for human review.

**Retraining cadence**:

The used car market is non-stationary. Prices fluctuate with seasons, economic cycles,
and supply shocks (e.g., pandemic-era chip shortage inflated used car prices 30-40%).

- Full retrain: weekly or biweekly with latest transaction data.
- Online updates: daily incremental updates with most recent transactions using warm-start.
- Feature refresh: market features (competitor prices, fuel prices) update in real-time
  or daily.
- Model versioning: keep the previous N models so you can roll back if a new model
  degrades.

**Feature importance analysis**:

After training, produce:
- Global feature importance (gain-based and SHAP-based) — shows what drives prices overall.
- Per-segment importance — features that matter for trucks may differ from sedans.
- SHAP dependence plots for top features — reveals the shape of each feature's effect.

Share these with business stakeholders. If the model says "exterior color is the #3 most
important feature," that should match business intuition. If not, investigate.

### 1.5 Evaluation Metrics

#### Offline Metrics

| Metric | Formula | Why It Matters |
|--------|---------|---------------|
| MAPE | `mean(abs(predicted - actual) / actual)` | Interpretable: "our model is off by X% on average" |
| MAE | `mean(abs(predicted - actual))` | Dollar-level accuracy |
| RMSE | `sqrt(mean((predicted - actual)^2))` | Penalizes large errors more — a $5K miss is worse than five $1K misses |
| % within $500 | `mean(abs(predicted - actual) < 500)` | Practical accuracy bucket |
| % within $1000 | Same, wider bucket | |
| Median absolute error | 50th percentile of abs errors | Robust to outliers |
| R-squared | Variance explained | Overall fit — should be >0.95 for vehicle pricing |

**Segment-level evaluation**: aggregate metrics can hide poor performance on specific
segments. Always break down by:
- Price tier (economy <$15K, mid $15-30K, luxury >$30K)
- Body style
- Age bracket
- Volume vs rare vehicles

A model with 3% overall MAPE might have 2% MAPE on common Civics but 15% MAPE on rare
luxury vehicles. The business cares about both.

#### Business Metrics (online evaluation)

| Metric | Definition | Target Direction |
|--------|-----------|-----------------|
| GPPU (Gross Profit Per Unit) | Revenue - cost - recon per vehicle | Maximize |
| Days to sale | Time from listing to transaction | Minimize |
| Sell-through rate | % of inventory sold within N days | Maximize |
| Price adjustment frequency | How often we reprice a vehicle | Minimize (get it right the first time) |
| Customer price satisfaction | Survey / NPS component | Maximize |
| Return rate | % of vehicles returned within guarantee period | Minimize |

**Offline vs online evaluation gap**: a model with lower MAPE might actually hurt business
metrics if it systematically underprices high-demand vehicles (sells fast but leaves money
on the table) or overprices slow segments (great margin on paper but cars sit on lot).

Always run A/B tests (Section 2) before declaring a new model superior.

### 1.6 Deployment & Monitoring

**Real-time vs batch scoring**:
- Batch: run the model nightly on all inventory. Simple, debuggable, sufficient if prices
  don't need intra-day updates.
- Real-time: score on demand when a vehicle is acquired, when market data changes, or
  when a customer views a listing. Needed for dynamic pricing.
- Hybrid: batch baseline with real-time adjustments for rapid market moves.

**Serving architecture**:
```
[Feature Store] --> [Model Server (FastAPI/TF Serving)] --> [Pricing API]
                                                               |
                                    [Business Rules Engine] <--+
                                    (min margin, max price, competitive bounds)
                                               |
                                    [Price Database] --> [Website / Sales System]
```

**Model monitoring**:
- **Data drift**: are input feature distributions shifting? Monitor with PSI (Population
  Stability Index) or KS test. If mileage distribution shifts (e.g., fleet vehicles
  flooding market), the model may need retraining.
- **Prediction drift**: are model outputs shifting even if inputs look stable? Could
  indicate a subtle data quality issue.
- **Performance drift**: track MAPE on recent transactions vs prediction at listing time.
  If accuracy degrades beyond a threshold, trigger retraining.
- **Feature freshness**: are market features (competitor prices, auction indices) updating
  on schedule? Stale features cause silent degradation.

**A/B testing new models**: see Section 2 for details. Never hard-cut to a new model —
always validate in production with a controlled experiment.

**Fallback strategies**:
- If the model server goes down, fall back to the most recent batch scores.
- If batch scores are stale (>48 hours), fall back to a simple rule-based model
  (market average + segment adjustment).
- If a prediction has very low confidence (wide prediction interval), flag for human
  pricing analyst review.

---

## 2. A/B TESTING FOR PRICING

Pricing A/B tests are among the hardest experiments in industry. The interviewer is
testing whether you understand why standard A/B testing breaks down for pricing.

### 2.1 Why Pricing A/B Tests Are Uniquely Challenging

**Problem 1: you cannot show different prices to different customers for the same car.**
Unlike a website button color test where each user sees their own version, a car has
ONE listed price. If customer A sees $25,000 and customer B sees $24,500 for the same
VIN, that violates CarMax's no-haggle promise and potentially fair pricing regulations.

**Problem 2: SUTVA violations (Stable Unit Treatment Value Assumption).** SUTVA requires
that one unit's treatment doesn't affect another unit's outcome. In pricing:
- If CarMax lowers prices in Market A, customers in Market B (control) might drive to
  Market A, contaminating both groups.
- Competitors observe and respond to CarMax price changes, affecting the entire market.
- A price change on one vehicle affects demand for substitute vehicles on the same lot.

**Problem 3: small sample sizes.** Each store sells maybe 300-500 cars per month. You
can't split a single store's inventory into treatment/control because of Problem 1.
So the unit of randomization is the store or market — and CarMax has ~240 stores.
That's a small N for statistical power.

**Problem 4: long feedback cycles.** A car might sit on the lot for 30-60 days. To
measure the full effect of a pricing change, you need to observe complete sales cycles,
which means experiments run for months.

### 2.2 Randomization Strategies

**Store-level randomization**:
- Randomly assign stores to treatment (new pricing model) and control (current model).
- Pros: clean separation, no cross-contamination within store.
- Cons: stores differ in location, demographics, competition — high variance between
  units. Need many stores per arm for balance.

**Market-level randomization**:
- Group stores into geographic markets (DMAs). Randomize at market level.
- Pros: reduces cross-store contamination (customers less likely to cross market
  boundaries). Captures local competitive dynamics.
- Cons: even fewer units (maybe 50-80 markets). Very low power.

**Vehicle-segment randomization within store**:
- Within each store, apply new pricing to SUVs (treatment) and old pricing to sedans
  (control). Or randomize by acquisition cohort.
- Pros: larger effective sample, controls for store-level effects.
- Cons: cross-segment spillover (customer who came for a mispriced SUV buys a sedan
  instead), potential selection bias.

**Matched-pair design**:
- Pair similar stores (same market size, demographics, volume). Within each pair,
  randomly assign one to treatment and one to control.
- Pros: dramatically reduces variance by controlling for store-level confounders.
- Cons: imperfect matching, loss of degrees of freedom.

**Best practice**: matched-pair store-level randomization with stratification on store
volume, market size, and geographic region.

### 2.3 Measuring Incrementality

The question is not "did stores with new pricing sell more?" but "did the new pricing
model CAUSE more profit than the old model would have generated?"

**Difference-in-differences (DiD)**:
- Compare the change in the treatment group's metrics vs the change in the control
  group's metrics, relative to a pre-experiment baseline.
- Controls for pre-existing differences between groups.
- Requires parallel trends assumption: absent treatment, both groups would have followed
  the same trajectory.

**Regression adjustment**:
- Fit a model: `outcome = beta_0 + beta_1 * treatment + beta_2 * covariates + epsilon`
- Covariates include store-level characteristics, pre-experiment performance, and market
  conditions.
- The treatment effect is `beta_1`, adjusted for observable confounders.

**Synthetic control method** (when randomization is infeasible):
- If you can only test in one market (e.g., pilot in Charlotte), construct a synthetic
  Charlotte from a weighted combination of untreated markets that matches Charlotte's
  pre-period trajectory.
- Compare Charlotte's post-treatment outcomes to synthetic Charlotte's.
- Excellent when you have a long pre-period and few treatment units.

### 2.4 Sample Size and Duration

**Power calculation for store-level experiments**:

Inputs:
- Minimum detectable effect (MDE): what is the smallest improvement worth detecting?
  For GPPU, maybe $50/unit. For days-to-sale, maybe 1 day.
- Baseline variability: standard deviation of the metric across stores.
- Number of stores available.
- Desired power (typically 80%) and significance level (typically 5%).

For a two-sample t-test at the store level:
```
n_per_arm = 2 * (z_alpha/2 + z_beta)^2 * sigma^2 / delta^2
```

With high store-level variance and small MDE, you often need more stores than you have.
Solutions:
- Increase MDE (accept that you can only detect large effects).
- Increase experiment duration to reduce within-store noise through averaging.
- Use covariates (CUPED: Controlled-experiment Using Pre-Experiment Data) to reduce
  variance by 20-50%.

**Duration considerations**:
- Minimum 4-6 weeks for a pricing experiment (need full sales cycles).
- 8-12 weeks preferred to capture seasonal effects and customer decision timelines.
- Pre-experiment period should be at least as long as the experiment for DiD.

### 2.5 Guardrail Metrics

While the primary metric is GPPU or total gross profit, monitor these guardrails to
ensure the new pricing model isn't winning on profit by destroying other value:

- **Customer satisfaction (NPS / survey scores)**: are customers happy with the prices?
- **Return rate**: are customers experiencing buyer's remorse at higher prices?
- **Traffic and test drives**: are higher prices reducing lot traffic?
- **Time-to-sale distribution**: not just the mean — is the tail getting longer (some
  cars sitting way too long)?
- **Wholesale loss rate**: are more cars being sent to auction because they won't sell?
- **Employee satisfaction**: are sales consultants getting negative customer feedback?

### 2.6 Common Pitfalls

- **Peeking**: checking results daily and stopping early when p < 0.05 inflates false
  positive rate. Use sequential testing (e.g., always-valid p-values) if you must
  monitor continuously.
- **Ignoring novelty effects**: a price drop might spike short-term demand that doesn't
  sustain. Run long enough to reach steady state.
- **Confounding with marketing**: if a marketing campaign coincides with the experiment
  in treatment stores, you can't separate the effects.
- **Contamination**: customers shopping across stores, or sales staff learning about the
  experiment and changing behavior.

---

## 3. DEMAND FORECASTING

### 3.1 Why Demand Forecasting Matters for Pricing

You cannot set optimal prices without understanding demand. The price that maximizes
profit depends on how many customers want the vehicle at each price point (the demand
curve). Demand forecasting feeds directly into the pricing model's "time-to-sale"
component.

### 3.2 Time Series Approaches

**ARIMA / SARIMAX**:
- Good for capturing trend and seasonality in aggregate demand (total units sold per
  week at a market level).
- SARIMAX adds exogenous variables (marketing spend, economic indicators).
- Limitation: univariate — doesn't naturally incorporate the rich feature set of
  vehicle attributes.

**Prophet (Meta)**:
- Additive decomposition: trend + seasonality + holidays + regressors.
- Handles missing data and outliers robustly.
- Good for aggregate forecasts (market-level or segment-level demand).
- Easy to incorporate CarMax-specific events (sale events, store openings).

**LSTM / Temporal Fusion Transformer**:
- For learning complex temporal patterns across multiple related time series.
- TFT is current state-of-the-art for multi-horizon forecasting with mixed inputs.
- Can jointly forecast demand across all vehicle segments, sharing information.
- Higher complexity — justified only with sufficient data and engineering resources.

### 3.3 Feature-Based Demand Models

Instead of pure time series, model demand as a function of features:
```
demand(vehicle_segment, market, time) = f(price, season, economic_indicators,
                                          competitor_supply, marketing, ...)
```

This is often more useful than pure time series because:
- It directly estimates price elasticity (how demand changes with price).
- It can forecast demand for NEW segments or markets without historical data.
- It naturally incorporates exogenous variables.

Model choices: Poisson regression (count data), negative binomial, or gradient boosted
trees with a Poisson objective.

### 3.4 Granularity Hierarchy

Forecast at multiple levels and reconcile:
1. **National**: total CarMax demand. Driven by macro factors.
2. **Market/DMA**: regional demand. Driven by local economy, weather, competition.
3. **Store**: individual store demand. Driven by store capacity, local marketing.
4. **Segment**: demand for SUVs vs sedans vs trucks at each store.
5. **Make-model**: demand for specific vehicles. Very noisy at fine grain.

Use hierarchical reconciliation (top-down, bottom-up, or optimal reconciliation via
MinT) to ensure forecasts are coherent across levels.

### 3.5 Incorporating External Signals

| Signal | Source | Latency | Impact |
|--------|--------|---------|--------|
| Gas prices | EIA weekly | 1 week | Shifts demand between segments |
| Interest rates | Federal Reserve | Real-time | Affects affordability |
| Consumer confidence | Conference Board | Monthly | Leading indicator |
| Unemployment claims | Dept of Labor | Weekly | Economic health |
| New vehicle inventory | OEM reports | Monthly | Substitution pressure |
| Competitor pricing | Web scraping | Daily | Direct competitive effect |
| Weather forecasts | NOAA | Hourly | Short-term traffic impact |
| Tax refund timing | IRS data | Annual | Seasonal demand spike |

### 3.6 Forecast Accuracy Metrics

| Metric | Use Case |
|--------|----------|
| MAPE | Overall accuracy, interpretable |
| WMAPE (Weighted MAPE) | Weighted by volume — errors on high-volume segments matter more |
| Bias (mean error) | Are we systematically over- or under-forecasting? |
| Coverage of prediction interval | Do 80% of actuals fall within our 80% PI? |
| CRPS (Continuous Ranked Probability Score) | Evaluates the full predictive distribution |

---

## 4. DYNAMIC PRICING STRATEGY

### 4.1 Price Markdown Curves

Every vehicle depreciates while sitting on CarMax's lot. The longer it sits, the more it
costs in financing, insurance, lot space, and depreciation. Dynamic pricing accounts for
this through a structured markdown schedule.

**Typical markdown pattern**:
- Days 0-14: list at full model-recommended price. Fresh inventory generates organic
  interest.
- Days 15-30: first markdown if no strong interest. Typically 1-3% reduction.
- Days 31-45: second markdown. 3-5% cumulative from original price.
- Days 46-60: aggressive markdown. 5-10% cumulative. Urgency increases.
- Days 60+: evaluate whether to continue marking down or send to wholesale auction.

The optimal markdown schedule is NOT one-size-fits-all. It depends on:
- Vehicle segment (trucks hold value differently than sedans)
- Local market demand (hot markets need fewer markdowns)
- Acquisition cost (more headroom = slower markdown)
- Season (approaching winter? SUV demand is rising)

### 4.2 Optimal Price Path

Model this as a dynamic programming / sequential decision problem:

At each time step t, choose price P(t) to maximize:
```
V(t) = max_P { P(sale at time t | P) * (P - cost - holding_cost(t))
              + P(no sale at t | P) * discount_factor * V(t+1) }
```

Base case: at the maximum holding period T_max, the vehicle goes to wholesale auction at
the expected auction price minus transport costs.

This is a stochastic dynamic programming problem. Approximate solutions:
- Discretize the price space and solve with backward induction.
- Use reinforcement learning (contextual bandits or full RL) to learn the markdown policy.
- Simpler: fit a parametric markdown curve (exponential decay) and optimize its parameters.

### 4.3 Wholesale Decision Point

A critical business decision: when is it more profitable to send a vehicle to wholesale
auction rather than continue marking it down on the retail lot?

```
if E[retail_profit | continued_markdown] < E[auction_price - transport_cost]:
    send to auction
```

This requires:
- Accurate retail demand forecasting at current and reduced prices.
- Accurate auction price prediction (Manheim auction data is helpful).
- Proper accounting for opportunity cost (the lot space could hold a faster-selling car).

### 4.4 Price Elasticity Estimation

Price elasticity of demand: % change in quantity demanded per % change in price.

**Methods**:
- **Historical regression**: regress log(sales_velocity) on log(price), controlling for
  vehicle and market characteristics. Endogeneity is a problem — prices are set in
  response to demand, creating reverse causality.
- **Instrumental variables**: use cost shocks (unexpected reconditioning costs, auction
  price spikes) as instruments for price. These affect price but shouldn't directly
  affect demand.
- **Experimental estimates**: use A/B test data (Section 2) to estimate causal
  elasticities. Gold standard but expensive.
- **Difference-in-differences**: exploit policy changes (e.g., a new markdown schedule
  rolled out in some markets) as quasi-experiments.

**Key findings** (typical for used auto):
- Overall demand elasticity is around -1.5 to -2.5 (elastic — price drops generate
  more-than-proportional demand increases).
- Luxury vehicles are less elastic (buyers are less price-sensitive).
- Economy vehicles are more elastic (buyers are very price-sensitive).
- Elasticity varies by days-on-lot: fresh inventory is less elastic (new = exciting),
  aged inventory is more elastic (buyers know it's sat there).

### 4.5 Multi-Objective Optimization

The pricing team must balance competing objectives:

| Objective | Metric | Tension |
|-----------|--------|---------|
| Maximize margin | GPPU | Higher prices = slower sales |
| Maximize velocity | Days to sale | Lower prices = lower margin |
| Maximize throughput | Units sold/month | Need balance of both |
| Minimize wholesale losses | Auction rate | Aggressive pricing moves more units but hurts margin |
| Maintain brand trust | Customer satisfaction | Over-pricing erodes trust |

**Pareto optimization**: find the set of pricing policies where improving one objective
necessarily worsens another. Let the business choose the operating point on the Pareto
frontier.

**Practical approach**: define a single composite objective with business-specified weights:
```
score = w1 * normalized_GPPU + w2 * normalized_velocity - w3 * wholesale_rate
```

Let leadership set w1, w2, w3 based on strategic priorities. During a recession, they
might favor velocity. During a seller's market, favor margin.

---

## 5. RECOMMENDATION ENGINE

### 5.1 Use Cases at CarMax

- **Website**: "Similar vehicles you might like" on vehicle detail pages.
- **Email**: "New inventory matching your saved searches."
- **In-store**: sales consultant tablet — suggest alternatives when first-choice is
  unavailable.
- **Search ranking**: re-rank search results based on user's predicted preferences.

### 5.2 Collaborative Filtering

**User-based**: customers similar to you (based on browsing/purchase history) liked these
vehicles. Use cosine similarity on user-vehicle interaction vectors.

**Item-based**: vehicles similar to the one you're viewing (based on co-viewing patterns).
If users who viewed Vehicle A also viewed Vehicle B frequently, recommend B.

**Matrix factorization**: decompose the user-vehicle interaction matrix into latent
factors using ALS or SVD. Each vehicle and user gets a latent vector; the dot product
predicts interaction strength.

**Challenges at CarMax**:
- Sparse interactions — most users view 5-20 vehicles out of 50K+ inventory.
- Inventory turnover — vehicles sell and leave, new ones arrive. Cold start constantly.
- Implicit feedback only — views, searches, saves. No explicit ratings.

### 5.3 Content-Based Filtering

Represent each vehicle by its features (make, model, year, price, body style, etc.).
Recommend vehicles that are feature-similar to what the user has engaged with.

**Advantages**:
- No cold-start problem for new inventory — features are known immediately.
- Transparent — "We recommended this because it's also a mid-size SUV under $30K."
- Works for anonymous users if you have current-session behavior.

**Limitations**:
- Doesn't capture taste that isn't reflected in explicit features.
- Tends to recommend very similar items (filter bubble).

### 5.4 Hybrid Approach

In practice, combine both:
1. Content-based for new inventory and anonymous users.
2. Collaborative filtering for returning users with history.
3. A blending layer (learned weights or a re-ranking model) that combines both signals
   with business rules.

### 5.5 Interaction with Pricing

This is a subtle but important point for CarMax:
- Don't systematically recommend underpriced vehicles first. If the recommendation
  engine always surfaces the best "deals," it trains customers to wait for price drops.
- Don't recommend vehicles far above the user's apparent budget — it creates frustration.
- Consider the profit margin in ranking. A vehicle with 15% margin that the customer
  would love is a better recommendation than one with 3% margin of equal appeal.
- This does NOT mean manipulative upselling. It means, among equally relevant
  recommendations, prefer higher-margin options. The customer is well-served by any of
  them.

---

## 6. ML SYSTEM DESIGN INTERVIEW PATTERNS

### 6.1 Real-Time Pricing API Design

**Problem**: design a system that returns the recommended price for a vehicle in <100ms.

**Architecture**:

```
                        +-------------------+
                        |  Pricing Client   |
                        |  (Web/Mobile/POS) |
                        +--------+----------+
                                 |
                                 v
                        +--------+----------+
                        |  API Gateway      |
                        |  (rate limiting,  |
                        |   auth, routing)  |
                        +--------+----------+
                                 |
                    +------------+------------+
                    |                         |
                    v                         v
          +---------+--------+    +----------+---------+
          | Feature Service  |    | Business Rules     |
          | (assembles       |    | Engine             |
          | feature vector   |    | (min/max, rounding,|
          | from stores)     |    |  competitive       |
          +---------+--------+    |  bounds)           |
                    |             +----------+---------+
                    v                        ^
          +---------+--------+               |
          | Model Serving    +---------------+
          | (LightGBM/       |  raw prediction
          | TorchServe)      |
          +------------------+
```

**Feature service**: pre-computes and caches features in a feature store (Redis/Feast).
Vehicle attributes are static after acquisition. Market features update hourly/daily.
At request time, assemble the feature vector by joining cached features.

**Model serving**: load the serialized model into memory. LightGBM inference on a
single row is <1ms. Use multiple replicas behind a load balancer for throughput.

**Business rules engine**: applies post-model adjustments:
- Round to nearest $100 (aesthetic pricing)
- Enforce minimum gross profit floor
- Cap price at N% above market to maintain competitiveness
- Apply promotional discounts if applicable

**Caching**: cache predictions for vehicles whose features haven't changed. Invalidate
when market features refresh or the vehicle crosses a time threshold.

### 6.2 Feature Store Architecture

**Why a feature store**: features used in training must exactly match features used in
serving. A feature store is the single source of truth.

**Components**:
- **Offline store** (data warehouse — BigQuery, Snowflake, Redshift): stores historical
  feature values for training data generation. Supports point-in-time lookups to prevent
  leakage.
- **Online store** (Redis, DynamoDB): stores latest feature values for real-time serving.
  Low-latency key-value lookups.
- **Feature computation pipeline** (Spark, Flink, or dbt): transforms raw data into
  features on a schedule or in streaming mode.
- **Registry**: metadata about each feature — owner, description, data type, freshness
  SLA, lineage.

### 6.3 Model Serving Infrastructure

**Options**:
- **BentoML / MLflow Serving**: package model + preprocessing into a Docker container.
  Deploy on Kubernetes with auto-scaling.
- **TorchServe / TF Serving**: for deep learning models with batching and GPU inference.
- **SageMaker Endpoints**: managed serving on AWS.
- **Custom FastAPI**: for maximum control. Wrap model in a Python API with health
  checks, metrics, and A/B routing.

**Considerations**:
- **Latency**: P99 latency budget. Feature assembly is usually the bottleneck, not
  model inference.
- **Throughput**: 50K daily listings means ~0.6 QPS at steady state, but bursts during
  batch reruns can be 10-100x.
- **Versioning**: serve multiple model versions simultaneously for A/B testing. Route
  traffic by store/market assignment.
- **Canary deploys**: roll out new model to 5% of traffic, monitor for regressions,
  gradually increase.

### 6.4 Data Pipeline: Acquisition to Pricing

```
[Vehicle Acquired at Auction/Customer Trade-in]
    |
    v
[Intake System] --> vehicle attributes, VIN decode, photos
    |
    v
[Inspection & Reconditioning] --> condition features, recon cost
    |
    v
[Feature Pipeline] --> joins market data, competitor prices, demand signals
    |
    v
[Model Scoring] --> recommended price
    |
    v
[Business Rules] --> adjusted price
    |
    v
[Price Published] --> website, in-store systems, third-party listings
    |
    v
[Monitoring] --> track views, inquiries, test drives, sales
    |
    v
[Feedback Loop] --> transaction data feeds back into training set
```

### 6.5 Monitoring and Alerting

| Monitor | Metric | Alert Threshold |
|---------|--------|----------------|
| Model latency | P99 response time | > 200ms |
| Prediction distribution | Mean / stddev of predicted prices | > 2 sigma shift from baseline |
| Feature freshness | Time since last update per feature | > SLA (e.g., 24h for market features) |
| Error rate | HTTP 5xx rate | > 0.1% |
| Data quality | Null rate per feature | > 5% for any critical feature |
| Business metric | Daily GPPU | > 10% drop from trailing average |
| Drift | PSI per feature | > 0.25 (severe drift) |

---

## 7. SQL & PYTHON CODING PATTERNS

### 7.1 SQL Patterns

**Window functions for running averages**:

```sql
-- 30-day rolling average price by make/model
SELECT
    make,
    model,
    sale_date,
    sale_price,
    AVG(sale_price) OVER (
        PARTITION BY make, model
        ORDER BY sale_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_avg_price,
    COUNT(*) OVER (
        PARTITION BY make, model
        ORDER BY sale_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30d_sales_count
FROM transactions
WHERE sale_date >= '2025-01-01'
ORDER BY make, model, sale_date;
```

**Self-join for cross-store comparison**:

```sql
-- Find vehicles priced differently across stores for the same make/model/year/trim
SELECT
    a.store_id AS store_a,
    b.store_id AS store_b,
    a.make, a.model, a.year, a.trim,
    a.list_price AS price_a,
    b.list_price AS price_b,
    ABS(a.list_price - b.list_price) AS price_diff
FROM inventory a
JOIN inventory b
    ON a.make = b.make
    AND a.model = b.model
    AND a.year = b.year
    AND a.trim = b.trim
    AND a.store_id < b.store_id  -- avoid duplicates
WHERE a.status = 'active'
    AND b.status = 'active'
    AND ABS(a.mileage - b.mileage) < 5000  -- comparable mileage
ORDER BY price_diff DESC
LIMIT 50;
```

**Conditional aggregation with CASE WHEN**:

```sql
-- Sales mix and margin by price tier
SELECT
    store_id,
    COUNT(*) AS total_sales,
    SUM(CASE WHEN sale_price < 15000 THEN 1 ELSE 0 END) AS economy_sales,
    SUM(CASE WHEN sale_price BETWEEN 15000 AND 30000 THEN 1 ELSE 0 END) AS mid_sales,
    SUM(CASE WHEN sale_price > 30000 THEN 1 ELSE 0 END) AS luxury_sales,
    AVG(CASE WHEN sale_price < 15000 THEN gross_profit END) AS economy_avg_gp,
    AVG(CASE WHEN sale_price BETWEEN 15000 AND 30000 THEN gross_profit END) AS mid_avg_gp,
    AVG(CASE WHEN sale_price > 30000 THEN gross_profit END) AS luxury_avg_gp
FROM transactions
WHERE sale_date >= DATE_ADD(CURRENT_DATE, INTERVAL -90 DAY)
GROUP BY store_id
ORDER BY total_sales DESC;
```

**Date arithmetic for days-on-lot**:

```sql
-- Inventory aging report with markdown triggers
SELECT
    vin,
    make, model, year,
    list_price,
    acquisition_date,
    DATEDIFF(CURRENT_DATE, acquisition_date) AS days_on_lot,
    CASE
        WHEN DATEDIFF(CURRENT_DATE, acquisition_date) <= 14 THEN 'Fresh'
        WHEN DATEDIFF(CURRENT_DATE, acquisition_date) <= 30 THEN 'Standard'
        WHEN DATEDIFF(CURRENT_DATE, acquisition_date) <= 45 THEN 'Aging'
        WHEN DATEDIFF(CURRENT_DATE, acquisition_date) <= 60 THEN 'Stale'
        ELSE 'Wholesale Candidate'
    END AS aging_bucket,
    num_price_changes,
    original_list_price,
    original_list_price - list_price AS total_markdown
FROM inventory
WHERE status = 'active'
ORDER BY days_on_lot DESC;
```

**Subquery for above/below market pricing**:

```sql
-- Vehicles priced more than 5% above market average
WITH market_avgs AS (
    SELECT
        make, model, year, trim,
        AVG(list_price) AS avg_market_price,
        STDDEV(list_price) AS stddev_price,
        COUNT(*) AS comparable_count
    FROM (
        SELECT make, model, year, trim, list_price
        FROM inventory WHERE status = 'active'
        UNION ALL
        SELECT make, model, year, trim, list_price
        FROM competitor_listings WHERE scraped_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
    ) combined
    GROUP BY make, model, year, trim
    HAVING COUNT(*) >= 5  -- enough comparables
)
SELECT
    i.vin,
    i.make, i.model, i.year, i.trim,
    i.list_price,
    m.avg_market_price,
    ROUND((i.list_price - m.avg_market_price) / m.avg_market_price * 100, 1) AS pct_above_market,
    m.comparable_count
FROM inventory i
JOIN market_avgs m
    ON i.make = m.make AND i.model = m.model AND i.year = m.year AND i.trim = m.trim
WHERE i.status = 'active'
    AND i.list_price > m.avg_market_price * 1.05
ORDER BY pct_above_market DESC;
```

**Ranking and percentile analysis**:

```sql
-- Price percentile rank within segment for competitive analysis
SELECT
    vin,
    make, model, year,
    list_price,
    PERCENT_RANK() OVER (
        PARTITION BY make, model, year
        ORDER BY list_price
    ) AS price_percentile,
    NTILE(4) OVER (
        PARTITION BY make, model, year
        ORDER BY list_price
    ) AS price_quartile
FROM inventory
WHERE status = 'active'
ORDER BY make, model, year, list_price;
```

### 7.2 Python Patterns

**Feature engineering pipeline**:

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw vehicle data into model-ready features.
    Assumes df has columns: make, model, year, mileage, acquisition_date, etc.
    """
    df = df.copy()

    # Mileage per year (avoid division by zero for current-year vehicles)
    vehicle_age = pd.Timestamp.now().year - df['year']
    df['mileage_per_year'] = df['mileage'] / vehicle_age.clip(lower=1)

    # Age-mileage interaction
    df['age_mileage_interaction'] = vehicle_age * np.log1p(df['mileage'])

    # Days since acquisition
    df['days_since_acquisition'] = (
        pd.Timestamp.now() - pd.to_datetime(df['acquisition_date'])
    ).dt.days

    # Holding cost estimate (simplified)
    daily_holding_cost = 15  # $/day — financing + depreciation + lot cost
    df['estimated_holding_cost'] = df['days_since_acquisition'] * daily_holding_cost

    # Recon cost as fraction of estimated value
    df['recon_cost_ratio'] = df['reconditioning_cost'] / df['estimated_market_value'].clip(lower=1000)

    # Season encoding
    acquisition_month = pd.to_datetime(df['acquisition_date']).dt.month
    df['is_tax_season'] = acquisition_month.isin([2, 3, 4]).astype(int)
    df['is_summer'] = acquisition_month.isin([6, 7, 8]).astype(int)

    # Cyclical month encoding
    df['month_sin'] = np.sin(2 * np.pi * acquisition_month / 12)
    df['month_cos'] = np.cos(2 * np.pi * acquisition_month / 12)

    # Local market competitiveness
    df['supply_demand_ratio'] = (
        df['comparable_listings_count'] / df['comparable_sales_30d'].clip(lower=1)
    )

    # Depreciation curve position (approximate)
    typical_5yr_depreciation = 0.60  # vehicles lose ~60% over 5 years
    annual_depreciation_rate = 1 - (1 - typical_5yr_depreciation) ** (1/5)
    df['expected_depreciation_pct'] = 1 - (1 - annual_depreciation_rate) ** vehicle_age

    return df
```

**Model training with time-based split**:

```python
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import numpy as np

def train_pricing_model(df: pd.DataFrame, feature_cols: list, target_col: str = 'sale_price'):
    """
    Train a LightGBM pricing model with proper time-based splitting.
    """
    df = df.sort_values('sale_date')

    # Time-based split: 70% train, 15% val, 15% test
    n = len(df)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]

    print(f"Train: {train['sale_date'].min()} to {train['sale_date'].max()} ({len(train)} rows)")
    print(f"Val:   {val['sale_date'].min()} to {val['sale_date'].max()} ({len(val)} rows)")
    print(f"Test:  {test['sale_date'].min()} to {test['sale_date'].max()} ({len(test)} rows)")

    # Create LightGBM datasets
    dtrain = lgb.Dataset(train[feature_cols], train[target_col])
    dval = lgb.Dataset(val[feature_cols], val[target_col], reference=dtrain)

    params = {
        'objective': 'regression',
        'metric': ['mae', 'mape'],
        'learning_rate': 0.05,
        'num_leaves': 127,
        'max_depth': -1,
        'min_child_samples': 50,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'verbose': -1,
    }

    model = lgb.train(
        params,
        dtrain,
        num_boost_round=2000,
        valid_sets=[dtrain, dval],
        valid_names=['train', 'val'],
        callbacks=[
            lgb.early_stopping(50),
            lgb.log_evaluation(100),
        ],
    )

    # Evaluate on test set
    test_preds = model.predict(test[feature_cols])
    test_mae = mean_absolute_error(test[target_col], test_preds)
    test_mape = mean_absolute_percentage_error(test[target_col], test_preds)
    within_500 = np.mean(np.abs(test[target_col].values - test_preds) < 500)
    within_1000 = np.mean(np.abs(test[target_col].values - test_preds) < 1000)

    print(f"\nTest Results:")
    print(f"  MAE:           ${test_mae:,.0f}")
    print(f"  MAPE:          {test_mape:.2%}")
    print(f"  Within $500:   {within_500:.1%}")
    print(f"  Within $1000:  {within_1000:.1%}")

    return model, test_preds
```

**SHAP-based model interpretability**:

```python
import shap

def explain_prediction(model, feature_cols, vehicle_features: pd.DataFrame):
    """
    Generate SHAP explanation for a single vehicle's predicted price.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(vehicle_features[feature_cols])

    # Base value (average prediction)
    base_value = explainer.expected_value

    # Top factors pushing price up
    feature_impacts = pd.DataFrame({
        'feature': feature_cols,
        'shap_value': shap_values[0],
        'feature_value': vehicle_features[feature_cols].values[0],
    }).sort_values('shap_value', key=abs, ascending=False)

    print(f"Base price: ${base_value:,.0f}")
    print(f"Predicted price: ${base_value + shap_values[0].sum():,.0f}")
    print(f"\nTop price drivers:")
    for _, row in feature_impacts.head(10).iterrows():
        direction = "+" if row['shap_value'] > 0 else ""
        print(f"  {row['feature']}: {direction}${row['shap_value']:,.0f} "
              f"(value: {row['feature_value']})")

    return feature_impacts
```

**Evaluation metric implementation**:

```python
def pricing_evaluation_report(y_true, y_pred, segment_labels=None):
    """
    Comprehensive evaluation report for a pricing model.
    """
    errors = y_true - y_pred
    abs_errors = np.abs(errors)
    pct_errors = abs_errors / y_true

    report = {
        'n': len(y_true),
        'mae': np.mean(abs_errors),
        'median_ae': np.median(abs_errors),
        'rmse': np.sqrt(np.mean(errors ** 2)),
        'mape': np.mean(pct_errors),
        'median_ape': np.median(pct_errors),
        'within_500': np.mean(abs_errors < 500),
        'within_1000': np.mean(abs_errors < 1000),
        'within_2000': np.mean(abs_errors < 2000),
        'bias': np.mean(errors),  # positive = model overestimates
        'max_overestimate': errors.max(),
        'max_underestimate': errors.min(),
    }

    print("=" * 50)
    print("PRICING MODEL EVALUATION REPORT")
    print("=" * 50)
    print(f"Sample size:         {report['n']:,}")
    print(f"MAE:                 ${report['mae']:,.0f}")
    print(f"Median AE:           ${report['median_ae']:,.0f}")
    print(f"RMSE:                ${report['rmse']:,.0f}")
    print(f"MAPE:                {report['mape']:.2%}")
    print(f"Median APE:          {report['median_ape']:.2%}")
    print(f"Within $500:         {report['within_500']:.1%}")
    print(f"Within $1,000:       {report['within_1000']:.1%}")
    print(f"Within $2,000:       {report['within_2000']:.1%}")
    print(f"Bias:                ${report['bias']:+,.0f}")
    print(f"Max overestimate:    ${report['max_overestimate']:+,.0f}")
    print(f"Max underestimate:   ${report['max_underestimate']:+,.0f}")

    # Segment-level breakdown
    if segment_labels is not None:
        print(f"\n{'Segment':<20} {'N':>6} {'MAE':>10} {'MAPE':>8} {'<$1K':>8}")
        print("-" * 52)
        for segment in sorted(set(segment_labels)):
            mask = segment_labels == segment
            seg_mae = np.mean(abs_errors[mask])
            seg_mape = np.mean(pct_errors[mask])
            seg_within_1k = np.mean(abs_errors[mask] < 1000)
            print(f"{segment:<20} {mask.sum():>6} ${seg_mae:>8,.0f} {seg_mape:>7.1%} {seg_within_1k:>7.1%}")

    return report
```

**Data cleaning patterns**:

```python
def clean_vehicle_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standard cleaning pipeline for vehicle transaction data.
    """
    df = df.copy()
    initial_rows = len(df)

    # Remove obvious data entry errors
    df = df[df['sale_price'] > 1000]           # filter out $1 test entries
    df = df[df['sale_price'] < 200000]         # filter out extreme outliers
    df = df[df['mileage'] >= 0]                # negative mileage is a data error
    df = df[df['mileage'] < 300000]            # extremely high mileage — unreliable
    df = df[df['year'] >= 2000]                # very old vehicles have different dynamics
    df = df[df['year'] <= pd.Timestamp.now().year + 1]  # can't be future year + 1

    # Handle missing values strategically
    # Mileage: impute with median for same make/model/year
    df['mileage'] = df.groupby(['make', 'model', 'year'])['mileage'].transform(
        lambda x: x.fillna(x.median())
    )
    # If still missing (no group match), use global median
    df['mileage'] = df['mileage'].fillna(df['mileage'].median())

    # Reconditioning cost: missing likely means not yet inspected — flag it
    df['recon_cost_missing'] = df['reconditioning_cost'].isna().astype(int)
    df['reconditioning_cost'] = df['reconditioning_cost'].fillna(
        df.groupby('body_style')['reconditioning_cost'].transform('median')
    )

    # Standardize categorical values
    df['make'] = df['make'].str.upper().str.strip()
    df['model'] = df['model'].str.upper().str.strip()
    df['exterior_color'] = df['exterior_color'].str.lower().str.strip()

    # Map rare colors to 'other'
    color_counts = df['exterior_color'].value_counts()
    rare_colors = color_counts[color_counts < 100].index
    df.loc[df['exterior_color'].isin(rare_colors), 'exterior_color'] = 'other'

    rows_removed = initial_rows - len(df)
    print(f"Cleaned: {initial_rows:,} -> {len(df):,} rows ({rows_removed:,} removed, "
          f"{rows_removed/initial_rows:.1%})")

    return df
```

---

## 8. STATISTICAL CONCEPTS TO KNOW

### 8.1 Hypothesis Testing

**Framework**: you are testing whether a new pricing model (treatment) produces better
outcomes than the current model (control).

**t-test** (continuous outcome like GPPU):
- H0: mean GPPU(treatment) = mean GPPU(control)
- H1: mean GPPU(treatment) > mean GPPU(control) (one-sided)
- Use Welch's t-test (unequal variances) — store-level variance almost certainly differs.
- Report: test statistic, p-value, confidence interval for the difference, effect size
  (Cohen's d).

**Chi-square test** (categorical outcome like sell-through vs wholesale):
- H0: sell-through rate is independent of treatment assignment.
- Use when comparing proportions across groups.

**Proportion test** (e.g., % of vehicles sold within 30 days):
- Two-proportion z-test.
- For store-level experiments, use the store as the unit and compare average proportions.

### 8.2 Confidence Intervals

**Why CIs matter more than p-values for business decisions**:

A p-value of 0.03 says "this result is unlikely under the null." But the business needs
to know: "How big is the effect, and how certain are we?"

A 95% CI of [$20, $80] for the GPPU improvement means: we're 95% confident the true
improvement is between $20 and $80 per unit. At 500 units/month, that's $10K-$40K/month.
The business can make a decision even without a "significant" result if the CI is
sufficiently narrow and the lower bound is acceptable.

**Bootstrap confidence intervals**:
- When the test statistic doesn't have a clean distributional form (e.g., ratio of
  metrics, trimmed means), use the bootstrap.
- Resample stores with replacement 10,000 times, compute the metric each time, take
  the 2.5th and 97.5th percentiles.

### 8.3 P-Values and Their Limitations

What p-value IS: P(data this extreme | H0 is true).
What p-value IS NOT: P(H0 is true | data).

**Limitations to articulate in an interview**:
- P-value depends on sample size. With enough data, trivially small effects become
  "significant." A $2 GPPU improvement with p=0.001 is not business-relevant.
- P-value does not convey effect magnitude. Always pair with confidence intervals.
- P-value does not account for practical significance. Define a minimum detectable
  effect (MDE) before the experiment.
- Multiple testing: if you test 20 metrics, you expect 1 to be "significant" by chance
  at alpha=0.05.

### 8.4 Multiple Testing Correction

In a pricing experiment, you'll evaluate multiple metrics simultaneously: GPPU,
days-to-sale, sell-through rate, return rate, etc.

**Bonferroni correction**: divide alpha by the number of tests. If testing 10 metrics at
alpha=0.05, use alpha=0.005 per test. Very conservative — high risk of false negatives.

**Holm-Bonferroni**: step-down procedure. Less conservative than Bonferroni, controls
FWER (family-wise error rate).

**Benjamini-Hochberg (FDR control)**: controls the false discovery rate — the expected
proportion of rejected hypotheses that are false positives. Less conservative, appropriate
when you're exploring many hypotheses and some false positives are tolerable.

**Practical recommendation for CarMax**: designate ONE primary metric (e.g., total gross
profit) for the formal hypothesis test. Treat all other metrics as guardrails — monitor
them for red flags but don't adjust the primary metric's p-value.

### 8.5 Bayesian vs Frequentist Approaches

**Frequentist (traditional A/B testing)**:
- Set alpha, power, MDE before experiment.
- Run for fixed duration. Analyze once.
- Binary decision: reject or fail to reject H0.

**Bayesian**:
- Start with a prior distribution on the treatment effect.
- Update with data to get a posterior distribution.
- Compute P(treatment is better) directly — more intuitive for stakeholders.
- Can check results continuously without inflating error rates.
- "There is a 94% probability that the new model improves GPPU by at least $20" is
  more actionable than "p = 0.03."

**When to use Bayesian at CarMax**:
- When sample sizes are small (store-level experiments with N=30 stores per arm).
- When you want to incorporate prior knowledge (we know the model was validated offline).
- When stakeholders want continuous monitoring with probability statements.

### 8.6 Power Analysis

**Why it matters**: before running an experiment, calculate whether you have enough sample
size to detect a meaningful effect. Running an underpowered experiment wastes time and
money.

**Key parameters**:
- Effect size (delta): the minimum improvement worth detecting. For GPPU, maybe $50.
- Variance (sigma): standard deviation of the metric across experimental units (stores).
- Significance level (alpha): typically 0.05.
- Power (1-beta): typically 0.80 (80% chance of detecting a true effect).

**Formula for two-sample t-test**:
```
n_per_arm = 2 * ((z_{alpha/2} + z_beta) * sigma / delta)^2
```

**Example**: if store-level GPPU has sigma=$200 and you want to detect a $50 improvement:
```
n_per_arm = 2 * ((1.96 + 0.84) * 200 / 50)^2 = 2 * (11.2)^2 = 251 stores per arm
```
With ~240 total stores, this is infeasible with a pure store-level split. Solutions:
- Increase experiment duration (more sales per store reduces within-store noise).
- Use CUPED to reduce variance.
- Accept a larger MDE.

### 8.7 Central Limit Theorem

The CLT underpins most of the statistical inference above. For CarMax pricing:
- The mean GPPU across N stores is approximately normal, even if individual-vehicle GPPU
  is skewed (which it is — some vehicles have negative gross profit, others have very
  high GP).
- This justifies using t-tests and normal-based CIs for store-level averages.
- BUT: if N is very small (e.g., 10 stores per arm), the CLT approximation may be poor.
  Use bootstrap or permutation tests instead.

### 8.8 Regression Assumptions and Diagnostics

If using linear regression as a component (e.g., for price elasticity estimation):

| Assumption | How to Check | If Violated |
|-----------|-------------|------------|
| Linearity | Residual vs fitted plot | Add polynomial terms or use non-linear model |
| Homoscedasticity | Residual vs fitted plot, Breusch-Pagan test | Use robust standard errors or WLS |
| Normality of residuals | QQ plot, Shapiro-Wilk | Usually fine with large N (CLT); if small N, use bootstrap |
| No multicollinearity | VIF (Variance Inflation Factor) | Drop or combine correlated features |
| Independence | Durbin-Watson test (for time series) | Use clustered standard errors or time series model |
| No endogeneity | Economic reasoning | Use instrumental variables (Section 4.4) |

For vehicle pricing, the most problematic assumption is endogeneity in price elasticity
estimation: prices are set in response to demand, so regressing quantity on price gives
biased estimates. Always flag this in an interview.

---

## 9. MACHINE LEARNING CONCEPTS

### 9.1 Bias-Variance Tradeoff

**In the vehicle pricing context**:
- **High bias (underfitting)**: a linear model that predicts all Toyota Camrys at the
  same price regardless of mileage, trim, or condition. Misses important patterns.
- **High variance (overfitting)**: a 5000-leaf decision tree that memorizes that one
  specific red 2019 Camry SE with 42,376 miles sold for $23,450. Doesn't generalize.

**Practical balance for pricing**:
- Use gradient boosting with regularization (max_depth, min_child_samples, learning_rate).
- Cross-validate on a time-based holdout — the most honest evaluation.
- If train MAPE is 1.5% but test MAPE is 5%, the model is overfitting.

### 9.2 Overfitting and Regularization

| Technique | How It Works | Use Case |
|-----------|-------------|----------|
| L1 (Lasso) | Penalty on absolute value of weights; drives some to zero | Feature selection — identifies irrelevant features |
| L2 (Ridge) | Penalty on squared weights; shrinks all toward zero | Reduces impact of correlated features |
| Elastic Net | Combines L1 and L2 | When you have many correlated features (make and model are correlated) |
| Early stopping | Stop boosting when validation loss plateaus | Default for GBTs — use callback |
| Max depth | Limit tree depth | Prevents memorization of rare combinations |
| Min samples per leaf | Require minimum N observations per leaf | Prevents splits on tiny subgroups |
| Feature fraction | Random feature subset per tree | Decorrelates trees in ensemble |
| Bagging fraction | Random data subset per tree | Reduces overfitting to any single observation |
| Dropout (neural nets) | Randomly zero out neurons during training | Prevents co-adaptation |

### 9.3 Cross-Validation Strategies

**For vehicle pricing (time-dependent data)**:

Standard k-fold is WRONG because it ignores temporal ordering.

Correct approaches:
- **Time series split**: expanding window as described in Section 1.4.
- **Blocked time series split**: each fold is a contiguous time block. No data from
  future blocks leaks into training.
- **Purged cross-validation**: remove a gap between train and validation folds to prevent
  leakage from lagged features.

**Group cross-validation**: if the same vehicle (e.g., same VIN) appears multiple times
(re-listed after transfer), use GroupKFold with VIN as the group to prevent the model
from memorizing specific vehicles.

### 9.4 Feature Selection Methods

| Method | Description | Pros | Cons |
|--------|------------|------|------|
| Correlation filter | Drop features with abs(corr) > 0.95 with another feature | Fast, simple | Misses non-linear redundancy |
| Mutual information | Information-theoretic measure of feature-target dependence | Captures non-linear relationships | Slow for many features |
| Lasso (L1) | Zero-weight features are irrelevant | Embedded in training | Only for linear models (or linear probing) |
| Recursive feature elimination (RFE) | Iteratively remove least important features | Works with any model | Expensive — retrain N times |
| Permutation importance | Shuffle feature, measure accuracy drop | Model-agnostic, accounts for interactions | Slow; biased for correlated features |
| SHAP importance | Mean absolute SHAP value per feature | Gold standard for tree models | Computationally expensive |
| Boruta | Random forest wrapper that compares real features to shadow (randomized) features | Statistical rigor | Slow |

**Practical recommendation**: start with all engineered features. Train a LightGBM.
Use SHAP importance to rank features. Drop features with near-zero importance and retrain.
Verify that performance doesn't degrade.

### 9.5 Handling Imbalanced Data

Less relevant for the regression pricing model, but critical for adjacent models:
- **Reconditioning cost prediction**: most vehicles have low-to-moderate recon costs, but
  a few have extremely high costs (blown engine, frame damage). The tail matters most.
- **Wholesale decision model**: classification — should this vehicle go to retail or
  wholesale? The wholesale class may be 10-15% of inventory.
- **Fraud detection**: identifying title-washed or odometer-rolled vehicles. Very rare
  positive class.

**Techniques**:
- SMOTE (oversampling the minority class) — use cautiously, can create unrealistic
  synthetic examples.
- Class weights in the loss function — simpler and often just as effective.
- Threshold tuning — optimize the classification threshold for the business objective.
- Focal loss — down-weights easy examples, focuses on hard ones.
- For regression with heavy tails: use Huber loss or quantile regression to give more
  attention to extreme values.

### 9.6 Missing Data Strategies

| Strategy | When to Use |
|----------|-------------|
| Drop rows | Only if very few rows are missing and data is MCAR (Missing Completely At Random) |
| Mean/median imputation | Quick baseline; distorts variance |
| Group-based imputation | Fill with median of same make/model/year — better for vehicle data |
| Indicator variable | Add `feature_missing` binary flag — lets model learn that missingness is informative |
| Model-based imputation | Use other features to predict the missing value (KNN, iterative imputer) |
| Native handling | LightGBM handles NaN natively — often the best approach for tree models |

**CarMax-specific missing patterns**:
- Reconditioning cost: missing at acquisition (inspection hasn't happened yet). This is
  MAR (Missing At Random) — depends on how recently the vehicle was acquired.
- Accident history: missing if CarFax report unavailable. Informative missingness — lack
  of report may correlate with title issues.
- Competitor prices: missing for rare vehicles with no local comparables. Indicates low
  competition (which might INCREASE pricing power).

Always create a binary `is_missing` indicator and let the model decide whether missingness
is informative.

### 9.7 Categorical Encoding

This is critical for vehicle pricing — make/model/year/trim has thousands of unique
combinations.

| Method | Cardinality | Pros | Cons |
|--------|------------|------|------|
| One-hot encoding | Low (<20) | Explicit, no assumptions | Explodes dimensions for high-cardinality |
| Label encoding | Any | Compact | Implies ordinal relationship (misleading for nominal) |
| Target encoding | High | Captures average target per category; compact | Leakage if not regularized; use k-fold |
| Frequency encoding | High | `count(category) / total` — captures popularity | Loses target signal |
| Learned embeddings | Very high | Neural network learns latent representation | Requires NN training; extract for use in GBT |
| Leave-one-out target encoding | High | Like target encoding but excludes current row | Reduces leakage |
| CatBoost encoding | High | Built-in ordered target encoding | CatBoost-specific |

**Recommended approach for CarMax**:
- Use LightGBM's native categorical handling (converts to integer, splits optimally).
- For make/model interaction: concatenate into a single `make_model` feature.
- For trim: target-encode with 5-fold regularization and smoothing (blend category mean
  with global mean, weighted by category count).

### 9.8 Ensemble Methods

| Method | How It Works | When to Use |
|--------|-------------|-------------|
| Bagging (Random Forest) | Train many trees on bootstrap samples; average | Reduce variance of high-variance models |
| Boosting (XGBoost, LightGBM) | Train trees sequentially, each correcting previous errors | Primary method for tabular pricing data |
| Stacking | Train diverse models, then a meta-model on their predictions | Squeeze last 1-2% of accuracy; competition trick |
| Blending | Simple weighted average of diverse model predictions | Production-friendly stacking; easy to maintain |

**Production ensemble at CarMax**:
- Primary: LightGBM trained on full feature set.
- Secondary: XGBoost with slightly different hyperparameters (for diversity).
- Optional: neural network with embeddings for make/model/trim.
- Meta-model: simple linear combination with weights tuned on validation set.
- Keep it simple — maintaining 2-3 models is manageable. 10-model stacks are a
  maintenance nightmare.

### 9.9 Model Interpretability

This is CRITICAL at CarMax. Every price needs to be explainable — to business
stakeholders, to regulators, and potentially to customers who ask "why is this priced
at $X?"

**SHAP (SHapley Additive exPlanations)**:
- Gold standard for tree-based models.
- Provides per-prediction feature attributions that sum to the prediction.
- "This car is priced $2,000 above average because: +$3,000 for low mileage, -$800 for
  black exterior in this market, -$200 for standard transmission."
- Supports global importance (mean |SHAP|), dependence plots, interaction values.

**Partial dependence plots (PDP)**:
- Show the marginal effect of one feature on predictions, averaging over all other features.
- Useful for communicating to non-technical stakeholders: "Here's how mileage affects
  price for a 2022 Toyota Camry."
- ICE (Individual Conditional Expectation) plots show heterogeneity across vehicles.

**Feature importance (gain-based)**:
- Built into GBTs. Fast to compute.
- Caveat: biased toward high-cardinality and continuous features. Use SHAP for
  unbiased importance.

**LIME (Local Interpretable Model-agnostic Explanations)**:
- Fits a local linear model around a single prediction.
- Useful for one-off explanations but less consistent than SHAP.

**Counterfactual explanations**:
- "This vehicle would be priced $1,500 higher if it had 20,000 fewer miles."
- Very intuitive for business users.
- Can be generated by perturbing features and re-scoring.

---

## 10. CASE STUDY: DESIGNING A RECONDITIONING COST MODEL

**Interview prompt**: "Walk me through how you would build a model to predict
reconditioning cost for a vehicle at the time of acquisition."

### 10.1 Problem Statement

When CarMax acquires a vehicle (at auction or through customer trade-in), they need to
estimate the reconditioning cost BEFORE they know the actual cost. This estimate feeds
directly into the acquisition offer: if a car costs $1,500 to recondition, CarMax will
offer $1,500 less for it.

**Why accuracy matters**:
- Overestimate recon cost → offer too little → lose acquisitions to competitors.
- Underestimate recon cost → pay too much → lose money when actual recon cost is higher.
- The margin on used cars is thin (often $1,000-$2,500 GPPU). A $500 recon cost
  prediction error directly erodes 20-50% of the margin.

### 10.2 Data Available at Acquisition Time

**What you HAVE**:
- VIN decode (make, model, year, trim, engine, transmission)
- Mileage (odometer reading)
- Exterior visual condition (photos, inspector notes at auction)
- CarFax/AutoCheck report (accident history, service history, number of owners)
- Title status
- Auction condition report (if bought at auction — includes basic inspection)
- Historical reconditioning costs for similar vehicles (your training data)

**What you DON'T have**:
- Full CarMax inspection results (that happens after acquisition)
- Actual parts and labor breakdown (that's the label, not a feature)
- Hidden issues (electrical problems, internal rust, etc.)

### 10.3 Feature Engineering

```python
recon_features = {
    # Vehicle attributes
    'vehicle_age': 'current_year - model_year',
    'mileage': 'odometer reading',
    'mileage_per_year': 'mileage / vehicle_age',
    'body_style': 'sedan, SUV, truck, etc.',
    'make_model': 'concatenated, target-encoded',
    'drivetrain': 'FWD, RWD, AWD, 4WD',
    'engine_cylinders': '4, 6, 8',
    'transmission_type': 'auto, manual, CVT',

    # Condition signals
    'num_accidents': 'from CarFax',
    'accident_severity_max': 'minor, moderate, severe — from CarFax',
    'num_owners': 'from CarFax',
    'service_history_regularity': 'derived: regular vs irregular maintenance',
    'title_status': 'clean, salvage, rebuilt, lemon',
    'auction_condition_grade': 'if from auction: 1-5 scale',
    'auction_lights': 'green/yellow/red from auction inspection',

    # Historical priors
    'median_recon_cost_make_model_year': 'group-level average from training data',
    'median_recon_cost_vehicle_age_bucket': 'age-based average',
    'high_recon_rate_make_model': '% of this make/model that exceeds $X in recon',

    # Interaction features
    'age_x_mileage': 'vehicle_age * mileage — captures compounding wear',
    'accident_x_age': 'accidents are worse on older vehicles',
    'high_mileage_flag': 'mileage > 15K * vehicle_age — above average use',
}
```

### 10.4 Target Variable

The target is TOTAL reconditioning cost in dollars. This includes:
- Mechanical repairs (engine, transmission, brakes, suspension)
- Cosmetic repairs (paint, body, interior)
- Tires
- Safety items (lights, wipers, recalls)
- Cleaning and detailing

**Target distribution**: highly right-skewed. Most vehicles: $500-$1,500. Some: $3,000+.
Rare: $5,000+ (major mechanical failure discovered after acquisition).

**Transform considerations**:
- Log-transform the target: `log(recon_cost + 1)`. Reduces the influence of extreme
  values and often improves GBT performance on right-skewed targets.
- Alternatively, use Huber loss (robust to outliers) or quantile regression (predict
  the 50th percentile directly).

### 10.5 Model Architecture

**Primary model**: LightGBM regressor with Huber loss.

Why Huber over MAE or MSE:
- MSE over-penalizes the occasional $8,000 recon cost, distorting predictions for
  typical vehicles.
- MAE ignores tail risk. A few badly underestimated $8,000 recon costs will be very
  costly.
- Huber is a compromise: quadratic for small errors (responsive), linear for large
  errors (robust).

**Secondary consideration**: also produce a PREDICTION INTERVAL, not just a point
  estimate. Use quantile regression at the 10th and 90th percentiles. If the 90th
  percentile is very high, flag the vehicle for extra inspection scrutiny.

```python
# Point estimate
model_point = lgb.train(params={'objective': 'huber', 'alpha': 1.0, ...}, ...)

# Upper bound (90th percentile)
model_upper = lgb.train(params={'objective': 'quantile', 'alpha': 0.9, ...}, ...)

# Lower bound (10th percentile)
model_lower = lgb.train(params={'objective': 'quantile', 'alpha': 0.1, ...}, ...)
```

### 10.6 Evaluation

| Metric | What It Tells You |
|--------|------------------|
| MAE | Average dollar error — business stakeholders understand this |
| MAPE | Percentage error — but misleading for low-cost vehicles (MAPE for $200 vehicle is huge) |
| % within $200 | How often are we nearly right? Target: >60% |
| % within $500 | Practical accuracy bucket. Target: >85% |
| Bias | Are we systematically over- or under-estimating? Even $50 of bias * 800K annual units = $40M |
| Tail accuracy (P90) | How well do we predict the high-cost vehicles? These are the ones that kill margin |

**Segment-level evaluation** is critical:
- Newer vehicles (0-3 years): low recon cost, easy to predict. Model should excel here.
- Older vehicles (8+ years): higher and more variable recon costs. Model may struggle.
- Specific makes: some brands have predictable recon (Toyota, Honda); others are volatile
  (Land Rover, BMW with complex electronics).
- Accident vehicles: much higher variance. Consider a separate model or additional
  features.

### 10.7 Deployment

**Where this model runs**:
- At auction: buyer has seconds to decide on a bid. Model runs in real-time on a tablet
  or laptop, feeding into the maximum bid calculator.
- At customer trade-in: appraisal team uses the model to set the offer price.
- In inventory management: recon cost estimate is a key input to the retail pricing model.

**Integration with pricing pipeline**:

```
[Acquisition] --> [Recon Cost Model] --> estimated_recon_cost
                                              |
                                              v
[Vehicle in Inventory] --> [Pricing Model] --> recommended_retail_price
                                |
                                +-- uses estimated_recon_cost as a feature AND
                                    in the profit calculation:
                                    expected_profit = retail_price - acquisition_cost
                                                      - estimated_recon_cost - holding_cost
```

**Feedback loop**:
- After reconditioning is complete, actual recon cost is known.
- Compare actual vs predicted. Log the error.
- If systematic biases emerge (e.g., consistently underestimating for a specific make),
  investigate and retrain.
- Monthly performance review with business stakeholders.

### 10.8 Business Impact Quantification

Suppose the current model (or human estimators) has MAE of $400, and the new model
reduces MAE to $250.

- CarMax acquires ~800,000 vehicles per year.
- Each $1 of average recon prediction error translates to $1 of margin impact.
- But it's not symmetric: underestimates hurt more than overestimates (you overpay for
  the vehicle and eat the loss).
- Assume the improvement reduces average absolute error by $150, of which $100 is on the
  underestimate side (directly recaptured as margin).

Impact: ~$100 * 800,000 = $80M annualized margin improvement.

That's likely an overestimate (not all error flows to margin), but even 10% of that is
$8M/year — easily justifying a data science team working on this problem full-time.

### 10.9 Extensions and Advanced Approaches

**Computer vision**: Use vehicle photos from acquisition to predict reconditioning cost.
A CNN can identify paint damage, body dents, tire wear, and interior condition from images,
extracting features that complement the structured data.

**NLP on inspection notes**: Auction condition reports often include free-text notes.
Train a text classifier to extract severity and type of issues mentioned. Feed the
extracted features into the main model.

**Transfer learning across vehicle segments**: A model trained on sedans can transfer some
knowledge to SUVs (engine wear patterns, tire wear, brake wear are somewhat universal).
Use a shared base model with segment-specific heads.

**Causal inference for recon decisions**: sometimes the decision of WHAT to recondition
is itself a modeling problem. A vehicle with a cosmetic scratch might sell just fine
without fixing it. Model the incremental sale price impact of each reconditioning action
to optimize the reconditioning menu.

---

## APPENDIX: QUICK REFERENCE — KEY NUMBERS TO KNOW

| Metric | Approximate Value | Source |
|--------|------------------|--------|
| CarMax annual unit sales | ~800,000 | Public filings |
| CarMax store count | ~240 | Public filings |
| Average used car transaction price (US) | ~$28,000 | Industry reports |
| CarMax average selling price | ~$28,000-$30,000 | Public filings |
| Average GPPU (retail) | ~$2,200-$2,500 | Public filings |
| Average days to sale | ~35-45 days | Industry estimate |
| Average reconditioning cost | ~$1,000-$1,500 | Industry estimate |
| Used car market size (US) | ~40M units/year | Industry reports |
| Manheim Used Vehicle Value Index baseline | 236.3 (Jan 1995 = 100) | Manheim |
| Average used car depreciation year 1 | ~20% | Industry rule of thumb |
| Average used car depreciation year 5 | ~60% | Industry rule of thumb |

---

## APPENDIX: BEHAVIORAL TIE-INS FOR TECHNICAL QUESTIONS

When answering any technical question in a CarMax interview, always close with the
business impact. Interviewers are evaluating whether you can connect the math to the
business.

**Pattern**: Technical answer → "And the reason this matters for CarMax is..."

Examples:
- "I would use time-based cross-validation... because the used car market is
  non-stationary, and random splits would leak future market conditions into the
  training set, giving us falsely optimistic accuracy numbers."
- "I recommend LightGBM over neural networks here... because with ~1M annual
  transactions and hundreds of features, gradient boosting provides better accuracy on
  tabular data, faster iteration, and — critically — SHAP-based interpretability that
  lets us explain every price to business stakeholders."
- "We need to monitor for data drift... because a supply shock like the 2021 chip
  shortage can shift the entire used car market 20-30% in months. A model trained on
  pre-shock data would systematically underprice inventory, costing millions."

---

## APPENDIX: QUESTIONS TO ASK THE INTERVIEWER

Technical questions that demonstrate depth:

1. "How do you handle the cold-start problem for newly launched models or trims that
   don't have transaction history?"
2. "What's the current retraining cadence for the pricing model, and have you explored
   online learning approaches?"
3. "How do you measure the causal effect of pricing changes versus confounders like
   seasonality and marketing campaigns?"
4. "Is the pricing model a single global model, or do you train separate models per
   vehicle segment or market?"
5. "How do you balance model accuracy with explainability — do pricing analysts have
   override authority?"
6. "What does the feature store architecture look like for real-time scoring?"
7. "How do you handle the tension between maximizing per-unit margin and inventory
   velocity?"
8. "Are there any regulatory constraints on pricing algorithms that affect model design
   (e.g., fair lending interactions with financing)?"
