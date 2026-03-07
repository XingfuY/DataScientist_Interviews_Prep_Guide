# Talk Tracking & Experience Bridge — TikTok Integrity & Safety Data Scientist

**Purpose**: A night-before-interview reference. Every section maps your medical imaging / ML / fraud detection background to TikTok I&S competencies with specific numbers, methods, and story cross-references.

**Interview Format**: 4 rounds
- Round 1 — Peer: SQL / Python / Stats
- Round 2 — HM: Cases / Open-ended
- Round 3 — Skip-Level: Exploration / Business
- Round 4 — HRBP: Behavioral

**Core Principle**: The HM explicitly rejected collaboration framing. Every answer must lead with technical depth, quantitative rigor, and the decision it informed. Never say "I partnered with..." without immediately following it with "to implement X, which measured Y, revealing Z."

---

## 1. Self-Introduction Script

### 1.1 Two-Minute Version (Universal — Adapt Emphasis per Round)

> I am a quantitative researcher with a PhD in medical imaging and machine learning. My work sits at the intersection of statistical methodology, ML system design, and measurement science — which maps directly to what a Data Scientist does in Integrity & Safety.
>
> Let me give you the technical specifics. My PhD focused on 3D medical image reconstruction, where I built a conditional GAN pipeline that improved image quality from 0.82 to 0.91 SSIM — an 11% gain — and increased PSNR by 3.2 dB. To evaluate that pipeline rigorously, I designed a validation framework that compared four reconstruction methods across seven metrics using paired t-tests with Bonferroni correction over 28 comparisons, alpha adjusted to 0.0018. That framework revealed that while the GAN was superior on image quality metrics, it was not statistically significant on diagnostic task accuracy, p = 0.12. This changed the deployment recommendation from "ship the GAN" to "ship the GAN with a diagnostic quality monitoring pipeline." That kind of nuance — where the evaluation methodology changes the business decision — is exactly what I see in the I&S metrics role: the difference between a classifier that looks good on AUC-ROC and one that actually reduces violating view rate in production.
>
> Beyond medical imaging, I have built A/B testing frameworks for LLM prompt evaluation with proper power analysis — n = 1,024 per variant, Holm-Bonferroni correction for 6 comparisons, stratified by content difficulty — and the framework revealed heterogeneous treatment effects that a naive analysis would have missed. I have also built fraud detection systems where I engineered 12 temporal features that improved AUC from 0.89 to 0.94, handled extreme class imbalance at 0.1% positive rate using ensemble undersampling that pushed AUC-PR from 0.38 to 0.72, and reduced anomaly detection latency from 18 hours to 4.2 minutes, preventing $340K in losses.
>
> The statistical foundations of my work — hypothesis testing, power analysis, multiple comparison corrections, causal inference, and evaluating measurement systems under uncertainty — are the same foundations that drive A/B testing, metric design, and safety measurement at TikTok. I am looking for a role where I can apply these methods at billion-user scale to problems where measurement rigor has direct impact on platform safety.

### 1.2 Round-Specific Emphasis Adjustments

**Round 1 (Peer — SQL/Python/Stats)**: After the standard intro, add:
> "On the technical execution side, I have optimized SQL queries from 45 minutes down to 1 minute 48 seconds by analyzing query plans and implementing materialized views — Story 14. My Python stack includes NumPy, SciPy, scikit-learn, PyTorch, and I have extensive experience with pandas feature engineering pipelines, including catching subtle temporal leakage bugs that inflated offline AUC by 4pp — Story 4 behavioral."

**Round 2 (HM — Cases/Open-ended)**: After the standard intro, add:
> "What I bring to open-ended problems is a structured decomposition approach. When asked to evaluate an intervention, I immediately think: what is the causal identification strategy, what are the primary and guardrail metrics, what are the threats to validity, and what sample size do I need to detect a meaningful effect? I have applied this framework to medical imaging method comparison, LLM prompt evaluation, and fraud detection system design."

**Round 3 (Skip-Level — Exploration/Business)**: After the standard intro, add:
> "I have a track record of identifying measurement problems that others have not noticed and building systems to fix them. I caught a data pipeline bug that was artificially deflating violating view rate by 23%, preventing leadership from presenting inflated results to the board — Story 15. I also built an experiment design template that was adopted by three teams, increasing experiment velocity by 25% while preventing $1.2M in safety-related costs — Story 5 behavioral."

**Round 4 (HRBP — Behavioral)**: After the standard intro, add:
> "What drives me is applying rigorous methodology to problems that matter. Medical imaging taught me that measurement quality directly affects patient outcomes. Content safety teaches the same lesson at a different scale — measurement quality directly affects what billions of users are exposed to. I am drawn to TikTok's I&S team because the technical challenges are genuinely hard: rare event detection, network effects in experimentation, causal inference without randomization, and building measurement systems that leadership trusts."

### 1.3 Key Numbers to Memorize

| Metric | Before | After | Story |
|---|---|---|---|
| SSIM (image quality) | 0.82 | 0.91 (+11%) | Story 1 |
| PSNR (image quality) | 28.1 dB | 31.3 dB (+3.2 dB) | Story 1 |
| GPU utilization | 16% | 89% | Story 2 |
| Training time | 72 hours | 18 hours (4x) | Story 2 |
| Bonferroni-corrected alpha | 0.05 | 0.0018 (28 tests) | Story 3 |
| LLM prompt accuracy | 72% | 79% (Variant C) | Story 4 |
| Encoding attack bypass rate | 52% | 3% (after mitigation) | Story 5 |
| Impression Gini coefficient | 0.89 | 0.64 | Story 6 |
| Fraud detection AUC | 0.89 | 0.94 | Story 8 |
| AUC-PR (class imbalance) | 0.38 | 0.72 | Story 9 |
| Anomaly detection latency | 18+ hours | 4.2 minutes | Story 10 |
| Prevented losses | — | $340K (3 incidents) | Story 10 |
| VVR pipeline bug | 23% inflation | 3.4% true change | Story 15 |
| SQL query optimization | 45 minutes | 1 min 48 sec | Story 14 |
| Experiment framework ROI | $1.2M prevented | 25% velocity increase | Story 5 behavioral |

---

## 2. Round-by-Round Talking Points

### 2.1 Round 1: Peer (SQL / Python / Stats)

#### SQL Bridges

**Medical imaging data pipeline --> Content moderation data pipeline**

| Medical Imaging SQL Pattern | Content Safety SQL Pattern | Story Reference |
|---|---|---|
| Query DICOM metadata tables (patient_id, study_date, modality, slice_thickness) | Query content_items table (content_id, creator_id, content_type, created_at, region) | Story 2 |
| Patient cohort analysis: SELECT patient_id, COUNT(*) FROM studies WHERE modality = 'PET' GROUP BY patient_id HAVING COUNT(*) > 3 | Creator cohort analysis: SELECT creator_id, COUNT(*) FROM content_items WHERE is_removed GROUP BY creator_id HAVING COUNT(*) > 5 | Story 14 |
| Join reconstruction results to quality metrics: studies JOIN quality_scores ON study_id | Join content to moderation actions: content_items JOIN moderation_actions ON content_id | Story 14 |
| Rolling average of image quality metrics (7-day SSIM trend across scanner calibration) | Rolling average of violation rates (7-day VVR by region) | Story 14 |
| Window functions for cumulative dose tracking per patient | Window functions for cumulative strike count per user (SUM OVER PARTITION BY user_id ORDER BY violation_date) | Story 14 |

**SQL optimization experience (Story 14 — lead with this)**:
- Diagnosed a 45-minute dashboard query using EXPLAIN ANALYZE
- Root causes: missing composite index on (created_at, region, content_type), CTE materializing 200M rows, window function computing over full partition
- Fixes: composite index reduced scan from 500M to 35M rows, materialized view eliminated redundant scans, date-spine approach pre-aggregated to 30K rows
- Result: 45 minutes --> 1 minute 48 seconds
- Safety analogy: this is the exact pattern for the daily safety dashboard — 7-day rolling VVR by region and category

**Prepared SQL patterns to demonstrate fluency**:
1. Ratio metrics with NULLIF: `ROUND(removed::DECIMAL / NULLIF(total, 0), 4)`
2. Self-join for FPR: removals LEFT JOIN reinstatements on content_id
3. Window functions: `SUM() OVER (PARTITION BY user_id ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`
4. PERCENTILE_CONT for median response time
5. CTE chaining for multi-step metric computation
6. Date-spine approach for gap-free time series

#### Python Bridges

**3D volume processing --> Content feature engineering**

| Medical Imaging Python | Content Safety Python | Story Reference |
|---|---|---|
| NumPy 3D array manipulation (reshape, transpose, slice indexing on [H, W, D] volumes) | NumPy feature matrix manipulation for content features | Story 1, 2 |
| pydicom parsing --> memory-mapped .npy conversion (4.2s --> 0.3s per volume) | Efficient data loading for large-scale content feature tables | Story 2 |
| scipy.stats.ttest_rel for paired image quality comparisons | scipy.stats.ttest_ind for A/B test metric comparisons | Story 3 |
| scipy.stats.bootstrap for metric confidence intervals (B=10,000) | Bootstrap CIs for experiment effect size estimation | Story 3 |
| sklearn.metrics.roc_auc_score, precision_recall_curve for classifier evaluation | Same functions for safety classifier evaluation (AUC-PR preferred over AUC-ROC under class imbalance) | Story 8, 9 |
| Featuretools for automated temporal feature engineering (12 features: velocity, entropy, z-scores) | Same library for content behavioral feature engineering | Story 8 |
| XGBoost with scale_pos_weight for imbalanced classification | XGBoost for rare violation detection with class weight tuning | Story 9 |
| ONNX Runtime for real-time inference (0.3ms/prediction, 5000 pred/sec) | Real-time content scoring at low latency | Story 10 |
| pandas temporal joins with explicit timestamp validation to prevent look-ahead bias | Same discipline for content feature pipelines — always assert feature_timestamp < prediction_timestamp | Story 4 behavioral |

**Key Python talking points**:
- "I caught a look-ahead bias bug in a pandas merge that inflated offline AUC from 0.91 to 0.95. In production, the leaked feature was stale, causing precision to drop 23pp for 5 days. Total cost: $222K. I built temporal validation checks and a monitoring system tracking KL divergence of feature distributions hourly." (Story 4 behavioral)
- "For class imbalance at 0.1% positive rate, I implemented SMOTE inside the CV loop — never on the full dataset — because applying SMOTE before splitting causes synthetic minority samples to leak between folds, inflating recall estimates." (Story 9)

#### Stats Bridges (Each Mapped to a Specific Project)

| Statistical Method | Medical Imaging Application | Content Safety Application | Story |
|---|---|---|---|
| Paired t-test with Bonferroni | Evaluating 4 reconstruction methods on 7 metrics (28 tests, alpha = 0.0018) | Evaluating multiple classifier versions on multiple safety metrics | Story 3 |
| Bootstrap CIs (B=10,000) | 95% CI on SSIM, PSNR, RMSE for each method | 95% CI on VVR, FPR, precision, recall for each experiment arm | Story 3 |
| Cohen's d effect size | Quantifying practical significance: GAN vs. OSEM d = 0.94 on SSIM, d = 0.21 on diagnostic accuracy | Quantifying practical significance of classifier improvements | Story 3 |
| McNemar's test | Paired comparison of classifier errors on same test set | Paired comparison of old vs. new content classifier | Story 4 |
| Holm-Bonferroni step-down | Comparing k=6 LLM prompt variants against baseline (less conservative than Bonferroni, still controls FWER) | Comparing multiple experiment variants or multiple metrics | Story 4 |
| Power analysis (McNemar) | n = 1,024 per prompt variant at 5pp MDE, 80% power | Sample size calculation for A/B tests on classifier accuracy | Story 4 |
| Stratified evaluation | Detecting heterogeneous treatment effects by content difficulty (easy/medium/hard) | Detecting heterogeneous effects by content type, region, language | Story 4 |
| Wilson score interval | 95% CI on recall with n=23 positives: +/- 20pp — too wide for decision-making | CI width assessment for rare violation types with small samples | Story 2 behavioral |
| DeLong test | Comparing AUC of two classifiers on same dataset (p = 0.18 for new vs. old) | Comparing AUC of two content classifiers | Story 1 behavioral |
| Cost-asymmetry analysis | Missed fraud ($180K) vs. false alarm ($42K labor) --> cost-optimal threshold | Missed violation (user harm, regulatory risk) vs. wrongful removal (creator churn) --> optimal threshold | Story 4 behavioral |
| CUPED variance reduction | Not directly used in medical imaging | Mandatory for all experiments: pre-experiment metric as covariate, R^2 = 0.42, 72% effective sample size increase | Story 7 |
| mSPRT sequential testing | Not directly used in medical imaging | Continuous monitoring without inflating Type I error, alpha-spending function across weekly interim analyses | Story 7 |
| DID (difference-in-differences) | Estimating causal effect of content exposure on user retention (2.1% churn difference, p = 0.003) | Evaluating policy impact when randomization is not possible | Story 11 |
| Survival analysis (Cox PH) | Treatment outcome modeling | Creator retention after wrongful removal: each wrongful removal increases 6-month churn hazard by 1.4x | Open-ended Q10 |

**Critical stats talking points for Round 1**:
1. "When I evaluate classifiers, I never use AUC-ROC alone under class imbalance. In fraud detection with 0.1% positive rate, AUC-ROC was 0.95 while AUC-PR was only 0.41 — a massive overstatement of real-world performance. AUC-PR is the appropriate metric when the positive class is rare, which is exactly the case for content violations." (Story 9, Story 1 behavioral)
2. "I compute bootstrap confidence intervals for every metric, not just point estimates. On my medical imaging validation, the GAN's diagnostic accuracy improvement was d = 0.21 — statistically non-significant. Without the CI, the team would have deployed based on the SSIM improvement alone." (Story 3)
3. "For multiple testing, I use Holm-Bonferroni rather than Bonferroni when possible because it is uniformly more powerful while still controlling FWER. In my LLM prompt evaluation with 6 variants, Bonferroni would have required p < 0.0083 while Holm-Bonferroni's step-down procedure rejected at the first step at p = 0.0003, which survived both corrections — but the distinction matters when effects are smaller." (Story 4)

---

### 2.2 Round 2: HM (Cases / Open-ended)

#### Case Analysis Framework

Every case answer follows this structure — no exceptions:

1. **"What decision does this inform?"** — Name the decision explicitly. "This analysis will determine whether we ship, iterate, or kill this policy/classifier/feature."
2. **Define metrics** — Primary metric (the one that determines the decision), guardrail metrics (must not degrade), and diagnostic metrics (explain the why).
3. **Propose method** — Causal identification strategy with specific statistical approach.
4. **Enumerate threats** — At least 3 threats to validity and how to address each.
5. **Recommend** — Concrete recommendation with expected effect sizes and confidence intervals.

**Never say**: "I would collaborate with the ML team to..."
**Always say**: "I would compute / measure / test / decompose / quantify..."

#### Open-Ended Question Strategies

**When asked "evaluate X"**:
- Immediately decompose into: causal identification + metrics + threats
- Example: "Evaluate content throttling effectiveness" -->
  - Causal ID: DID if universal rollout (parallel trends assumption), RDD if threshold-based (McCrary density test for manipulation)
  - Primary metrics: throttled seller VVR reduction, bad seller GMV reduction, new bad account creation rate
  - Guardrails: legitimate seller engagement (spillover), false positive throttling rate
  - Threats: selection bias (PSM/IPW), account migration (device fingerprinting), displacement to other categories, Hawthorne effect
  - Expected: "25% GMV reduction (95% CI: [18%, 32%]) with legitimate seller engagement change < 1pp"

**When asked "design X"**:
- Start with the business objective, work backward to the measurement system
- Example: "Design a platform health metric" -->
  - Business objective: a single leading indicator that predicts 90-day user retention, advertiser spend, and regulatory incident frequency
  - Components: safety score (1 - VVR, weight 0.30), creator health (retention * diversity, weight 0.25), user trust (1 - report rate, weight 0.25), enforcement quality (mean of precision and recall, weight 0.20)
  - Validation: Granger causality test against downstream outcomes, p < 0.05 at 4-8 week lag

**When asked "how would you measure..."**:
- Always quantify: "I would measure X with expected effect size Y, requiring sample size Z, detectable within T weeks."
- Example: "How would you measure if a new hate speech classifier is better?"
  - Offline: McNemar's test on n >= 5,000 labeled test set, stratified by subcategory and language
  - Online: A/B test, 50/50 split, primary metric = VVR, guardrail = FPR from human audit sample
  - Sample size: 5% relative MDE on VVR, 80% power, alpha = 0.05 --> compute n
  - Beyond accuracy: latency (p99), calibration (reliability diagrams), fairness (disaggregated by language/dialect), adversarial robustness (red-team dataset from Story 5)

#### Experience Translations for Open-Ended Questions

**GAN validation framework --> A/B testing with multiple metrics (Story 3)**

The validation framework I built for comparing 4 reconstruction methods across 7 metrics is structurally identical to evaluating a content safety intervention across multiple KPIs. In both cases:
- You have a primary metric (SSIM / VVR) and guardrail metrics (diagnostic accuracy / creator engagement)
- You must correct for multiple comparisons (28 tests with Bonferroni / multiple metrics per experiment)
- Effect size matters more than p-value: the GAN had significant SSIM improvement (d = 0.94) but non-significant diagnostic improvement (d = 0.21) — the decision changed based on which metric you prioritize, just like a classifier that improves recall but degrades precision requires a cost-asymmetry analysis

**Medical image reconstruction pipeline --> Safety metrics system design (Story 1)**

The reconstruction pipeline takes raw sensor data (sinograms) through a series of transformations (OSEM iterations, neural network inference, quality scoring) to produce a diagnostic image with quantified uncertainty. The safety metrics pipeline takes raw event logs through classification, aggregation, and quality checks to produce a VVR dashboard with known measurement error. Both require:
- Explicit data lineage documentation (which pipeline feeds which metric)
- Quality checks at each stage (image quality metrics / data freshness and completeness checks)
- Monitoring for pipeline failures that silently degrade output (Story 15: pipeline bug caused 23% VVR inflation)

**LLM prompt evaluation --> Online experimentation with content classifiers (Story 4)**

The A/B testing framework for LLM prompts is directly transferable to content classifier evaluation:
- Power analysis: McNemar test for paired samples, n = 1,024 per variant at 5pp MDE
- Multiple comparison correction: Holm-Bonferroni for k variants
- Stratified evaluation: by content difficulty (easy/medium/hard) --> by content type, region, language
- Key finding: heterogeneous treatment effects — prompt improved on easy content but not hard. Same pattern in classifiers: a new model may improve on common violation types but regress on rare/nuanced ones

**Fraud detection temporal features --> Content safety feature engineering (Story 8)**

Temporal features capture behavioral signatures that static features miss. In fraud: transaction velocity windows (1h/6h/24h/7d), inter-transaction time entropy, geographic velocity. In content safety: posting velocity windows, content similarity entropy across recent posts, behavioral deviation from historical baseline. The engineering discipline is identical:
- Sliding window aggregations computed incrementally on event streams
- Z-scoring against user's own historical distribution (personalized baselines)
- Permutation importance for feature selection (kept 12 of 20 auto-generated features, removed 8 with importance < 0.01)
- Result: AUC from 0.89 to 0.94, month-over-month decay from 0.02 to 0.005

**Fraud detection --> Content safety classification (Stories 8-10)**

The fraud detection system is a direct structural analog to content safety classification:
- Both operate on behavioral event streams where the positive class is extremely rare (fraud: 0.1%, content violations: often < 1%)
- Both require temporal features because adversaries adapt (fraud patterns evolve, content evasion tactics evolve)
- Both face a cost asymmetry where false negatives are more expensive than false positives (missed fraud = financial loss, missed violation = user harm)
- Both require real-time detection for high-severity events (coordinated fraud attacks, coordinated inauthentic behavior campaigns)

The engineering journey from batch fraud detection (18h latency, Story 10 before) to streaming detection (4.2 min, Story 10 after) is the same journey a safety team makes when moving from daily batch classification to real-time content scoring. The architecture transfers: ONNX Runtime for low-latency inference, Flink for streaming feature computation, two-stage detection (individual scoring + graph community detection).

**Red-teaming for LLM safety --> Adversarial robustness for content classifiers (Story 5)**

The red-teaming protocol tested 650 adversarial inputs across 3 attack categories:
- Direct injection: 34% bypass rate
- Encoding attacks: 52% bypass rate (most vulnerable)
- Semantic evasion: 18% bypass rate
- Quantified risk: encoding attacks alone could allow 12,000 violating items/day to evade detection
- Mitigations: input sanitization (encoding bypass 52% --> 3%), adversarial training (semantic bypass 18% --> 9%)
- Direct applicability: any content classifier needs systematic adversarial evaluation, not just spot-checking

**DID for content exposure --> Causal inference for policy evaluation (Story 11)**

Used DID to estimate the causal effect of violating content exposure on user retention. Found 2.1% higher 30-day churn (p = 0.003) among users exposed to more violating content due to a classifier degradation incident. This estimated the penalty coefficient k = 7 in the Safety-Adjusted Engagement metric: SAE = engagement * (1 - 7 * VVR). Direct application: any time TikTok deploys a new policy without randomization, DID is the go-to causal method, with parallel trends validation on pre-period data.

**Real-time anomaly detection --> Real-time safety incident detection (Story 10)**

Redesigned fraud detection from daily batch to real-time streaming:
- ONNX Runtime for 0.3ms inference (10x vs. native XGBoost)
- Apache Flink for incremental sliding window feature computation
- Two-stage detection: individual scoring (p99 = 50ms) + graph-based community detection (every 5 min)
- EWMA alerting with 3-sigma threshold for hourly fraud score distribution
- Result: 18 hours --> 4.2 minutes latency, $340K prevented
- Safety equivalent: real-time detection of coordinated inauthentic behavior campaigns, spam waves, or new abuse vectors

---

### 2.3 Round 3: Skip-Level (Exploration / Business)

#### Exploration Bridges

**Proactively identifying data loading bottleneck (Story 2) --> Proactively identifying metric measurement gaps**

Nobody asked me to profile the data pipeline. I noticed GPU utilization was 16% and independently traced the bottleneck to pydicom's per-slice parsing. I implemented three optimizations (memory-mapped arrays, multi-worker loading, pipelined augmentation) that improved GPU utilization to 89% and reduced training time 4x.

The same proactive instinct applies to metrics. If a safety metric shows a suspiciously clean trend — no noise, no seasonality — that is a signal to investigate whether the metric is actually measuring what it claims. In Story 15, I caught a 23% VVR inflation caused by a silent pipeline failure. Nobody asked me to audit the metric — the suspiciously large improvement triggered my investigation.

Talking point: "I do not wait for someone to tell me a metric is broken. I look for signals that metrics are too good to be true, and I trace them back to the data source."

**Designing validation framework nobody asked for (Story 3) --> Designing experimentation standards**

The validation framework for comparing reconstruction methods was self-initiated. I saw that different team members were using different metrics, different test sets, and different statistical methods — producing incomparable results. I standardized the evaluation protocol (7 metrics, 300-volume stratified test set, Bonferroni-corrected paired tests, bootstrap CIs, effect sizes). The framework revealed that the "best" method depended on which metric you used — a finding that changed the deployment recommendation.

Same pattern at TikTok: if different teams run experiments with different alpha levels, different multiple testing corrections, and no guardrail metrics, the results are unreliable. Story 5 behavioral: I built an experiment design template adopted by 3 teams, which standardized pre-registration, significance thresholds, sequential testing, CUPED, and mandatory safety guardrails. Result: 47 experiments in the first quarter, 3 blocked by safety guardrails, $1.2M prevented costs, 25% velocity increase.

Talking point: "Standards are a force multiplier. One rigorous framework applied to 47 experiments delivers more value than 47 ad-hoc analyses."

**Building experimentation framework across teams (Story 5 behavioral) --> Cross-team analytical standards**

The experimentation framework addressed a specific failure: two experiments shipped changes with negative safety impact because safety metrics were not included as guardrails. I quantified the cost ($1.2M), built the solution (standardized template with mandatory safety guardrails, mSPRT for sequential testing, CUPED for variance reduction), and drove adoption across safety, growth, and monetization teams.

Talking point: "I led by building infrastructure that made the right thing easier than the wrong thing. Pre-registration is friction-free when the template auto-fills sample size calculations and generates the analysis report."

#### Statistical Methods in Business Context

| Medical Imaging Method | Business Application at TikTok I&S | Specific Numbers |
|---|---|---|
| Image quality metrics (SSIM, PSNR, RMSE) | Content safety metrics (VVR, FPR, appeal overturn rate) | SSIM: 0.82 --> 0.91 maps to VVR reduction targets of 10-20% relative |
| ROC/PR analysis for lesion detection classifiers | Threshold selection for content moderation classifiers | AUC-PR = 0.72 (fraud) maps to classifier evaluation for rare violations |
| Paired t-test with Bonferroni correction (28 tests) | Multi-metric experiment evaluation | alpha_adj = 0.0018, Story 3 |
| Bootstrap CIs (B=10,000) for image quality | Bootstrap CIs for experiment effect sizes | 95% CI on SSIM: [0.89, 0.93], Story 3 |
| Power analysis for clinical trial sample sizes | A/B test sample size calculation | n = 1,024 per variant at 5pp MDE, Story 4 |
| DID for treatment outcome estimation | Policy impact estimation without randomization | 2.1% churn difference, p = 0.003, Story 11 |
| Survival analysis (Kaplan-Meier, Cox PH) for patient outcomes | Creator retention after enforcement actions | Hazard ratio = 1.4 per wrongful removal, Open-ended Q10 |
| Anomaly detection (EWMA, 3-sigma) for scanner calibration drift | Anomaly detection for safety metric shifts (VVR spikes, classifier drift) | 3-sigma EWMA threshold, Story 10 |
| Feature importance (permutation) for diagnostic features | Feature importance for violation risk scoring | 12 of 20 features retained, importance > 0.01, Story 8 |
| Class imbalance handling (ensemble undersampling, SMOTE in CV loop) | Rare violation detection under extreme imbalance | 0.1% positive rate, AUC-PR 0.38 --> 0.72, Story 9 |

#### Business Understanding Preparation

**Key talking points about TikTok / Douyin / LIVE**:

1. **Scale**: TikTok has over 1 billion monthly active users globally. Content volume is billions of items per day across video, live stream, comments, and profiles. The scale makes automated classification essential — human review alone is infeasible.

2. **Three-sided marketplace**: Creators produce content, users consume content, advertisers pay for exposure. Safety affects all three sides:
   - Creator side: over-moderation causes creator churn (wrongful removals --> estimated 4,800 creators/month churn at 6% FPR, $960K/month in lost value, Open-ended Q10)
   - User side: under-moderation causes user harm (exposure to violating content --> 2.1% higher 30-day churn, Story 11)
   - Advertiser side: brand safety incidents reduce advertiser willingness to pay (unsafe adjacency = revenue risk)

3. **Safety as competitive advantage**: Platforms that maintain user trust retain users longer, attract more advertisers, and face fewer regulatory interventions. Safety is not a cost center — it is a moat. The DS who can quantify this tradeoff (SAE = engagement * (1 - k * VVR), Story 11) makes safety investment decisions defensible to leadership.

4. **Regulatory environment**: GDPR, DSA (Digital Services Act), US state-level privacy laws, and country-specific content regulations create compliance requirements. The DS must design metrics that are audit-friendly and can be reported to regulators. Metric definitions must be precise, documented, and reproducible.

5. **TikTok LIVE**: Live streaming presents unique safety challenges — content is ephemeral and must be moderated in real-time. Classifier latency requirements are stricter (p99 < 100ms for real-time scoring). False negatives in live have immediate user exposure. The real-time anomaly detection pipeline from Story 10 (p99 = 50ms) is directly applicable.

6. **E-commerce integration**: TikTok Shop creates additional safety vectors — fake products, misleading claims, bad sellers. Content throttling (reducing distribution without removal) is a key tool. The evaluation framework from Open-ended Q1 applies: DID for universal rollout, RDD for threshold-based enforcement.

7. **Global operations**: TikTok operates across 150+ markets with different languages, cultural norms, and regulatory requirements. Content moderation classifiers must be evaluated per-market, not just globally. A classifier that performs well on English-language content may fail on low-resource languages. This connects to Story 4's stratified evaluation: the LLM prompt that improved on "easy" content but not "hard" content is the same pattern as a classifier that improves on English but not Vietnamese.

8. **Douyin integration**: Douyin (Chinese market) shares infrastructure but different policies. Methods developed for one market should be generalizable. This is an advantage for someone with cross-domain experience — I have already demonstrated that statistical methods transfer across domains (medical imaging --> fraud --> content safety).

**How to reference the three-sided marketplace in answers**:
- "Any safety intervention must be evaluated on three dimensions: user harm reduction (primary), creator impact (guardrail), and advertiser safety (business context)."
- "Over-moderation is not free — each wrongful removal has a quantifiable cost in creator lifetime value. Under-moderation is not free — each missed violation has a quantifiable cost in user churn and regulatory risk. The optimal operating point minimizes total cost, and that calculation depends on violation category." (Open-ended Q5)

---

### 2.4 Round 4: HRBP (Behavioral)

#### ByteDance Values — Mapped to Specific Experiences

**"Always Day 1" (Urgency)**
- Story 10: Redesigned fraud detection from daily batch to real-time (18h --> 4.2min). The urgency was not theoretical — coordinated attacks could cause $340K in losses before the daily batch ran.
- Story 15: Caught VVR inflation before leadership presented inflated results to the board. Verified the root cause, quantified the 23% inflation, and proposed the fix within 24 hours.
- Story 3 behavioral (prioritization): Triaged 3 urgent requests using expected value calculation: metric anomaly (EV/effort = $370K/day), compliance report ($100K/day), A/B test ($11K/day). Completed all 3 in the correct priority order within 3 days.

**"Be Candid and Clear"**
- Story 3: The validation framework revealed that the GAN was NOT significant on diagnostic accuracy (p = 0.12, d = 0.21) despite being significant on SSIM. I presented both results — the good and the bad — which changed the deployment recommendation. I did not cherry-pick the favorable metrics.
- Story 1 behavioral: When a colleague proposed evaluating a classifier using AUC-ROC on a balanced test set, I directly challenged the methodology by preparing a quantitative comparison showing that AUC-ROC overstated performance under production class imbalance. The disagreement was resolved by data, not by authority.
- Story 15: Told leadership that their 12% VVR improvement was actually 3.4% after correcting for the pipeline bug. Delivering bad news backed by evidence.

**"Seek Truth and Be Pragmatic"**
- Story 2 behavioral: With only 23 confirmed SIM swap fraud cases (n=23), I calculated the Wilson score CI on recall was +/- 20pp — too wide for a supervised model. Instead of insisting on more data (not pragmatic) or deploying a bad model (not truthful), I designed a phased approach: rule-based detector --> human review --> labeled data --> ML model. Pragmatic incrementalism grounded in honest assessment of data limitations.
- Story 4 behavioral: Discovered a look-ahead bias bug that inflated offline AUC by 4pp. Instead of just fixing the bug, I quantified the full impact ($222K), built temporal validation checks, and deployed a monitoring system. Seeking truth meant quantifying the damage honestly; being pragmatic meant building systems to prevent recurrence.

**"Be Open and Humble"**
- Story 4 behavioral: The look-ahead bias bug was in code I wrote. I did not deflect blame. I quantified the $222K impact, documented the root cause (pandas merge without temporal ordering), and built safeguards. The failure was a teaching moment that produced better engineering practices.
- Domain transition itself: Moving from medical imaging to content safety requires intellectual humility — acknowledging that domain expertise must be rebuilt while statistical methodology transfers.

**"Dare to Dream" / "Champion Diversity and Inclusion"**
- Story 5 (red-teaming): Proactively tested for adversarial robustness when nobody asked. The 52% encoding bypass rate was a finding that required challenging the assumption that the deployed classifier was "good enough."
- Domain transition: Leaving a successful medical imaging career to pursue content safety DS is itself a bet on a bigger vision — applying the same statistical rigor at a scale that affects billions of users, not hundreds of patients.
- Story 4: The stratified evaluation by content difficulty revealed that classifier improvements were not uniform across difficulty tiers. Disaggregating performance by segment is the same discipline as evaluating classifier fairness across demographic groups and languages — a direct diversity and inclusion concern in content moderation.

**"Aim for the Highest"**
- Story 5 behavioral: Did not just fix the two experiments that had negative safety impact. Instead, built a comprehensive framework (pre-registration, sequential testing, CUPED, automated analysis) that raised the standard for ALL experiments across 3 teams. 47 experiments in the first quarter used the framework.
- Story 1: Did not settle for incremental SSIM improvement. Designed a conditional GAN with a three-component loss function (adversarial + L1 + perceptual) that achieved 11% SSIM improvement and 3.2 dB PSNR gain, validated by two radiologists on a 5-point Likert scale.

#### STAR Answers Pre-Mapped to Behavioral Questions

**Q1: "Tell me about yourself"**
--> Use the self-introduction script from Section 1, Round 4 variant.
- Emphasis: quantitative rigor, measurement science, domain transition motivation.
- Close with: "I am looking for a role where statistical methodology directly impacts what billions of users experience."

**Q2: "Why TikTok?"**
--> Frame around three pillars: technical challenge, impact at scale, and measurement sophistication.

> "Three reasons. First, the technical challenges in I&S are genuinely hard — rare event detection under extreme class imbalance, causal inference without randomization, A/B testing with network effects, and building measurement systems for metrics that have real regulatory and user safety consequences. These are problems where the quality of the analysis directly determines the outcome, which is exactly what motivates me.
>
> Second, scale. In medical imaging, my validation framework covered 300 test volumes. At TikTok, the same statistical methodology applies to billions of content items. The methods transfer; the impact multiplies by six orders of magnitude.
>
> Third, the measurement challenge. Safety metrics are inherently harder to measure than engagement metrics — violating view rate depends on classifier accuracy, which changes over time. A 10% VVR improvement could be real or could be a pipeline artifact. I have caught exactly this kind of measurement failure (Story 15: 23% VVR inflation from a pipeline bug) and I find the meta-problem of 'is the metric itself trustworthy' genuinely intellectually engaging."

**Q3: "Why leave current role?"**
--> Frame around seeking larger scale and A/B testing focus.

> "My current work has given me strong foundations in ML pipeline development, statistical evaluation, and fraud detection. What I am seeking is a role where experimentation and causal inference are central to the daily work, not peripheral. At TikTok I&S, the DS is the quantitative backbone connecting policy, ML, and product — designing experiments, evaluating classifiers, and measuring intervention effectiveness. That combination of statistical rigor and direct product impact is what I want to do full-time.
>
> Additionally, the scale difference is significant. My current systems process thousands of events per day. TikTok processes billions. The same statistical frameworks apply, but at a scale where the engineering of the measurement system itself becomes a first-class problem — data pipeline reliability, metric freshness, and alerting on metric integrity."

**Q4: "Greatest strength"**
--> Quantitative rigor. Cite specific metric improvements, not vague claims.

> "Quantitative rigor — the discipline of backing every claim with a number, a method, and a confidence interval. Concretely: I do not say 'the model improved.' I say 'AUC improved from 0.89 to 0.94, with 12 temporal features, evaluated on 5-fold stratified CV, and the improvement is robust — month-over-month AUC decay reduced from 0.02 to 0.005, meaning the model stays calibrated longer.' (Story 8)
>
> This rigor has saved real money. I caught a look-ahead bias that was costing $222K over 5 days (Story 4 behavioral). I caught a pipeline bug that was artificially deflating VVR by 23%, preventing leadership from presenting false results (Story 15). I designed a validation framework that revealed a classifier was not actually improving diagnostic accuracy despite improving image quality metrics (Story 3). In each case, the rigor changed the decision."

**Q5: "Greatest weakness"**
--> Initially focused too much on technical depth at the expense of business framing.

> "Early in my career, I would present results as technical findings — 'SSIM improved by 11%, p < 0.001' — without explicitly connecting to the business decision. A stakeholder would hear the statistics but not understand what to do. I have deliberately improved this by adopting a framework: every analysis starts with 'the decision this informs is...' and every result ends with 'therefore, I recommend... because...'
>
> A concrete example of the improvement: in Story 11, when the product team and safety team disagreed on a policy launch, I did not just present the DID analysis (2.1% churn uplift, p = 0.003). I translated it into a composite metric (Safety-Adjusted Engagement) with a specific formula (SAE = engagement * (1 - 7 * VVR)) and a specific recommendation (the policy was a net positive: SAE improved by 0.4%). That framing — formula to recommendation — resolved a multi-week cross-team debate in a single meeting."

**Q6: "Conflict with colleague"**
--> Story from Section 7, Q1: competing statistical methodologies.

> "S: A colleague proposed evaluating a new hate speech classifier using AUC-ROC on a balanced test set. I believed this was misleading because production data has a 0.3% positive rate. T: Reach a methodologically sound evaluation consensus without a drawn-out debate. A: I prepared a quantitative comparison rather than arguing in the abstract. I generated predictions from both classifiers on a balanced test set AND a production-representative set. On the balanced set, AUC-ROC was 0.95 vs. 0.92 — a clear win. On the production-representative set, AUC-PR was 0.41 vs. 0.38, not significant (DeLong p = 0.18). More critically, at the production threshold, precision dropped from 82% to 74% while recall improved from 71% to 76%. I presented both analyses side by side, letting the data make the argument. R: We adopted a standard protocol — AUC-PR on production-representative data as the primary metric, plus precision and recall at the production threshold. The new classifier was not deployed until precision degradation was fixed. The protocol was documented and used for all subsequent evaluations."

**Q7: "Decision with incomplete info"**
--> Story from Section 7, Q2: SIM swap fraud with n=23.

> "S: A new fraud type — SIM swap account takeover — emerged, but we had only 23 confirmed cases. Leadership wanted a detector in 2 weeks. T: Build detection with insufficient labeled data for supervised learning. A: First, I quantified the insufficiency: Wilson score CI on recall with n=23 is +/- 20pp — unacceptable. Instead of forcing a supervised model, I characterized the 23 cases' behavioral signature (password reset --> device change --> rapid transfers, all within 30 minutes), built a rule-based detector for that pattern, analytically estimated the false positive rate at ~100/day (manageable for human review), and deployed with a 2-week evaluation period to generate labels. R: The rules caught 8 of the next 11 cases (72% recall). The 108 human-reviewed cases (100 FP + 8 TP) were enough to train a proper ML model by week 4, achieving 89% recall at 0.5% FPR. The phased approach turned data scarcity into a label generation system."

**Q8: "Tell me about a failure"**
--> Story from Section 7, Q4: look-ahead bias bug.

> "S: I deployed a fraud detection model update with a feature engineering bug — a look-ahead bias from a pandas merge that did not enforce temporal ordering. One feature used future transaction data not available at prediction time. The feature had importance 0.14, inflating offline AUC from the true 0.91 to 0.95. T: In production, the feature defaulted to a stale value, causing precision to drop from 85% to 62% — a 23pp degradation that went undetected for 5 days. A: I quantified the damage: 3,400 additional false positive alerts * 15 min each = 850 analyst-hours ($42K labor cost), plus 12 missed fraud cases worth $180K. Total impact: $222K. I fixed the merge, added explicit temporal validation checks (assert feature_timestamp < prediction_timestamp), and built a production monitoring system tracking 4 metrics hourly: feature distribution KL divergence, prediction score distribution shift, precision/recall from human review sample, and feature staleness. R: Backtested the monitoring system — it would have caught the bug in 6 hours instead of 5 days, reducing impact from $222K to ~$18K. The temporal validation check has since caught 2 additional look-ahead bugs before they reached production. The failure was mine, and the monitoring system I built in response has prevented far more damage than the original incident caused."

**Q9: "Time you showed leadership"**
--> Story from Section 7, Q5: experiment framework adopted by 3 teams.

> "S: Three teams — safety, growth, and monetization — were running A/B tests with inconsistent methodology. Different significance levels, different multiple testing corrections, no pre-registration, no mandatory safety guardrails. Two experiments shipped changes with undetected negative safety impact. T: Standardize experimentation methodology across all teams. A: I quantified the cost of the status quo ($1.2M from the two incidents), then built a framework: mandatory pre-registration, alpha = 0.05 with safety guardrails for ALL experiments, mSPRT for sequential testing (eliminates p-hacking from peeking), CUPED for variance reduction (30-40% duration reduction), and an automated analysis pipeline that generates standardized reports. I validated the framework by re-analyzing the two problematic experiments — both would have been caught. I presented the retrospective and the solution to all three teams. R: Adopted by all teams within 6 weeks. 47 experiments used the framework in the first quarter. Three experiments were blocked by safety guardrails that would have been missed under the old process. Experiment velocity increased 25% from CUPED and automation. Analyst time per experiment dropped from 2 days to 3 hours."

**Q10: "Where do you see yourself in 5 years?"**
--> Leading a DS function that sets analytical standards for safety measurement.

> "In 5 years, I want to be leading a data science function — not necessarily managing people, but owning the analytical standards for how safety is measured and how interventions are evaluated. Specifically:
>
> At the individual contributor level, I want to have established the causal inference methodology for policy evaluation — the frameworks, the pre-registered analysis plans, the metrics definitions that become the team's operating standard. The experiment framework from Story 5 behavioral is a prototype of this: one person's framework became the standard for 47 experiments across 3 teams.
>
> At the organizational level, I want to be the person leadership consults when they need to know 'is this metric trustworthy?' and 'what is the causal effect of this intervention?' The ability to answer those questions rigorously — with confidence intervals, threats to validity enumerated, and clear recommendations — is what I see as the highest-leverage contribution a DS can make.
>
> I am particularly interested in the methodological frontier: how to do causal inference at TikTok's scale with network effects, how to build composite metrics that capture the safety-engagement tradeoff, and how to design experimentation infrastructure that makes rigorous testing the path of least resistance."

---

## 3. Key Experience Translations

### 3.1 Comprehensive Mapping Table

| # | Medical Imaging / ML Experience | TikTok I&S Equivalent | Key Story | Specific Numbers |
|---|---|---|---|---|
| 1 | Conditional GAN for 3D PET image reconstruction | ML model improvement for content classification quality | Story 1 | SSIM 0.82 --> 0.91, PSNR +3.2 dB, RMSE -34% |
| 2 | Data loading bottleneck profiling and optimization | Data pipeline performance optimization for metric freshness | Story 2 | GPU util 16% --> 89%, training 72h --> 18h, 4x throughput |
| 3 | Multi-method validation framework (OSEM vs. GAN vs. diffusion vs. CNN) | A/B testing with multiple metrics and multiple comparisons | Story 3 | 7 metrics, 28 tests, Bonferroni alpha = 0.0018, B = 10,000 bootstrap |
| 4 | A/B testing framework for LLM prompt variants | Online experimentation for content classifier variants | Story 4 | n = 1,024/variant, Holm-Bonferroni, stratified by difficulty, 72% --> 79% |
| 5 | Systematic red-teaming for LLM prompt injection | Adversarial robustness evaluation for content classifiers | Story 5 | 650 adversarial examples, 52% encoding bypass --> 3% after mitigation |
| 6 | Popularity bias diagnosis and debiasing in recommendations | Content distribution fairness and creator ecosystem health | Story 6 | Gini 0.89 --> 0.64, tail impression share 3% --> 18%, CTR -2.3% |
| 7 | Sequential A/B test design with mSPRT and CUPED | Rigorous online experimentation infrastructure | Story 7 | mSPRT z = 2.87, CUPED R^2 = 0.42, 72% effective sample size increase |
| 8 | Temporal feature engineering for fraud detection | Content safety feature engineering for violation risk scoring | Story 8 | 12 features, AUC 0.89 --> 0.94, monthly decay 0.02 --> 0.005 |
| 9 | Extreme class imbalance handling (0.1% positive rate) | Rare violation detection (low base rate enforcement) | Story 9 | AUC-PR 0.38 --> 0.72, ensemble undersampling, SMOTE in CV loop |
| 10 | Real-time anomaly detection pipeline (batch --> streaming) | Real-time safety incident detection | Story 10 | 18h --> 4.2min latency, $340K prevented, ONNX 0.3ms inference |
| 11 | Conflicting metrics resolution with composite metric (SAE) | Safety-engagement tradeoff quantification | Story 11 | DID: 2.1% churn uplift (p = 0.003), k = 7, SAE +0.4% |
| 12 | Ambiguous requirements --> phased rollout with success criteria | Policy rollout with explicit metrics and decision gates | Story 12 | Spam VVR -23% (target: -20%), hate speech VVR -18%, total VVR -14.2% |
| 13 | Impact-effort prioritization of competing analysis requests | DS request prioritization and stakeholder management | Story 13 | 7 requests from 4 teams, EV/effort scoring, top 3 in 6 days |
| 14 | Slow SQL optimization (EXPLAIN ANALYZE, materialized views) | Dashboard query optimization for safety metrics | Story 14 | 45min --> 1min 48s, composite index, date-spine aggregation |
| 15 | Data pipeline bug causing metric inflation | Metric integrity monitoring for safety dashboards | Story 15 | 23% VVR inflation, silent row drops, 12% apparent improvement was 3.4% |

### 3.2 Method-Level Translation Table

| Statistical / ML Method | Medical Imaging Context | Content Safety Context | Why It Transfers |
|---|---|---|---|
| Paired t-test | Compare image quality (SSIM) between two reconstruction methods on the same test volumes | Compare VVR between treatment and control on the same time period | Same test, same assumptions (normality of paired differences), same interpretation |
| Bonferroni correction | 7 metrics * 4 comparisons = 28 tests, alpha_adj = 0.0018 | Multiple metrics per experiment (VVR, FPR, appeal rate, creator churn), alpha_adj = 0.05/k | FWER control is FWER control regardless of domain |
| Bootstrap CI (B=10,000) | CI on SSIM, PSNR for each reconstruction method | CI on experiment effect size, metric estimates | Non-parametric CI estimation when distributional assumptions are uncertain |
| McNemar's test | Compare error rates of two classifiers on the same labeled test set | Compare old vs. new content classifier on the same labeled test set | Paired binary outcome comparison — more powerful than unpaired chi-squared |
| Power analysis | n = 1,024 per LLM prompt variant at 5pp MDE | n per experiment arm for VVR MDE, rare event power calculations | Same formula: n = f(alpha, beta, MDE, baseline_rate) |
| DID | Effect of violating content exposure on user retention (2.1% churn, p = 0.003) | Effect of policy change on VVR when randomization is not possible | Same identifying assumption (parallel trends), same regression specification |
| CUPED | Not used in medical imaging (no sequential experiments) | Pre-experiment metric as covariate, R^2 = 0.42, variance reduction | Novel application: learn from my A/B testing framework work (Story 7) |
| mSPRT | Not used in medical imaging | Sequential testing for continuous monitoring, alpha-spending across interim analyses | Novel application: learn from Story 7 |
| XGBoost with class weights | Fraud detection at 0.1% positive rate, scale_pos_weight = 999 | Rare violation detection, cost-sensitive classification | Same library, same hyperparameter, same evaluation framework |
| ONNX Runtime deployment | Real-time fraud scoring, 0.3ms/prediction | Real-time content scoring, latency requirement < 100ms | Same inference optimization approach |
| EWMA anomaly detection | Monitoring fraud score distribution, 3-sigma alert threshold | Monitoring safety metric distributions, incident detection | Same statistical process control framework |
| Survival analysis (Cox PH) | Patient treatment outcomes | Creator retention after enforcement actions (HR = 1.4 per wrongful removal) | Same model, different unit of analysis (patient --> creator) |
| ROC/PR analysis | Lesion detection classifier evaluation | Content moderation classifier threshold selection | Same curves, but AUC-PR is preferred under class imbalance |
| Feature permutation importance | Selecting 12 of 20 temporal features for fraud model | Selecting informative features for safety risk scoring | Same method: shuffle feature, measure accuracy drop |
| Cost-asymmetry analysis | Missed fraud ($180K) vs. false alarm ($42K) --> threshold | Missed violation (user harm) vs. wrongful removal (creator churn) --> threshold | Same framework: C_FN vs. C_FP, argmin total cost |

### 3.3 Quick-Reference Bridge Statements

For rapid recall during the interview, memorize these one-sentence bridges:

1. "SSIM is to image quality as VVR is to platform safety — both are ratio metrics that require decomposition to diagnose root causes."
2. "Comparing 4 reconstruction methods across 7 metrics with Bonferroni correction is structurally identical to evaluating a safety experiment across multiple KPIs."
3. "Fraud at 0.1% positive rate is the same class imbalance problem as detecting CSAM or coordinated inauthentic behavior — AUC-PR, not AUC-ROC."
4. "The conditional GAN training pipeline (data loading, augmentation, training, evaluation) maps to the content classifier lifecycle (data labeling, feature engineering, training, A/B testing, monitoring)."
5. "My DID analysis showing 2.1% user churn from violating content exposure is exactly the kind of causal inference I would use to evaluate a new content policy without randomization."
6. "Real-time fraud detection at 4.2 minutes is the same engineering challenge as real-time safety incident detection — streaming features, low-latency inference, EWMA alerting."
7. "The data pipeline bug I caught (23% VVR inflation) is why I always decompose metrics into components and verify each data source independently."

---

## 4. Product Impact Framing for Every Story

Every technical achievement must connect to a business outcome. For each STAR story, here is the one-line product impact framing followed by the TikTok I&S analogy.

### Story 1: GAN Reconstruction (SSIM 0.82 --> 0.91)
**Product impact**: Improved diagnostic image quality by 11% SSIM, increasing radiologist confidence from 3.2 to 4.4 on a 5-point scale — enabling more accurate diagnoses.
**TikTok analogy**: Analogous to improving a content classifier's precision by 11pp, which reduces wrongful content removals and directly improves creator trust in the platform. Each percentage point of precision improvement at TikTok's scale translates to thousands fewer wrongful removals per day.

### Story 2: Data Loading Bottleneck (GPU util 16% --> 89%)
**Product impact**: Reduced model training time from 72 hours to 18 hours (4x), accelerating the research iteration cycle and enabling more experiments per quarter.
**TikTok analogy**: Analogous to reducing classifier retraining time, which shortens the feedback loop between identifying a new abuse pattern and deploying an updated model. In content safety, a 4x reduction in model iteration speed means 4x faster response to emerging threats.

### Story 3: Validation Framework (7 metrics, 28 tests, Bonferroni)
**Product impact**: Revealed that the "best" reconstruction method was NOT best on the clinically relevant metric (diagnostic accuracy p = 0.12), changing the deployment recommendation and preventing a suboptimal clinical tool from reaching patients.
**TikTok analogy**: Directly applicable to evaluating safety classifier updates. A classifier that improves AUC-ROC but degrades precision at the production threshold is a net negative for user safety. The validation framework prevents shipping classifiers based on misleading metrics.

### Story 4: LLM A/B Testing Framework (n=1,024, Holm-Bonferroni)
**Product impact**: Identified heterogeneous treatment effects — prompt improved on easy content (68% --> 82%) but not hard content (41% --> 43%). Led to a hybrid approach achieving 81% overall accuracy vs. 79% from the naive deployment.
**TikTok analogy**: Directly maps to evaluating content classifier performance across content difficulty levels, languages, and regions. A classifier that improves on common English-language violations but regresses on rare non-English violations creates measurement blind spots that put specific user populations at disproportionate risk.

### Story 5: Red-Teaming (650 adversarial examples, 52% bypass)
**Product impact**: Quantified that encoding attacks alone could allow 12,000 violating items per day to evade detection. Mitigations reduced encoding bypass from 52% to 3% — preventing an estimated 11,760 daily violating item exposures.
**TikTok analogy**: Every content classifier deployed at TikTok faces adversarial users. Systematic red-teaming with quantified bypass rates is essential for understanding true classifier performance in adversarial environments, not just on curated test sets.

### Story 6: Popularity Bias Debiasing (Gini 0.89 --> 0.64)
**Product impact**: Increased tail content impression share from 3% to 18% with only 2.3% CTR decline — expanding the creator ecosystem and reducing concentration risk.
**TikTok analogy**: Content safety affects content distribution. If enforcement disproportionately targets certain content types or creator demographics, it introduces bias in the content ecosystem. The debiasing methodology (IPS weighting, causal embedding, exploration) applies to ensuring fair enforcement across creator segments.

### Story 7: Sequential A/B Test Design (mSPRT, CUPED)
**Product impact**: Saved one week of experiment duration via sequential testing (mSPRT rejected at week 3 instead of waiting for week 4) and reduced required sample size by 72% via CUPED — accelerating the ship decision for a recommendation algorithm change that improved engagement-adjusted diversity by 8.2%.
**TikTok analogy**: Safety experiments on TikTok require the same infrastructure: sequential testing to avoid false positives from peeking, CUPED for variance reduction (safety metrics are often high-variance), and cluster randomization for network effects. This is the experimentation playbook I would bring on day one.

### Story 8: Temporal Feature Engineering (AUC 0.89 --> 0.94)
**Product impact**: Improved fraud detection accuracy while reducing model drift — AUC decay from 0.02 to 0.005 per month. False positive rate at 80% recall decreased from 2.1% to 0.9%, saving 1,200 manual review hours per month.
**TikTok analogy**: Content safety classifiers face the same model drift problem — adversarial users adapt, new abuse patterns emerge, and static features become stale. Temporal features that capture behavioral velocity, entropy, and deviation from baseline keep the model adaptive. The 1,200 hours/month saved in manual review maps directly to content moderation queue efficiency.

### Story 9: Class Imbalance (0.1% positive, AUC-PR 0.38 --> 0.72)
**Product impact**: Achieved 84% recall at 31% precision for rare fraud events — catching 84 of 100 fraud cases with 187 false alarms, a manageable manual review load vs. the baseline of catching 0 with 0 false alarms.
**TikTok analogy**: Content violations at TikTok are similarly rare events (VVR is often < 1%). The same techniques — ensemble undersampling, SMOTE within CV folds (never before the split), AUC-PR as the evaluation metric, cost-weighted F-beta — apply directly to rare violation detection like CSAM or coordinated inauthentic behavior.

### Story 10: Real-Time Anomaly Detection (18h --> 4.2min)
**Product impact**: Caught 3 coordinated fraud attacks that the daily batch would have missed, preventing $340K in losses. Reduced infrastructure cost by 60% via ONNX deployment while increasing throughput 10x.
**TikTok analogy**: Real-time safety incident detection is critical for live events, viral content, and coordinated attacks. The EWMA-based alerting with 3-sigma thresholds and the two-stage detection architecture (individual scoring + graph-based community detection) map directly to TikTok's need for real-time CIB detection and spam wave response.

### Story 11: Conflicting Metrics / SAE (DID, k=7, SAE +0.4%)
**Product impact**: Created the Safety-Adjusted Engagement composite metric that resolved a multi-week cross-team debate in a single meeting. SAE was adopted as the joint north-star metric for all policy launches, reducing decision latency from 2+ weeks to one meeting.
**TikTok analogy**: This is the most directly applicable story. The tension between engagement and safety is TikTok's central tradeoff. The SAE framework (engagement * (1 - k * VVR)) with empirically estimated k provides a principled, quantitative way to make ship/no-ship decisions that balance both objectives. The DID-estimated k = 7 can be re-estimated at TikTok using their data.

### Story 12: Ambiguous Requirements --> Phased Rollout
**Product impact**: Transformed "reduce bad content" into measurable phases with explicit targets. Phase 1 exceeded the 20% spam VVR reduction target (achieved 23%) within 4 weeks. Total 12-week VVR reduction: 14.2%.
**TikTok analogy**: Leadership directives at TikTok are often similarly broad ("improve platform safety"). The DS must translate them into specific, measurable, time-bounded plans with decision gates. The phased rollout approach with pre-registered success criteria demonstrates the ability to make ambiguity actionable.

### Story 13: Prioritization with Impact-Effort Framework
**Product impact**: Completed the 3 highest-value analysis requests in 6 analyst-days out of 7 requests. All time-sensitive decisions were informed on schedule. The metric anomaly investigation (0.5 days) prevented $50K in wrong decisions.
**TikTok analogy**: A DS in I&S will face competing demands from T&S policy, ML engineering, product, legal, and leadership. The expected value per analyst-day framework provides a principled, quantitative way to prioritize that stakeholders can verify and accept.

### Story 14: SQL Optimization (45min --> 1min 48s)
**Product impact**: Dashboard was fresh by 8:45 AM instead of 9:30 AM, enabling the team to make data-driven decisions at the morning standup. Reduced production database load by eliminating redundant full table scans.
**TikTok analogy**: Safety dashboards that are stale during the morning review are worse than useless — they create false confidence. The optimization techniques (composite indexes, materialized views, date-spine aggregation) are standard tools for any DS who owns dashboard freshness.

### Story 15: Pipeline Bug / Metric Inflation (23% VVR error)
**Product impact**: Prevented leadership from presenting inflated safety results to the board. True VVR improvement was 3.4%, not 12%. Implemented metric integrity monitoring that detects component-level deviations > 2 standard deviations.
**TikTok analogy**: This is the highest-stakes story for the I&S role. If a VVR metric is wrong and leadership makes decisions based on it — staffing, budget allocation, regulatory reporting — the consequences compound. The ability to independently verify metrics and build monitoring systems that catch silent failures is a core DS competency.

### Product Impact Summary Table

| Story | Core Technical Achievement | Business Value | Dollar / % Impact |
|---|---|---|---|
| 1 | GAN reconstruction quality | Diagnostic accuracy improvement | +11% SSIM, +1.2 Likert points |
| 2 | Data pipeline optimization | Faster model iteration | 4x training speedup |
| 3 | Validation framework | Prevented suboptimal deployment | Changed ship/no-ship decision |
| 4 | LLM A/B testing | Heterogeneous effect detection | +9pp overall accuracy |
| 5 | Red-teaming | Adversarial vulnerability quantification | 12,000 daily evasions prevented |
| 6 | Debiasing | Creator ecosystem health | +15pp tail impression share |
| 7 | Sequential testing + CUPED | Faster, more reliable experiments | 1 week saved, 72% sample size reduction |
| 8 | Temporal features | Adaptive fraud detection | AUC +0.05, 1,200 review hours/month saved |
| 9 | Class imbalance handling | Rare event detection capability | AUC-PR +0.34, 84% recall from 0% |
| 10 | Real-time detection | Attack response speed | 18h --> 4.2min, $340K prevented |
| 11 | Composite metric (SAE) | Cross-team decision framework | Decision time: 2+ weeks --> 1 meeting |
| 12 | Phased rollout | Structured ambiguity resolution | VVR -14.2% in 12 weeks |
| 13 | EV/effort prioritization | Analyst time optimization | 3 of 7 requests in 6 days, all on-time |
| 14 | SQL optimization | Dashboard freshness | 45min --> 1min 48s |
| 15 | Metric integrity monitoring | Prevented false reporting | 23% inflation caught, 3.4% true change |

---

## Appendix A: Emergency Quick Reference

### If You Blank on a Question

1. Pause. Say: "Let me structure my thinking on this."
2. Write down the framework: "I would approach this as: (1) define the decision, (2) define the metrics, (3) propose a method, (4) enumerate threats."
3. Map to the nearest STAR story. Every question can be answered by analogy to one of the 15 stories.

### Story Lookup by Topic

| Topic | Primary Story | Backup Story |
|---|---|---|
| A/B testing | Story 7 (mSPRT, CUPED) | Story 4 (LLM prompts) |
| Causal inference | Story 11 (DID, SAE) | Open-ended Q1 (throttling) |
| Classifier evaluation | Story 3 (validation framework) | Story 1 behavioral (AUC-ROC vs AUC-PR) |
| Class imbalance | Story 9 (0.1% positive rate) | Story 8 (fraud features) |
| Data pipeline issues | Story 15 (VVR inflation) | Story 2 (data loading bottleneck) |
| Feature engineering | Story 8 (12 temporal features) | Story 6 (debiasing features) |
| Metric design | Story 11 (SAE composite) | Open-ended Q4 (platform health) |
| Real-time systems | Story 10 (streaming detection) | Story 2 (pipelined data loading) |
| Adversarial robustness | Story 5 (red-teaming) | Open-ended Q2 (classifier evaluation) |
| SQL | Story 14 (query optimization) | Section 2 (15 SQL problems) |
| Prioritization | Story 13 (EV/effort) | Story 3 behavioral (3 urgent requests) |
| Failure | Story 4 behavioral (look-ahead bias) | Story 15 (pipeline bug) |
| Leadership | Story 5 behavioral (experiment framework) | Story 3 (validation framework) |
| Ambiguity | Story 12 (phased rollout) | Story 2 behavioral (n=23) |
| Conflict | Story 1 behavioral (AUC-ROC debate) | Story 11 (safety vs. engagement) |

### Numbers to Drop in Any Answer

- "0.82 to 0.91 SSIM" — image quality improvement
- "0.89 to 0.94 AUC" — fraud detection improvement
- "0.38 to 0.72 AUC-PR" — class imbalance solution
- "18 hours to 4.2 minutes" — detection latency improvement
- "$340K prevented" — real-time detection value
- "$222K cost" — look-ahead bias failure
- "$1.2M prevented" — experiment framework value
- "23% VVR inflation" — pipeline bug impact
- "45 minutes to 1 minute 48 seconds" — SQL optimization
- "28 tests, alpha = 0.0018" — multiple comparison rigor
- "n = 1,024" — proper sample size calculation
- "2.1% churn, p = 0.003" — causal inference result

### Forbidden Phrases

| Never Say | Instead Say |
|---|---|
| "I collaborated with the team to..." | "I computed / designed / implemented / measured..." |
| "We worked together on..." | "I built X, which measured Y, revealing Z" |
| "I helped facilitate..." | "I owned the analysis: defined metrics, ran the test, quantified the result" |
| "I think X might work..." | "Based on power analysis with n = X, MDE = Y, we need Z samples to detect..." |
| "The model was good" | "AUC-PR improved from 0.38 to 0.72 under 0.1% class imbalance" |
| "We improved things" | "VVR decreased 14.2% across 6 violation categories over 12 weeks" |

### Closing Statement (Any Round)

> "I want to emphasize one thing: every number I have cited today comes from work I directly executed — the code I wrote, the analyses I ran, the frameworks I designed. I am looking for a role where that level of quantitative ownership is expected, and from everything I know about TikTok's I&S data science team, that is exactly what this role demands."

---

## Appendix B: Anticipated Follow-Up Questions and Rehearsed Responses

### Follow-Ups After Self-Introduction

**"You come from medical imaging. How does that prepare you for content safety?"**

> "The statistical methods are identical — the domain objects change but the math does not. In medical imaging, I evaluate whether a reconstruction method produces diagnostically useful images using paired tests, bootstrap CIs, and effect sizes. In content safety, I would evaluate whether a classifier produces safe content feeds using the same statistical tools on different metrics. Specifically:
>
> - Image quality metric (SSIM) maps to safety metric (VVR) — both are ratio metrics that require decomposition.
> - Comparing reconstruction methods (OSEM vs. GAN vs. diffusion) maps to comparing classifier versions — I used 28 paired tests with Bonferroni correction, the same discipline applies to multi-metric experiment evaluation.
> - Rare lesion detection at low prevalence maps to rare violation detection under extreme class imbalance — I handled 0.1% positive rate in fraud and know that AUC-ROC is misleading, AUC-PR is required.
> - My DID analysis for causal inference (2.1% churn from violating exposure, p = 0.003) is directly applicable to evaluating policy changes without randomization.
>
> The domain transition is an advantage: I bring rigorous statistical methodology without legacy assumptions about how content safety 'should' be measured."

**"What is your experience with A/B testing at scale?"**

> "I have designed and implemented two A/B testing frameworks. The first was for LLM prompt evaluation (Story 4): proper power analysis yielding n = 1,024 per variant, Holm-Bonferroni correction for 6 comparisons, stratified by content difficulty — which revealed heterogeneous treatment effects the naive analysis missed. The second was an online A/B test for a recommendation algorithm (Story 7): mSPRT for sequential testing to prevent false positives from peeking, CUPED with R^2 = 0.42 for 72% effective sample size increase, and cluster randomization to handle network effects. The mSPRT rejected at week 3 (z = 2.87), saving one week vs. fixed-horizon design.
>
> Beyond individual experiments, I built the experiment framework adopted by 3 teams (Story 5 behavioral): mandatory pre-registration, standard alpha, safety guardrails for all experiments, automated analysis pipeline. 47 experiments used it in the first quarter.
>
> What I have not done yet is A/B testing at TikTok's scale — billions of daily content items. But the methodology is the same, and the unique challenges (network effects, rare events, real-time metrics) are ones I have studied and have concrete approaches for."

### Follow-Ups After STAR Stories

**After Story 3 (Validation Framework): "How did you choose 7 metrics? Why not 3 or 15?"**

> "The 7 metrics were chosen to cover three dimensions of quality, each with different stakeholders. Image fidelity metrics (SSIM, PSNR, RMSE) — 3 metrics that the ML team cares about. Perceptual quality metrics (LPIPS, FID) — 2 metrics that capture visual quality beyond pixel-level accuracy. Clinical utility metrics (lesion detection accuracy, radiologist preference) — 2 metrics that the clinical team cares about. The key insight was that metric agreement is not guaranteed: the GAN won on fidelity (SSIM d = 0.94) but tied on clinical utility (diagnostic accuracy p = 0.12). If I had used only fidelity metrics, the wrong decision would have been made. If I had used 15 metrics, the multiple testing correction would have reduced power to detect real differences. 7 metrics with 28 pairwise tests at alpha = 0.0018 provided sufficient power (> 0.80 for d > 0.5) while controlling FWER."

**After Story 11 (SAE): "How did you estimate k = 7? What if k is wrong?"**

> "k was estimated from a natural experiment — a classifier degradation incident that exogenously increased violating content exposure for some users. Using DID, I found 2.1% higher 30-day churn (p = 0.003) in the exposed group, with a VVR increase of approximately 0.3pp. k = delta_churn / delta_VVR * mean_time_spent. The 95% CI on the DID estimate gives a range for k of approximately 4 to 11. I computed SAE under k = 4 (lower bound), k = 7 (point estimate), and k = 11 (upper bound). The policy was a net positive under all three values, so the decision was robust. If the decision had been sensitive to k — positive under k = 4 but negative under k = 11 — I would have recommended collecting more data to narrow the CI before making the ship decision."

**After Story 15 (Pipeline Bug): "How do you prevent this from happening again?"**

> "Three layers of defense. (1) Data quality checks: row count comparison against historical baselines for each pipeline component, with alerts when any component deviates by > 2 standard deviations day-over-day. If live stream classification pipeline drops 23% of rows, the alert fires within 24 hours. (2) Metric decomposition monitoring: the composite VVR metric is decomposed into numerator (violating views) and denominator (total views), each further decomposed by data source. If the numerator/denominator ratio changes but the component contributions shift, that signals a data source issue, not a real safety change. (3) Automated validation of schema migrations: before any upstream schema change, a staging test verifies that the downstream pipeline produces row counts within 5% of production. The NOT NULL constraint that caused the silent drop would have been caught in staging."

### Follow-Ups for Round 3 (Skip-Level)

**"What would you do in your first 30 days?"**

> "Week 1-2: I would map the complete metrics stack — identify every dashboard, trace the data lineage from raw event logs to aggregated KPIs, and document the metric definitions including any known limitations. I would identify the top 5 metrics the team reviews weekly and for each understand: definition, data source, refresh cadence, historical trends, and known seasonality. I would also run a simple AA test to verify the randomization infrastructure produces balanced groups.
>
> Week 3-4: I would take ownership of one metric deep-dive. I would select a metric — say, false positive rate on content removal — and produce a comprehensive analysis: trend decomposition by content type, geography, language, and violation category; correlation with upstream classifier changes; and identification of measurement gaps. The deliverable would be a written report with 2-3 actionable recommendations. For example: 'FPR for Spanish-language content is 2.3x higher than English, likely due to classifier training data imbalance; recommend prioritizing Spanish-language labeling.'
>
> This approach establishes credibility through concrete output, not through learning abstractly."

**"How would you explain a 15% increase in VVR to a non-technical VP?"**

> "I would decompose the number and present it as a story with a decision at the end.
>
> 'The 15% increase has three possible causes, and I have investigated each: (1) Volume effect — we have 8% more content this month, which mechanically increases violations even if the rate is unchanged. This accounts for about 5pp of the increase. (2) Rate effect — the fraction of new content that violates policy increased from 0.15% to 0.17%, concentrated in short-form video. This accounts for about 7pp. (3) Detection effect — our new classifier catches more violations, so we are counting things we previously missed. This accounts for about 3pp and is actually a positive signal.
>
> Net: the real safety concern is the 7pp rate increase in short-form video. I recommend investigating whether a new abuse pattern has emerged in that category. The 5pp volume effect is expected growth. The 3pp detection effect means our investment in the new classifier is working.'
>
> The VP needs to know: is this bad, is it expected, and what do we do about it?"

**"What is the biggest risk in safety metrics?"**

> "Goodharting — optimizing the metric instead of the outcome the metric is supposed to measure. Three concrete examples:
>
> (1) If we optimize for VVR (violating view rate), teams might reduce it by removing content more aggressively — increasing FPR. The VVR number looks better but creator trust erodes. Defense: always pair VVR with an FPR guardrail.
>
> (2) If we optimize for time-to-action (how fast we respond to reports), teams might prioritize easy reports over hard ones. Average response time improves but the hardest, most harmful content gets deprioritized. Defense: measure time-to-action by severity tier separately.
>
> (3) If we optimize for classifier recall, teams might lower the confidence threshold, catching more violations but also generating more false positives. Recall goes up, but so does the appeals queue. Defense: track precision at the operating threshold, not just recall.
>
> The meta-solution is composite metrics like SAE (Story 11) and mandatory guardrails on every optimization target. No metric should be optimized in isolation."

### Follow-Ups for Round 4 (HRBP)

**"How do you handle feedback you disagree with?"**

> "I treat feedback as data. If my manager says 'your analysis is too technical for the audience,' I do not defend the analysis — I ask for the specific audience and decision context, then restructure the presentation. But if the feedback is methodological — 'use AUC-ROC instead of AUC-PR' — I prepare a quantitative comparison showing why the recommendation is wrong, present both analyses side by side, and let the data resolve the disagreement. This happened in Story 1 behavioral: my colleague proposed AUC-ROC on balanced data, I showed it overstated performance, and we adopted AUC-PR on production-representative data as the standard. I disagreed by producing evidence, not by arguing."

**"How do you stay current with new methods?"**

> "Three channels: (1) I read papers in my core areas — causal inference, experimentation methodology, adversarial ML — with a focus on papers that propose new methods with production applications, not just theoretical contributions. (2) I implement methods from papers on real data. My red-teaming protocol (Story 5) was inspired by recent adversarial robustness literature, adapted to our specific classifier. (3) I monitor industry blogs from experimentation teams at large platforms — they surface practical challenges (network effects, variance reduction, peeking) that academic papers often idealize away. The CUPED implementation (Story 7) came from reading about variance reduction at tech companies and implementing it from the original paper."

**"Tell me about a time you received constructive criticism."**

> "After presenting a classifier evaluation to a product team, the product lead told me that my analysis was technically correct but 'completely unusable for making a decision.' I had presented precision, recall, F1, AUC-PR, calibration curves, and fairness disaggregation — comprehensive but overwhelming. The feedback was valid: the product lead needed one number and one recommendation, not seven charts.
>
> I restructured my reporting approach. Now every analysis has a one-page executive summary: (1) the decision, (2) the recommendation, (3) the key number supporting the recommendation, (4) the confidence level. All supporting detail goes into appendices. The classifier evaluation became: 'Recommendation: do not deploy. The new classifier improves recall by 5pp but degrades precision by 8pp at the production threshold. At our current traffic volume, this means 2,400 more wrongful removals per day. Supporting detail in Appendix A.' The product lead adopted the recommendation immediately.
>
> The lesson: technical rigor and executive communication are complementary, not conflicting. I was doing the rigor but failing at the communication."

**"What motivates you?"**

> "Problems where the quality of the measurement directly determines the quality of the decision. In medical imaging, a poorly calibrated quality metric leads to deploying a suboptimal reconstruction method, which degrades diagnostic accuracy. In content safety, a poorly calibrated VVR leads to wrong resource allocation decisions, which leaves users exposed to harmful content.
>
> I find the meta-problem — 'is the metric itself trustworthy?' — more intellectually engaging than the object-level problem. Story 15 is the canonical example: a 12% VVR improvement that was actually 3.4% after correcting for a pipeline bug. The ability to distinguish real signal from measurement artifact is what separates data science from data reporting."

---

## Appendix C: Round Transition Notes

### Between Rounds — Mental Reset

After each round, take 60 seconds to:
1. Note which stories you already used (avoid repeating the same story in consecutive rounds)
2. Check which numbers you cited — ensure consistency
3. Remind yourself of the next round's emphasis

### Story Usage Tracker (Fill In During Interview)

| Story | Round 1 (Peer) | Round 2 (HM) | Round 3 (Skip) | Round 4 (HRBP) |
|---|---|---|---|---|
| 1 (GAN) | Self-intro | | | |
| 2 (Data loading) | | | Exploration bridge | |
| 3 (Validation) | Stats bridge | Case framework | Standards bridge | |
| 4 (LLM A/B) | Stats bridge | Open-ended | | |
| 5 (Red-team) | | Open-ended | | |
| 6 (Debiasing) | | | | |
| 7 (Sequential test) | | | | |
| 8 (Temporal features) | Python bridge | Feature eng. | | |
| 9 (Class imbalance) | Stats bridge | | | |
| 10 (Real-time) | | | Business | Day 1 value |
| 11 (SAE/DID) | | Case framework | Business tradeoff | |
| 12 (Phased rollout) | | | | Ambiguity Q |
| 13 (Prioritization) | | | | Prioritization Q |
| 14 (SQL) | SQL bridge | | | |
| 15 (Pipeline bug) | | | Exploration | Candor value |
| Behavioral 1 | | | | Conflict Q |
| Behavioral 2 | | | | Incomplete info Q |
| Behavioral 4 | | | | Failure Q |
| Behavioral 5 | | | | Leadership Q |

### Suggested Story Distribution Across Rounds

- **Round 1**: Stories 3, 4, 8, 9, 14 (stats, Python, SQL focus)
- **Round 2**: Stories 3, 4, 5, 10, 11 (cases, open-ended, measurement)
- **Round 3**: Stories 2, 5 behavioral, 11, 15 (exploration, business, proactive impact)
- **Round 4**: Stories behavioral 1-5, plus 1 (GAN for strengths), 10 (urgency), 15 (candor)

### Time Management Per Answer

- Self-intro: 2 minutes maximum
- STAR story: 2-3 minutes (Situation: 20 sec, Task: 10 sec, Action: 90 sec, Result: 30 sec)
- Case/open-ended: 4-5 minutes (framework: 30 sec, analysis: 3 min, recommendation: 1 min)
- SQL: write the query, then explain the business context in 30 seconds
- Behavioral: 2 minutes (lead with the technical decision, not the interpersonal dynamic)

### Red Flags to Avoid

1. **Do not** spend more than 30 seconds on the Situation. The HM wants to hear the Action.
2. **Do not** describe what you "would" do when you can describe what you "did." Hypotheticals signal inexperience.
3. **Do not** use the word "collaboration" without immediately following it with a specific technical action you took.
4. **Do not** cite a number without its context. "AUC improved to 0.94" means nothing without the baseline (0.89), the method (temporal features), and the business impact (1,200 review hours saved).
5. **Do not** answer a question about methodology with a result. If asked "how did you handle class imbalance," describe the technique (ensemble undersampling, SMOTE in CV loop, cost-sensitive learning), not just the outcome (AUC-PR 0.72).
6. **Do not** ask "what do you mean by X?" unless the question is genuinely ambiguous. Instead, state your interpretation and proceed: "I will interpret 'effectiveness' as a causal question: did the intervention cause the outcome change, controlling for confounders?"

---

## Appendix D: Questions to Ask Each Interviewer

### Round 1 (Peer)
- "What does the typical analysis workflow look like — from receiving a question to delivering a recommendation? What tools and infrastructure do you use?"
- "How is the experimentation platform set up? Does it support sequential testing and cluster randomization out of the box?"
- "What is the biggest data quality challenge the team faces today?"

### Round 2 (HM)
- "What is the most important metric the team owns, and what is the current measurement gap you most want to close?"
- "How do you evaluate DS performance — what does a strong first-quarter contribution look like?"
- "What is the balance between reactive work (incident response, ad-hoc requests) and proactive work (framework building, metric design)?"

### Round 3 (Skip-Level)
- "How does the DS function influence policy decisions? Is there a formal process for DS-recommended threshold changes or policy modifications?"
- "What distinguishes a senior DS from a staff DS in terms of scope and organizational influence?"
- "What is the team's long-term vision for experimentation methodology in I&S?"

### Round 4 (HRBP)
- "What does the onboarding process look like for this role?"
- "How does the team handle the operational intensity of safety — is there on-call rotation, and what is the expected response time for metric anomalies?"
- "What are the most common reasons people leave this team, and what keeps people here?"

These questions signal technical depth, ownership orientation, and genuine interest in the role's operating model.
