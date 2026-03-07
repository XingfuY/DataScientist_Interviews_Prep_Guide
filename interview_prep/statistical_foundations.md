# Statistical Foundations — Quick Reference for DS Interview Prep

**Cross-referenced from**: `tiktok_integrity_safety.md` (Section 3: Statistical & ML Foundations)
**Purpose**: Dense, practical reference covering 16 core statistical topics. Each topic includes formal theory, intuition, a TikTok Integrity & Safety use case, and executable Python code.
**Intended use**: Rapid review before interviews, not a textbook replacement.

---

## Table of Contents

1. [P-value, Significance Level, Confidence Level, Confidence Interval](#1-p-value-significance-level-confidence-level-confidence-interval)
2. [Common Distributions](#2-common-distributions)
3. [Central Limit Theorem](#3-central-limit-theorem)
4. [Law of Large Numbers](#4-law-of-large-numbers)
5. [Hypothesis Testing & Sample Size](#5-hypothesis-testing--sample-size)
6. [Estimator vs Estimate](#6-estimator-vs-estimate)
7. [Simpson's Paradox](#7-simpsons-paradox)
8. [Bias-Variance Tradeoff](#8-bias-variance-tradeoff)
9. [ANOVA](#9-anova)
10. [Bootstrap](#10-bootstrap)
11. [Type I and Type II Errors](#11-type-i-and-type-ii-errors)
12. [Precision vs Recall](#12-precision-vs-recall)
13. [Z-test and T-test](#13-z-test-and-t-test)
14. [Bayesian Formula / Conditional Probability](#14-bayesian-formula--conditional-probability)
15. [Maximum Likelihood Estimation](#15-maximum-likelihood-estimation)
16. [Regression](#16-regression)

---

## 1. P-value, Significance Level, Confidence Level, Confidence Interval

### Theory

**P-value**: The probability of observing a test statistic at least as extreme as the one computed from the data, *assuming the null hypothesis is true*. Formally:

$$p = P(T \geq t_{\text{obs}} \mid H_0)$$

for a one-sided test, where $T$ is the random test statistic and $t_{\text{obs}}$ is its observed value.

**Significance level** ($\alpha$): The pre-specified threshold for rejecting $H_0$. If $p \leq \alpha$, we reject. Common choices: 0.05, 0.01, 0.10. This is the maximum tolerable Type I error rate.

**Confidence level** ($1 - \alpha$): The long-run proportion of confidence intervals that contain the true parameter, across repeated sampling. A 95% CI means: if we repeated the experiment infinitely, 95% of the constructed intervals would cover the true value.

**Confidence interval**: An interval $[\hat{\theta}_L, \hat{\theta}_U]$ such that $P(\hat{\theta}_L \leq \theta \leq \hat{\theta}_U) = 1 - \alpha$ across repeated samples. For a mean with known variance: $\bar{x} \pm z_{\alpha/2} \cdot \sigma / \sqrt{n}$.

**Wilson score interval** (for proportions): Preferred over the Wald interval ($\hat{p} \pm z \sqrt{\hat{p}(1-\hat{p})/n}$) when $n$ is small or $p$ is near 0 or 1:

$$\tilde{p} = \frac{\hat{p} + \frac{z^2}{2n}}{1 + \frac{z^2}{n}}, \quad w = \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}$$

The interval is $[\tilde{p} - w, \tilde{p} + w]$.

### Crux

**The p-value is NOT $P(H_0 \mid \text{data})$.** It is $P(\text{data this extreme} \mid H_0)$. Confusing these is the single most common statistical error in industry. The probability that $H_0$ is true given the data requires Bayesian reasoning with a prior.

A non-significant result does NOT mean "no effect." It means "we failed to detect an effect at this sample size." Always report the confidence interval alongside the p-value — a CI of [-0.001, 0.050] tells a very different story than [-0.025, 0.025], even if both yield $p > 0.05$.

### Intuition

Think of a courtroom trial. The null hypothesis is "innocent." The p-value is: "How likely is this evidence if the defendant is truly innocent?" A small p-value means the evidence is very surprising under innocence, so we reject innocence. But we never *prove* guilt — we just find the innocence claim implausible.

### TikTok Use Case

In an A/B test measuring whether a new hate-speech classifier reduces violating view rate (VVR), you compute $p = 0.03$ for a 5% relative reduction. This means: if the classifier had *zero* true effect, there's only a 3% chance of seeing a reduction this large or larger by chance. At $\alpha = 0.05$, you reject the null and recommend launching.

But always report the CI: "VVR decreased by 5.0% (95% CI: [0.5%, 9.5%])." The CI communicates both statistical significance and practical significance — a 0.5% lower bound may be too small to justify the engineering cost.

The Wilson score interval matters here because VVR is a proportion, typically very small (e.g., 0.001). The standard Wald interval can produce negative lower bounds, which is nonsensical.

### Python Code Snippet

```python
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

# --- P-value computation for a two-sample proportion test ---
# Control: 10,000 content views, 15 violations (VVR = 0.0015)
# Treatment: 10,000 content views, 8 violations (VVR = 0.0008)
n_ctrl, x_ctrl = 10000, 15
n_treat, x_treat = 10000, 8

p_ctrl = x_ctrl / n_ctrl
p_treat = x_treat / n_treat
p_pool = (x_ctrl + x_treat) / (n_ctrl + n_treat)

se = np.sqrt(p_pool * (1 - p_pool) * (1/n_ctrl + 1/n_treat))
z_stat = (p_ctrl - p_treat) / se
p_value = 1 - stats.norm.cdf(z_stat)  # one-sided: is treatment lower?

print(f"Control VVR: {p_ctrl:.4f}, Treatment VVR: {p_treat:.4f}")
print(f"Z-statistic: {z_stat:.3f}, P-value (one-sided): {p_value:.4f}")

# --- Wilson score interval for treatment VVR ---
ci_low, ci_high = proportion_confint(x_treat, n_treat, alpha=0.05, method='wilson')
print(f"Wilson 95% CI for treatment VVR: [{ci_low:.5f}, {ci_high:.5f}]")

# --- Compare with Wald interval ---
ci_low_w, ci_high_w = proportion_confint(x_treat, n_treat, alpha=0.05, method='normal')
print(f"Wald 95% CI for treatment VVR:   [{ci_low_w:.5f}, {ci_high_w:.5f}]")
# Note: Wald can give negative lower bounds for small proportions
```

---

## 2. Common Distributions

### Theory

**Bernoulli($p$)**: Single binary trial. $P(X=1)=p$, $P(X=0)=1-p$. Mean: $p$. Variance: $p(1-p)$.

**Binomial($n, p$)**: Number of successes in $n$ independent Bernoulli trials.
$$P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}$$
Mean: $np$. Variance: $np(1-p)$.

**Geometric($p$)**: Number of trials until first success.
$$P(X=k) = (1-p)^{k-1} p, \quad k = 1, 2, \ldots$$
Mean: $1/p$. Variance: $(1-p)/p^2$. Memoryless property.

**Poisson($\lambda$)**: Count of events in a fixed interval when events occur independently at constant rate.
$$P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$$
Mean: $\lambda$. Variance: $\lambda$. Approximates Binomial when $n$ is large and $p$ is small ($\lambda = np$).

**Exponential($\lambda$)**: Time between Poisson events. Continuous analog of Geometric.
$$f(x) = \lambda e^{-\lambda x}, \quad x \geq 0$$
Mean: $1/\lambda$. Variance: $1/\lambda^2$. Memoryless: $P(X > s+t \mid X > s) = P(X > t)$.

**Normal($\mu, \sigma^2$)**:
$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$
Mean: $\mu$. Variance: $\sigma^2$. 68-95-99.7 rule. Sum of normals is normal. Central role via CLT.

### Crux

The Poisson-Binomial connection is critical for rare events: when you have millions of content items each with a tiny violation probability, the total violation count follows approximately Poisson($np$). This justifies using Poisson models for violation counts even when the underlying process is binomial.

The exponential distribution's memoryless property means: "the time until the next policy violation doesn't depend on how long it's been since the last one" — but only if violations truly arrive as a Poisson process. Bursty patterns (coordinated attacks) violate this assumption.

### Intuition

- **Bernoulli/Binomial**: Coin flips. Each content item is a coin that lands "violating" with probability $p$.
- **Geometric**: How many coins do you flip before the first heads? How many posts does a bad actor make before the first one gets caught?
- **Poisson**: You're counting raindrops hitting a window per minute. The count doesn't depend on which specific minute — just the rate.
- **Exponential**: How long between raindrops? If the rate is constant, this waiting time is exponential.
- **Normal**: The average of many random things. Thanks to CLT, the average violation rate across many regions is approximately normal regardless of the underlying distribution.

### TikTok Use Case

| Distribution | Safety Application |
|---|---|
| Bernoulli($p$) | Whether a single content item is a violation ($p \approx 0.001$) |
| Binomial($n, p$) | Number of violations in a batch of $n$ reviewed content items |
| Geometric($p$) | Number of posts by a repeat offender before first detection |
| Poisson($\lambda$) | Number of CSAM upload attempts per hour platform-wide |
| Exponential($\lambda$) | Time between consecutive coordinated harassment campaigns |
| Normal | Distribution of daily VVR across many regions (by CLT) |

Understanding which distribution applies determines the right test. Testing whether the hourly violation count increased? Use Poisson regression, not a t-test. Testing whether the probability of violation changed? Use a proportion test (binomial), not a test on counts.

### Python Code Snippet

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

np.random.seed(42)

# --- Poisson approximation to Binomial for rare violations ---
n_content = 1_000_000  # content items reviewed
p_violation = 0.001     # violation probability
lam = n_content * p_violation  # Poisson lambda = 1000

binom_samples = np.random.binomial(n_content, p_violation, size=10000)
poisson_samples = np.random.poisson(lam, size=10000)

print(f"Binomial  — mean: {binom_samples.mean():.1f}, std: {binom_samples.std():.1f}")
print(f"Poisson   — mean: {poisson_samples.mean():.1f}, std: {poisson_samples.std():.1f}")
# These should be nearly identical

# --- Geometric: expected posts before first detection ---
p_detect = 0.85  # classifier recall
expected_posts = 1 / p_detect
print(f"\nWith recall={p_detect}, expected posts before detection: {expected_posts:.2f}")
print(f"P(evades 5+ times) = {(1-p_detect)**5:.6f}")

# --- Exponential: inter-arrival time between incidents ---
avg_incidents_per_day = 3.0
inter_arrival = stats.expon(scale=1/avg_incidents_per_day)
print(f"\nAvg time between incidents: {inter_arrival.mean():.2f} days")
print(f"P(next incident within 4 hours = 1/6 day): {inter_arrival.cdf(1/6):.4f}")

# --- Verify Poisson mean=variance property ---
real_counts = np.random.poisson(lam=50, size=365)  # daily violation counts
print(f"\nPoisson sample — mean: {real_counts.mean():.1f}, variance: {real_counts.var():.1f}")
print(f"Overdispersed? ratio var/mean = {real_counts.var()/real_counts.mean():.2f} (should be ~1.0)")
```

---

## 3. Central Limit Theorem

### Theory

**Statement**: Let $X_1, X_2, \ldots, X_n$ be i.i.d. random variables with mean $\mu$ and finite variance $\sigma^2$. Then as $n \to \infty$:

$$\frac{\bar{X}_n - \mu}{\sigma / \sqrt{n}} \xrightarrow{d} N(0, 1)$$

The sample mean converges in distribution to a normal, regardless of the underlying distribution.

**Assumptions**: (1) Independence. (2) Identically distributed. (3) Finite variance ($\sigma^2 < \infty$).

**Rate of convergence (Berry-Esseen)**: The supremum distance between the CDF of the standardized sample mean and the standard normal CDF is bounded by:

$$\sup_x \left| P\left(\frac{\bar{X}_n - \mu}{\sigma/\sqrt{n}} \leq x\right) - \Phi(x) \right| \leq \frac{C \cdot \rho}{\sigma^3 \sqrt{n}}$$

where $\rho = E[|X - \mu|^3]$ and $C \leq 0.4748$. Key insight: the more skewed the distribution (higher $\rho/\sigma^3$), the slower the convergence.

**When CLT fails**:
- **Infinite variance**: Cauchy distribution, Pareto with $\alpha \leq 2$. The sample mean doesn't converge to normal — it stays heavy-tailed.
- **Dependence**: Autocorrelated time series. CLT still applies but $\sigma/\sqrt{n}$ underestimates the true standard error. Need Newey-West or HAC standard errors.
- **Small $n$ with high skew**: For exponential data, need $n \geq 30$; for extremely skewed data (e.g., revenue per user), may need $n > 1000$.

### Crux

CLT tells you the *shape* of the sampling distribution of $\bar{X}$, but you must verify the *assumptions*. In safety metrics, the biggest threat is dependence — content from the same creator is correlated, content viewed in the same session is correlated. If you ignore clustering, your standard errors are too small and your CIs too narrow, leading to inflated Type I error in A/B tests.

The practical question is always: "Is $n$ large enough?" For proportions near 0.5, $n = 30$ suffices. For proportions near 0.001 (violation rates), you may need $n > 10{,}000$ before the normal approximation is adequate.

### Intuition

Roll a die: the outcomes are uniform on {1,2,3,4,5,6}. Average the results of 2 dice: the distribution is triangular. Average 10 dice: it looks bell-shaped. Average 100 dice: it's indistinguishable from normal. CLT is the mathematical guarantee that this always happens (given finite variance), no matter how weird the original distribution.

### TikTok Use Case

When computing the daily violating view rate (VVR) across billions of views, each view is a Bernoulli trial (violating or not). The daily VVR is a sample mean of billions of Bernoulli variables. By CLT, the sampling distribution of daily VVR is extremely tight around the true rate — so even small day-over-day changes in VVR are statistically detectable.

However, if you compute VVR *per creator* and average across creators, the independence assumption may break (creators in the same niche have correlated violation rates). You need cluster-robust standard errors or hierarchical models.

-> See `tiktok_integrity_safety.md` Section 3 for how CLT informs A/B test design in safety experiments.

### Python Code Snippet

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# --- CLT demonstration with exponential (highly skewed) data ---
lam_rate = 1.0  # exponential with mean=1, var=1, skewness=2
true_mean = 1.0
true_std = 1.0

sample_sizes = [5, 30, 100, 1000]

for n in sample_sizes:
    sample_means = [np.random.exponential(1/lam_rate, size=n).mean()
                    for _ in range(10000)]
    sample_means = np.array(sample_means)
    standardized = (sample_means - true_mean) / (true_std / np.sqrt(n))

    # Test normality of standardized sample means
    _, p_shapiro = stats.shapiro(standardized[:500])  # shapiro limited to 5000
    print(f"n={n:>4d}: mean(X_bar)={sample_means.mean():.4f}, "
          f"std(X_bar)={sample_means.std():.4f} "
          f"(theory={true_std/np.sqrt(n):.4f}), "
          f"Shapiro p={p_shapiro:.4f}")

# --- Berry-Esseen: skewed distribution converges slower ---
# Compare convergence for symmetric (uniform) vs skewed (exponential)
n = 30
for dist_name, sampler, mu, sigma in [
    ("Uniform[0,1]", lambda s: np.random.uniform(0, 1, s), 0.5, 1/np.sqrt(12)),
    ("Exponential(1)", lambda s: np.random.exponential(1, s), 1.0, 1.0),
]:
    means = np.array([sampler(n).mean() for _ in range(10000)])
    standardized = (means - mu) / (sigma / np.sqrt(n))
    ks_stat, ks_p = stats.kstest(standardized, 'norm')
    print(f"\n{dist_name}, n={n}: KS stat={ks_stat:.4f}, p={ks_p:.4f}")

# --- Dependence breaks CLT standard errors ---
# Simulate autocorrelated data (AR(1))
n = 1000
rho = 0.8  # autocorrelation
x = np.zeros(n)
x[0] = np.random.normal()
for i in range(1, n):
    x[i] = rho * x[i-1] + np.random.normal()

naive_se = x.std() / np.sqrt(n)
# True SE for AR(1): sigma / sqrt(n) * sqrt((1+rho)/(1-rho))
true_se = x.std() / np.sqrt(n) * np.sqrt((1 + rho) / (1 - rho))
print(f"\nAR(1) with rho={rho}:")
print(f"  Naive SE:  {naive_se:.4f}")
print(f"  Correct SE: {true_se:.4f}  ({true_se/naive_se:.1f}x larger)")
```

---

## 4. Law of Large Numbers

### Theory

**Weak Law of Large Numbers (WLLN)**: For i.i.d. random variables with mean $\mu$:

$$\bar{X}_n \xrightarrow{P} \mu$$

Convergence in probability: $\forall \epsilon > 0$, $P(|\bar{X}_n - \mu| > \epsilon) \to 0$ as $n \to \infty$.

**Strong Law of Large Numbers (SLLN)**: Under the same conditions:

$$\bar{X}_n \xrightarrow{a.s.} \mu$$

Almost sure convergence: $P(\lim_{n \to \infty} \bar{X}_n = \mu) = 1$.

**Key difference**: WLLN says "unlikely to be far away for any given large $n$." SLLN says "eventually stays close forever, with probability 1." The SLLN is strictly stronger — almost sure convergence implies convergence in probability, but not vice versa.

**Conditions**: WLLN requires finite mean. SLLN requires i.i.d. with finite mean (Kolmogorov's version). If variance is infinite but mean is finite, SLLN still holds but convergence is slow.

### Crux

LLN guarantees that your sample metric converges to the truth as sample size grows — but it says nothing about the *rate*. CLT gives you the rate ($1/\sqrt{n}$). LLN is the justification for using sample averages as estimates; CLT is the justification for putting error bars on them.

Practical trap: LLN assumes the underlying distribution is stable. If the violation rate is trending upward (non-stationary), the sample average of historical data converges to the wrong value. Always check stationarity before trusting long-run averages.

### Intuition

Flip a fair coin 10 times — you might get 70% heads. Flip it 10,000 times — you'll get very close to 50% heads. LLN is the mathematical guarantee that the proportion of heads converges to the true probability. The more data you collect, the closer your estimate gets to reality.

### TikTok Use Case

When estimating the platform-wide violation rate, each day's sample of reviewed content contributes to a running average. LLN guarantees that as the number of reviewed items grows, the estimated violation rate converges to the true rate.

But TikTok's content landscape is non-stationary — new violation types emerge, classifier updates change detection rates, seasonal trends affect posting behavior. This means naive historical averaging (relying on LLN over long periods) is dangerous. Use exponentially weighted moving averages or rolling windows to respect non-stationarity while still leveraging LLN within each window.

-> See `applied_ds_tutorial.md` for dashboarding applications of running averages and EWMA.

### Python Code Snippet

```python
import numpy as np

np.random.seed(42)

# --- LLN convergence for violation rate estimation ---
true_violation_rate = 0.0015
n_max = 100000

# Simulate content reviews (Bernoulli trials)
reviews = np.random.binomial(1, true_violation_rate, size=n_max)

# Running average at each sample size
cumulative_mean = np.cumsum(reviews) / np.arange(1, n_max + 1)

# Show convergence at key points
for n in [100, 1000, 10000, 100000]:
    est = cumulative_mean[n - 1]
    error = abs(est - true_violation_rate)
    print(f"n={n:>6d}: estimated rate = {est:.6f}, "
          f"|error| = {error:.6f}, "
          f"relative error = {error/true_violation_rate:.1%}")

# --- Non-stationarity: LLN fails when distribution shifts ---
# Violation rate doubles at midpoint (e.g., new policy, new attack vector)
rate_1 = 0.001
rate_2 = 0.002
n_half = 50000
reviews_shift = np.concatenate([
    np.random.binomial(1, rate_1, n_half),
    np.random.binomial(1, rate_2, n_half)
])
cum_mean_shift = np.cumsum(reviews_shift) / np.arange(1, 2 * n_half + 1)

print(f"\nNon-stationary case (rate shifts from {rate_1} to {rate_2}):")
print(f"  Naive average over all data: {cum_mean_shift[-1]:.6f}")
print(f"  Average over last half only: {reviews_shift[n_half:].mean():.6f}")
print(f"  True current rate:           {rate_2:.6f}")

# --- EWMA to handle non-stationarity ---
alpha_ewma = 0.01
ewma = np.zeros(2 * n_half)
ewma[0] = reviews_shift[0]
for i in range(1, len(reviews_shift)):
    ewma[i] = alpha_ewma * reviews_shift[i] + (1 - alpha_ewma) * ewma[i-1]

print(f"  EWMA estimate at end:        {ewma[-1]:.6f}")
```

---

## 5. Hypothesis Testing & Sample Size

### Theory

**Framework**:
1. **Null hypothesis** $H_0$: The default claim (e.g., no difference between treatment and control).
2. **Alternative hypothesis** $H_1$: What we're trying to detect (e.g., treatment reduces violation rate).
3. **Test statistic**: A function of the data that measures departure from $H_0$ (e.g., Z-statistic, t-statistic).
4. **Rejection region**: The set of test statistic values leading to rejection, determined by $\alpha$.
5. **Decision**: If the test statistic falls in the rejection region (equivalently, if $p \leq \alpha$), reject $H_0$.

**Power**: $1 - \beta = P(\text{reject } H_0 \mid H_1 \text{ is true})$. The probability of detecting a real effect. Convention: target 80% power ($\beta = 0.20$).

**Sample size for comparing two proportions** (two-sided test):

$$n = \frac{(z_{\alpha/2} + z_\beta)^2 \left[p_1(1-p_1) + p_2(1-p_2)\right]}{(p_1 - p_2)^2}$$

where $p_1$ is control proportion, $p_2$ is treatment proportion.

**Sample size for comparing two means**:

$$n = \frac{2(z_{\alpha/2} + z_\beta)^2 \sigma^2}{(\mu_1 - \mu_2)^2}$$

**Minimum detectable effect (MDE)**: The smallest effect size the test can detect at the specified power and alpha:

$$\text{MDE} = (z_{\alpha/2} + z_\beta) \cdot \sqrt{\frac{2 \hat{p}(1-\hat{p})}{n}}$$

for proportions, or $(z_{\alpha/2} + z_\beta) \cdot \sigma \sqrt{2/n}$ for means.

### Crux

In content safety, violation rates are tiny ($p \approx 0.001$) and effects are often small (5-10% relative change). This means sample sizes are enormous. For $p = 0.001$, a 10% relative change ($\Delta = 0.0001$), $\alpha = 0.05$, power = 0.80:

$$n \approx \frac{(1.96 + 0.84)^2 \cdot 2 \cdot 0.001 \cdot 0.999}{0.0001^2} \approx 1{,}566{,}000 \text{ per group}$$

This is why ratio metrics (violation rate = violations / views) and variance reduction techniques (CUPED) are essential in safety experiments.

### Intuition

You're listening for a faint signal in noise. Power analysis asks: "Given the noise level (variance), how much data (sample size) do I need to reliably hear a signal of a given loudness (effect size)?" Bigger effects are easier to hear. More noise requires more data. Demanding more certainty (lower $\alpha$) requires more data. Everything is a tradeoff.

### TikTok Use Case

Before launching an A/B test for a new content classifier, the DS must answer: "How many content items do we need in each arm, and how long must the test run?" If the expected improvement in VVR is 5% relative (from 0.0010 to 0.00095), the required sample size per arm is approximately 7.8 million views. At 50M views/day per arm, the test needs ~4 hours. But if the expected improvement is only 1% relative, the test needs ~100 hours.

This calculation fundamentally determines whether an experiment is feasible. If the required duration exceeds the team's patience or the policy's urgency, consider alternative approaches: use a more sensitive metric, apply CUPED variance reduction, or use a Bayesian decision framework.

### Python Code Snippet

```python
import numpy as np
from scipy import stats
from statsmodels.stats.power import NormalIndPower, tt_ind_solve_power
from statsmodels.stats.proportion import proportion_effectsize

# --- Sample size for proportion test (violation rate reduction) ---
p_control = 0.001     # baseline violation rate
relative_effect = 0.10  # 10% relative reduction
p_treatment = p_control * (1 - relative_effect)

# Effect size (Cohen's h for proportions)
effect_size_h = proportion_effectsize(p_control, p_treatment)

power_analysis = NormalIndPower()
n_per_group = power_analysis.solve_power(
    effect_size=effect_size_h,
    alpha=0.05,
    power=0.80,
    alternative='two-sided'
)
print(f"Baseline VVR: {p_control}, Target: {p_treatment}")
print(f"Effect size (Cohen's h): {effect_size_h:.6f}")
print(f"Required n per group: {n_per_group:,.0f}")

# --- MDE given fixed sample size ---
n_available = 500_000
mde_h = power_analysis.solve_power(
    nobs1=n_available,
    alpha=0.05,
    power=0.80,
    alternative='two-sided'
)
# Convert back to proportion difference
# h = 2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))
# approximate: delta_p ≈ h * sqrt(p*(1-p))
mde_absolute = mde_h * np.sqrt(p_control * (1 - p_control))
print(f"\nWith n={n_available:,} per group:")
print(f"  MDE (Cohen's h): {mde_h:.6f}")
print(f"  MDE (absolute proportion): {mde_absolute:.6f}")
print(f"  MDE (relative to baseline): {mde_absolute/p_control:.1%}")

# --- Sample size for means (e.g., time-to-action on violations) ---
# Baseline: mean = 120 seconds, sd = 200 seconds
# Want to detect 10% reduction (12 second improvement)
effect_d = 12 / 200  # Cohen's d = delta / sd
n_means = tt_ind_solve_power(effect_size=effect_d, alpha=0.05, power=0.80)
print(f"\nTime-to-action test:")
print(f"  Effect size (Cohen's d): {effect_d:.3f}")
print(f"  Required n per group: {n_means:,.0f}")
```

---

## 6. Estimator vs Estimate

### Theory

**Estimator**: A rule (function) $\hat{\theta}(X_1, \ldots, X_n)$ that maps data to a parameter estimate. It is a random variable — before data is collected, it has a distribution.

**Estimate**: A specific numerical value obtained by applying the estimator to observed data. It is a fixed number.

**Properties of estimators**:

- **Bias**: $\text{Bias}(\hat{\theta}) = E[\hat{\theta}] - \theta$. An estimator is unbiased if $E[\hat{\theta}] = \theta$.
- **Consistency**: $\hat{\theta}_n \xrightarrow{P} \theta$ as $n \to \infty$. The estimator converges to the truth.
- **Efficiency**: Among unbiased estimators, the one with smallest variance. Measured by relative efficiency: $\text{RE} = \text{Var}(\hat{\theta}_1) / \text{Var}(\hat{\theta}_2)$.
- **Sufficiency**: $\hat{\theta}$ is sufficient if it captures all information in the data about $\theta$. Formally: $P(X \mid \hat{\theta})$ does not depend on $\theta$.
- **MVUE**: Minimum Variance Unbiased Estimator. The best you can do among unbiased estimators (Rao-Blackwell theorem + Lehmann-Scheffe).

**MLE as estimator**: The Maximum Likelihood Estimator is consistent, asymptotically normal, and asymptotically efficient (achieves Cramer-Rao bound). But it can be biased in finite samples (e.g., MLE of variance is $\frac{1}{n}\sum(x_i - \bar{x})^2$, which is biased; Bessel's correction gives the unbiased $s^2 = \frac{1}{n-1}\sum(x_i - \bar{x})^2$).

**Standard error vs standard deviation**: SD measures variability of data. SE measures variability of an estimator. $SE(\bar{X}) = \sigma / \sqrt{n}$. The SE decreases with $n$; the SD does not (it's a property of the population).

### Crux

The critical distinction: **you can have a biased estimator that's better than an unbiased one** if it has much lower variance. This is the entire basis of regularization (Ridge, Lasso), shrinkage estimators (James-Stein), and Bayesian estimation. MSE = Bias^2 + Variance, and sometimes accepting a little bias dramatically reduces variance, lowering MSE.

### Intuition

An estimator is a recipe for making guesses. An estimate is one particular guess. If the recipe consistently overestimates (biased), you can correct it. If the recipe is noisy (high variance), you need more data. The best recipe minimizes total error (MSE), even if that means being slightly biased.

### TikTok Use Case

When estimating the platform-wide false positive rate (FPR) of content moderation, the sample FPR from human review is an estimator. Key considerations:

- **Bias**: If human reviewers are selected from a non-random sample (e.g., only reviewing appealed items), the FPR estimator is biased upward (appeals are enriched for false positives). Correction: use a stratified random sample.
- **Consistency**: As we review more items, the estimated FPR converges to the true FPR — but only if the sampling is representative.
- **Standard error**: With 1000 reviewed items and observed FPR = 0.05, the SE is $\sqrt{0.05 \cdot 0.95 / 1000} \approx 0.007$. This tells us the estimate is $0.05 \pm 0.014$ (95% CI).

### Python Code Snippet

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# --- Bias of variance estimators ---
true_mu = 10.0
true_var = 4.0
n = 10
n_simulations = 100000

biased_vars = []
unbiased_vars = []
for _ in range(n_simulations):
    sample = np.random.normal(true_mu, np.sqrt(true_var), n)
    biased_vars.append(np.var(sample, ddof=0))      # MLE: divide by n
    unbiased_vars.append(np.var(sample, ddof=1))     # Bessel: divide by n-1

print(f"True variance: {true_var:.4f}")
print(f"MLE (biased):   E[s^2_MLE] = {np.mean(biased_vars):.4f} "
      f"(bias = {np.mean(biased_vars) - true_var:.4f})")
print(f"Bessel (unbiased): E[s^2] = {np.mean(unbiased_vars):.4f} "
      f"(bias = {np.mean(unbiased_vars) - true_var:.4f})")

# --- MSE comparison: biased but lower MSE ---
# James-Stein-like shrinkage example
true_theta = 3.0
shrinkage_factor = 0.8  # shrink toward 0

naive_estimates = []
shrunk_estimates = []
for _ in range(n_simulations):
    sample = np.random.normal(true_theta, 2.0, size=5)
    x_bar = sample.mean()
    naive_estimates.append(x_bar)
    shrunk_estimates.append(shrinkage_factor * x_bar)

mse_naive = np.mean([(e - true_theta)**2 for e in naive_estimates])
mse_shrunk = np.mean([(e - true_theta)**2 for e in shrunk_estimates])
bias_shrunk = np.mean(shrunk_estimates) - true_theta

print(f"\nNaive estimator (unbiased): MSE = {mse_naive:.4f}")
print(f"Shrunk estimator: MSE = {mse_shrunk:.4f}, Bias = {bias_shrunk:.4f}")
print(f"MSE reduction: {(1 - mse_shrunk/mse_naive)*100:.1f}%")

# --- Standard error vs standard deviation ---
data = np.random.exponential(scale=5.0, size=100)
sd = data.std(ddof=1)
se = sd / np.sqrt(len(data))
print(f"\nSample SD (data spread): {sd:.3f}")
print(f"SE of mean (precision of estimate): {se:.3f}")
print(f"Ratio SD/SE = sqrt(n) = {sd/se:.1f}")
```

---

## 7. Simpson's Paradox

### Theory

**Definition**: A trend that appears in several groups of data reverses or disappears when the groups are combined. Formally, it is possible for:

$$P(Y \mid X, Z=z) > P(Y \mid \neg X, Z=z) \quad \forall z$$

but simultaneously:

$$P(Y \mid X) < P(Y \mid \neg X)$$

This occurs when the confounding variable $Z$ is associated with both $X$ (the treatment/exposure) and $Y$ (the outcome), and the group sizes are imbalanced.

**Correction**: Stratify by the confounding variable and report stratum-specific results. When causal interpretation is needed, use the adjustment formula:

$$P(Y \mid do(X)) = \sum_z P(Y \mid X, Z=z) P(Z=z)$$

**Causal interpretation via DAGs**: Simpson's paradox arises when there's a common cause (confounder) of both the treatment and outcome. The DAG is: $Z \to X$, $Z \to Y$, $X \to Y$. Conditioning on $Z$ blocks the backdoor path $X \leftarrow Z \to Y$, revealing the true causal effect $X \to Y$.

However, not all reversals should be "corrected." If $Z$ is a mediator ($X \to Z \to Y$), conditioning on $Z$ blocks the causal path and gives the *wrong* answer. You must draw the DAG before deciding whether to stratify.

### Crux

The aggregated numbers are not "wrong" — they're answering a different question. The stratified numbers answer "what is the effect within each group?" The aggregated numbers answer "what is the overall marginal relationship?" Which is the right question depends on the causal structure. Simpson's paradox is not a statistical anomaly — it's a failure to think causally.

### Intuition

Berkeley admissions: overall, women had a lower acceptance rate than men. But within every department, women had equal or higher acceptance rates. The resolution: women applied more to competitive departments. The aggregate masked the confounding effect of department choice.

### TikTok Use Case

**Content moderation accuracy by region**: Suppose the overall precision of the hate speech classifier is 85% in Region A and 90% in Region B. Aggregated across regions, precision is 83%. How? Region A has 10x more content, and Region A's content is harder to classify (more nuanced language). The overall precision is dragged down by the sheer volume of Region A content, not by inferior performance in any single region.

**Actionable consequence**: When the VP asks "why is precision dropping?", don't just report the aggregate. Decompose by region, language, content type, and violation category. The paradox often reveals that precision is *improving* everywhere, but the mix of content is shifting toward harder categories.

### Python Code Snippet

```python
import numpy as np
import pandas as pd

# --- Simpson's Paradox: content moderation accuracy ---
# Two regions, two content difficulty levels

np.random.seed(42)

data = {
    'Region': ['A']*4 + ['B']*4,
    'Difficulty': ['Easy', 'Easy', 'Hard', 'Hard'] * 2,
    'Classifier': ['New', 'Old'] * 4,
    'Correct': [950, 900, 700, 650, 190, 180, 70, 65],
    'Total':   [1000, 1000, 1000, 1000, 200, 200, 100, 100],
}
df = pd.DataFrame(data)
df['Accuracy'] = df['Correct'] / df['Total']

print("=== Stratified by Difficulty ===")
for diff in ['Easy', 'Hard']:
    sub = df[df['Difficulty'] == diff]
    for clf in ['New', 'Old']:
        row = sub[sub['Classifier'] == clf]
        acc = row['Correct'].sum() / row['Total'].sum()
        print(f"  {diff}, {clf}: accuracy = {acc:.3f}")

print("\n=== Aggregated (Simpson's Paradox) ===")
for clf in ['New', 'Old']:
    sub = df[df['Classifier'] == clf]
    acc = sub['Correct'].sum() / sub['Total'].sum()
    print(f"  {clf} classifier: overall accuracy = {acc:.3f}")

# The New classifier is better within every stratum,
# but may appear worse overall if it handles more Hard content.

# --- Causal correction via stratification ---
print("\n=== Correctly weighted comparison ===")
# Weight each stratum by the SAME distribution
for clf in ['New', 'Old']:
    sub = df[df['Classifier'] == clf]
    # Compute accuracy within each difficulty stratum
    acc_easy = sub[sub['Difficulty']=='Easy']['Correct'].sum() / \
               sub[sub['Difficulty']=='Easy']['Total'].sum()
    acc_hard = sub[sub['Difficulty']=='Hard']['Correct'].sum() / \
               sub[sub['Difficulty']=='Hard']['Total'].sum()
    # Standardize to equal weight for each difficulty
    standardized_acc = 0.5 * acc_easy + 0.5 * acc_hard
    print(f"  {clf} classifier (standardized): {standardized_acc:.3f}")
```

---

## 8. Bias-Variance Tradeoff

### Theory

For any estimator $\hat{f}(x)$ of a function $f(x)$, the expected prediction error decomposes:

$$E[(Y - \hat{f}(x))^2] = \text{Bias}(\hat{f}(x))^2 + \text{Var}(\hat{f}(x)) + \sigma^2_\epsilon$$

where $\sigma^2_\epsilon$ is the irreducible noise (Bayes error).

- **Bias**: $E[\hat{f}(x)] - f(x)$. Error from oversimplifying the model. High bias = underfitting.
- **Variance**: $E[(\hat{f}(x) - E[\hat{f}(x)])^2]$. Sensitivity to training set fluctuations. High variance = overfitting.

**Regularization** trades bias for variance:
- **L2 (Ridge)**: Adds $\lambda \|\beta\|_2^2$ to the loss. Shrinks coefficients toward zero. Increases bias, decreases variance.
- **L1 (Lasso)**: Adds $\lambda \|\beta\|_1$. Induces sparsity (some coefficients exactly zero). Feature selection + regularization.
- **ElasticNet**: $\alpha \|\beta\|_1 + (1-\alpha)\|\beta\|_2^2$. Combines both.

**Cross-validation**: Empirical method to estimate the bias-variance tradeoff. K-fold CV partitions data into K folds, trains on K-1, evaluates on the held-out fold. The average test error across folds estimates generalization error (which includes both bias and variance contributions).

### Crux

The practical manifestation: a model that performs spectacularly on training data but poorly on test data is high-variance (overfitting). A model that performs poorly on both is high-bias (underfitting). The sweet spot is where increasing complexity no longer reduces test error — the U-shaped test error curve.

Modern deep learning complicates this: very overparameterized models can have zero training error but still generalize well ("double descent"). But for the tabular models common in safety DS work (XGBoost, logistic regression), the classical tradeoff holds.

### Intuition

Imagine fitting a curve through noisy data points. A straight line (low complexity) misses the true pattern (high bias, low variance). A polynomial of degree $n-1$ passes through every point (zero bias, high variance) but oscillates wildly. The best fit is somewhere in between.

### TikTok Use Case

Building a content violation classifier: a very deep neural network (high complexity) might memorize the training examples of hate speech, learning idiosyncratic patterns that don't generalize to new hateful content. A logistic regression on TF-IDF features (low complexity) might miss subtle violations. The production model uses moderate complexity (fine-tuned transformer with dropout, weight decay, and early stopping) to balance bias and variance.

When comparing a simpler XGBoost model to a large transformer for a specific violation type (e.g., spam detection), the XGBoost model might actually win if training data is limited (< 10K examples) because its lower variance compensates for slightly higher bias.

### Python Code Snippet

```python
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error

np.random.seed(42)

# --- Bias-Variance Tradeoff: polynomial regression ---
# True function: f(x) = sin(2*pi*x)
n_train = 30
x_train = np.random.uniform(0, 1, n_train)
y_train = np.sin(2 * np.pi * x_train) + np.random.normal(0, 0.3, n_train)

x_test = np.linspace(0, 1, 200)
y_true = np.sin(2 * np.pi * x_test)

print("Polynomial degree | Train MSE | CV Test MSE | Bias^2+Var proxy")
print("-" * 65)

for degree in [1, 3, 5, 10, 20]:
    model = make_pipeline(
        PolynomialFeatures(degree),
        Ridge(alpha=1e-6)  # tiny regularization for numerical stability
    )
    model.fit(x_train.reshape(-1, 1), y_train)

    y_pred_train = model.predict(x_train.reshape(-1, 1))
    train_mse = mean_squared_error(y_train, y_pred_train)

    # CV estimate of test error
    cv_scores = cross_val_score(model, x_train.reshape(-1, 1), y_train,
                                 cv=5, scoring='neg_mean_squared_error')
    cv_mse = -cv_scores.mean()

    print(f"  {degree:>2d}              | {train_mse:.4f}    | {cv_mse:.4f}      | "
          f"{'underfitting' if degree < 3 else 'good' if degree <= 5 else 'overfitting'}")

# --- Regularization strength tradeoff ---
print("\n--- Ridge regularization (degree=10 polynomial) ---")
for alpha in [0.001, 0.01, 0.1, 1.0, 10.0]:
    model = make_pipeline(PolynomialFeatures(10), Ridge(alpha=alpha))
    cv_scores = cross_val_score(model, x_train.reshape(-1, 1), y_train,
                                 cv=5, scoring='neg_mean_squared_error')
    print(f"  alpha={alpha:<6.3f}: CV MSE = {-cv_scores.mean():.4f}")
```

---

## 9. ANOVA

### Theory

**One-way ANOVA**: Tests whether the means of $k$ groups are all equal.
- $H_0$: $\mu_1 = \mu_2 = \cdots = \mu_k$
- $H_1$: At least one $\mu_i$ differs.

**F-statistic**:

$$F = \frac{MS_{\text{between}}}{MS_{\text{within}}} = \frac{SS_B / (k-1)}{SS_W / (N-k)}$$

where $SS_B = \sum_{i=1}^k n_i (\bar{X}_i - \bar{X})^2$ (between-group sum of squares) and $SS_W = \sum_{i=1}^k \sum_{j=1}^{n_i} (X_{ij} - \bar{X}_i)^2$ (within-group sum of squares).

Under $H_0$, $F \sim F(k-1, N-k)$.

**Assumptions**: (1) Independence of observations. (2) Normality within each group (robust to violations with large $n$ by CLT). (3) Homoscedasticity — equal variances across groups (Levene's test to check; Welch's ANOVA if violated).

**Post-hoc tests** (only after rejecting $H_0$):
- **Tukey HSD**: Controls family-wise error rate (FWER). All pairwise comparisons.
- **Bonferroni**: Conservative FWER control. Adjusts $\alpha$ by $\alpha / m$ where $m$ is the number of comparisons.
- **Holm-Bonferroni**: Step-down procedure, less conservative than Bonferroni.

**Non-parametric alternative**: **Kruskal-Wallis test**. Rank-based. No normality assumption. Tests whether the distributions (not just means) differ. Post-hoc: Dunn's test with Bonferroni correction.

### Crux

ANOVA tells you *whether* groups differ, not *which* groups differ or by *how much*. Always follow up with post-hoc tests and effect size measures ($\eta^2 = SS_B / SS_T$).

The biggest practical mistake: using ANOVA when observations are not independent. If you compare moderation accuracy across 5 regions, but each region has autocorrelated daily metrics, the F-test is anticonservative (too many false positives). Use mixed-effects models or cluster-robust methods instead.

### Intuition

ANOVA asks: "Is the variation *between* groups large relative to the variation *within* groups?" If the between-group spread is much larger than the within-group noise, the group means are probably truly different. The F-statistic is literally the ratio of these two sources of variation.

### TikTok Use Case

**Comparing moderation accuracy across 4 regions** (NA, EMEA, APAC, LATAM): Is there a significant difference in false positive rates? Run one-way ANOVA on daily FPR values. If significant, Tukey HSD reveals which pairs of regions differ.

**Comparing 3 versions of a content classifier**: Deploy variants A, B, C to random user segments. Collect precision per segment-day. ANOVA tests whether the classifiers perform equally. If normality is suspect (small sample, skewed metrics), use Kruskal-Wallis.

### Python Code Snippet

```python
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

np.random.seed(42)

# --- One-way ANOVA: FPR across 4 regions ---
# Simulate daily FPR for 30 days per region
regions = {
    'NA':    np.random.normal(0.045, 0.008, 30),
    'EMEA':  np.random.normal(0.052, 0.010, 30),
    'APAC':  np.random.normal(0.048, 0.009, 30),
    'LATAM': np.random.normal(0.058, 0.012, 30),
}

# ANOVA
f_stat, p_value = stats.f_oneway(*regions.values())
print(f"One-way ANOVA: F={f_stat:.3f}, p={p_value:.4f}")

# Effect size (eta-squared)
all_data = np.concatenate(list(regions.values()))
grand_mean = all_data.mean()
ss_between = sum(len(v) * (v.mean() - grand_mean)**2 for v in regions.values())
ss_total = np.sum((all_data - grand_mean)**2)
eta_sq = ss_between / ss_total
print(f"Eta-squared (effect size): {eta_sq:.3f}")

# Tukey HSD post-hoc
labels = np.concatenate([[k]*len(v) for k, v in regions.items()])
tukey = pairwise_tukeyhsd(all_data, labels, alpha=0.05)
print(f"\nTukey HSD post-hoc:\n{tukey}")

# --- Levene's test for homoscedasticity ---
lev_stat, lev_p = stats.levene(*regions.values())
print(f"\nLevene's test: stat={lev_stat:.3f}, p={lev_p:.4f}")
if lev_p < 0.05:
    print("  Variances are unequal — use Welch's ANOVA instead")

# --- Kruskal-Wallis (non-parametric alternative) ---
kw_stat, kw_p = stats.kruskal(*regions.values())
print(f"\nKruskal-Wallis: H={kw_stat:.3f}, p={kw_p:.4f}")

# --- Welch's ANOVA (if homoscedasticity violated) ---
# scipy doesn't have Welch's ANOVA directly; use pingouin or manual
# Approximation: use Alexander-Govern test or just use Kruskal-Wallis
```

---

## 10. Bootstrap

### Theory

**Non-parametric bootstrap**: Given a sample of size $n$, draw $B$ resamples of size $n$ with replacement. Compute the statistic of interest on each resample. The distribution of the $B$ bootstrapped statistics approximates the sampling distribution.

**Procedure**:
1. Compute $\hat{\theta}$ on original data.
2. For $b = 1, \ldots, B$: draw $X^*_b$ (sample with replacement from data), compute $\hat{\theta}^*_b$.
3. Use the distribution of $\{\hat{\theta}^*_b\}$ for inference (CI, SE, bias).

**Bootstrap confidence intervals**:
- **Percentile method**: $[q_{\alpha/2}, q_{1-\alpha/2}]$ of the bootstrap distribution. Simple but biased.
- **BCa (bias-corrected and accelerated)**: Corrects for both bias and skewness of the bootstrap distribution. Preferred for serious inference.
- **Studentized bootstrap**: Bootstrap the pivotal quantity $(hat{\theta}^* - \hat{\theta}) / \widehat{SE}^*$. Most accurate coverage but computationally expensive (requires nested bootstrap for SE estimation).

**When to use bootstrap**:
- Complex statistics with no closed-form SE (median, ratio of means, quantiles).
- Small samples where asymptotic approximations are poor.
- Unknown underlying distribution.
- Paired comparisons in A/B tests (bootstrap the difference).

**When bootstrap fails**:
- Extremes (max, min) — bootstrap is inconsistent for extreme order statistics.
- Very small samples ($n < 10$) — resampling from too few points doesn't capture the population.
- Dependent data — need block bootstrap or stationary bootstrap.

### Crux

Bootstrap is not magic — it cannot create information that isn't in the data. It approximates the sampling distribution by treating the empirical distribution as the population. If your sample is unrepresentative (selection bias), the bootstrap faithfully replicates that bias.

For A/B tests, the **paired bootstrap** is particularly powerful: resample *pairs* (user_i_control, user_i_treatment) to preserve within-user correlation, then compute the test statistic on each resample.

### Intuition

You have one bag of marbles (your sample). You can't go back to the factory (population) to get more bags. Instead, you reach into your bag, grab a marble, note its color, put it back, repeat $n$ times — that's one bootstrap sample. Do this 10,000 times, and the variation across these resampled bags tells you how uncertain your estimate is.

### TikTok Use Case

Estimating the median time-to-action (time from content creation to enforcement action) has no closed-form SE — the distribution is heavily right-skewed with outliers (some violations take days to detect). Bootstrap provides the confidence interval:

1. Collect 5,000 enforcement actions with their time-to-action values.
2. Bootstrap 10,000 resamples.
3. Report: "Median time-to-action: 23 minutes (95% BCa CI: [19, 28] minutes)."

For A/B tests comparing two classifier variants, bootstrap the per-user difference in violation exposure to get a CI on the treatment effect that doesn't assume normality.

### Python Code Snippet

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# --- Bootstrap CI for median time-to-action ---
# Simulate right-skewed enforcement times (lognormal)
n = 500
time_to_action = np.random.lognormal(mean=3.0, sigma=1.2, size=n)  # in minutes
observed_median = np.median(time_to_action)

# Non-parametric bootstrap
B = 10000
boot_medians = np.array([
    np.median(np.random.choice(time_to_action, size=n, replace=True))
    for _ in range(B)
])

# Percentile CI
ci_percentile = np.percentile(boot_medians, [2.5, 97.5])

# BCa CI (using scipy)
# BCa requires bias correction factor (z0) and acceleration (a)
z0 = stats.norm.ppf(np.mean(boot_medians < observed_median))
# Jackknife for acceleration
jackknife_medians = np.array([
    np.median(np.delete(time_to_action, i)) for i in range(n)
])
jack_mean = jackknife_medians.mean()
a = np.sum((jack_mean - jackknife_medians)**3) / \
    (6 * np.sum((jack_mean - jackknife_medians)**2)**1.5)

# Adjusted percentiles
alpha_vals = [0.025, 0.975]
bca_percentiles = []
for alpha in alpha_vals:
    z_alpha = stats.norm.ppf(alpha)
    adjusted = stats.norm.cdf(z0 + (z0 + z_alpha) / (1 - a * (z0 + z_alpha)))
    bca_percentiles.append(np.percentile(boot_medians, 100 * adjusted))

print(f"Observed median time-to-action: {observed_median:.1f} minutes")
print(f"Bootstrap SE: {boot_medians.std():.1f} minutes")
print(f"Percentile 95% CI: [{ci_percentile[0]:.1f}, {ci_percentile[1]:.1f}]")
print(f"BCa 95% CI:        [{bca_percentiles[0]:.1f}, {bca_percentiles[1]:.1f}]")

# --- Paired bootstrap for A/B test ---
n_users = 1000
# Per-user violation exposure (Poisson)
control_exposure = np.random.poisson(lam=2.5, size=n_users)
treatment_exposure = np.random.poisson(lam=2.2, size=n_users)
observed_diff = treatment_exposure.mean() - control_exposure.mean()

boot_diffs = []
for _ in range(B):
    idx = np.random.randint(0, n_users, size=n_users)
    boot_diff = treatment_exposure[idx].mean() - control_exposure[idx].mean()
    boot_diffs.append(boot_diff)
boot_diffs = np.array(boot_diffs)

ci_diff = np.percentile(boot_diffs, [2.5, 97.5])
print(f"\nA/B Test (paired bootstrap):")
print(f"  Mean difference: {observed_diff:.3f}")
print(f"  95% CI: [{ci_diff[0]:.3f}, {ci_diff[1]:.3f}]")
print(f"  Significant at 5%? {'Yes' if ci_diff[1] < 0 or ci_diff[0] > 0 else 'No'}")
```

---

## 11. Type I and Type II Errors

### Theory

| | $H_0$ True (No Effect) | $H_0$ False (Real Effect) |
|---|---|---|
| **Reject $H_0$** | Type I Error ($\alpha$) | Correct (Power = $1-\beta$) |
| **Fail to Reject** | Correct ($1-\alpha$) | Type II Error ($\beta$) |

**Type I Error** ($\alpha$, false positive): Rejecting $H_0$ when it's true. Concluding an effect exists when it doesn't. Controlled by the significance level.

**Type II Error** ($\beta$, false negative): Failing to reject $H_0$ when $H_1$ is true. Missing a real effect. Controlled by power ($1-\beta$), which depends on sample size, effect size, and $\alpha$.

**Power** = $1 - \beta$. The probability of correctly detecting a real effect.

**Relationship**: For fixed sample size, decreasing $\alpha$ (more conservative) increases $\beta$ (less power). You can only reduce both simultaneously by increasing $n$.

**Operating Characteristic (OC) curve**: Plots $\beta$ (or $1-\beta$) as a function of the true effect size. Shows how power increases as the true effect gets larger.

**Multiple testing**: Running $m$ tests each at $\alpha = 0.05$ gives a family-wise error rate of $1 - (1-\alpha)^m \approx m\alpha$ for small $\alpha$. Corrections: Bonferroni ($\alpha/m$), Holm, Benjamini-Hochberg (FDR control).

### Crux

**Cost asymmetry in content safety is the key insight.** The costs of Type I and Type II errors are radically different depending on the violation type:

| Violation Type | Type I (wrongful removal) | Type II (missed violation) |
|---|---|---|
| CSAM | Low cost — better safe | Catastrophic — legal liability, child harm |
| Spam | Moderate — creator frustration | Low — user annoyance |
| Hate speech | High — free expression concerns | High — user harm, brand damage |

This asymmetry means you should NOT use the same $\alpha$ threshold for all violation types. For CSAM, accept high Type I error (aggressive removal). For borderline hate speech, balance both error types carefully.

### Intuition

Type I is a false alarm (fire alarm goes off, no fire). Type II is a missed detection (real fire, alarm didn't sound). In content safety, a missed CSAM detection is a fire that burns the building down; a false alarm on spam is a mild inconvenience. Set your alarm sensitivity accordingly.

### TikTok Use Case

When evaluating an A/B test for a new enforcement policy:
- **Type I**: Launching a policy that actually has no effect (wasted engineering effort, possible user disruption).
- **Type II**: Not launching a policy that would have reduced violations (continued user harm).

For a rare but severe violation type (CSAM, violent extremism), the team should use $\alpha = 0.10$ (accept higher false positive risk) and require only 70% power, because the cost of a Type II error (not deploying an effective defense) far outweighs the cost of a Type I error.

For engagement-impacting policies (content demotion), use stricter $\alpha = 0.01$ and 90% power, because a wrong launch could harm creator livelihoods at scale.

-> See `tiktok_integrity_safety.md` for full A/B testing framework including multiple testing correction.

### Python Code Snippet

```python
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

np.random.seed(42)

# --- Operating Characteristic Curve ---
# How power varies with true effect size
n_per_group = 100000
p_control = 0.001
alpha = 0.05

true_effects = np.linspace(0, 0.0005, 50)  # absolute reduction in violation rate
powers = []

for delta in true_effects:
    p_treat = p_control - delta
    if p_treat < 0:
        powers.append(1.0)
        continue
    # Compute power via normal approximation
    p_pool = (p_control + p_treat) / 2
    se_null = np.sqrt(2 * p_pool * (1 - p_pool) / n_per_group)
    se_alt = np.sqrt((p_control*(1-p_control) + p_treat*(1-p_treat)) / n_per_group)
    z_crit = stats.norm.ppf(1 - alpha/2)
    z_power = (delta - z_crit * se_null) / se_alt
    power = stats.norm.cdf(z_power)
    powers.append(power)

# Report key points
for delta_pct in [5, 10, 20, 50]:
    delta = p_control * delta_pct / 100
    idx = np.argmin(np.abs(true_effects - delta))
    print(f"Relative effect {delta_pct}% (delta={delta:.6f}): "
          f"Power = {powers[idx]:.3f}")

# --- Multiple testing correction ---
# Suppose we test 5 violation categories simultaneously
p_values = [0.03, 0.12, 0.04, 0.008, 0.25]
categories = ['Hate Speech', 'Spam', 'Harassment', 'CSAM', 'Misinformation']

# Bonferroni
bonf_threshold = 0.05 / len(p_values)
print(f"\nBonferroni threshold: {bonf_threshold:.3f}")
for cat, p in zip(categories, p_values):
    sig = "REJECT" if p < bonf_threshold else "fail to reject"
    print(f"  {cat}: p={p:.3f} -> {sig}")

# Benjamini-Hochberg (FDR control)
from statsmodels.stats.multitest import multipletests
reject_bh, pvals_corrected, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')
print(f"\nBenjamini-Hochberg (FDR=0.05):")
for cat, p, rej, p_adj in zip(categories, p_values, reject_bh, pvals_corrected):
    sig = "REJECT" if rej else "fail to reject"
    print(f"  {cat}: p={p:.3f}, adjusted p={p_adj:.3f} -> {sig}")
```

---

## 12. Precision vs Recall

### Theory

**Confusion matrix** (for binary classification):

| | Predicted Positive | Predicted Negative |
|---|---|---|
| **Actually Positive** | True Positive (TP) | False Negative (FN) |
| **Actually Negative** | False Positive (FP) | True Negative (TN) |

**Precision**: $\frac{TP}{TP + FP}$ — Of everything flagged, what fraction is truly positive?

**Recall (Sensitivity/TPR)**: $\frac{TP}{TP + FN}$ — Of everything truly positive, what fraction did we catch?

**Specificity (TNR)**: $\frac{TN}{TN + FP}$ — Of everything truly negative, what fraction did we correctly leave alone?

**F1 score**: Harmonic mean of precision and recall: $F_1 = \frac{2 \cdot P \cdot R}{P + R}$.

**F-beta score**: $F_\beta = \frac{(1 + \beta^2) \cdot P \cdot R}{\beta^2 \cdot P + R}$. When $\beta > 1$, recall is weighted more heavily. When $\beta < 1$, precision is weighted more.

**PR curve vs ROC curve**: For imbalanced data (e.g., 0.1% violation rate), the ROC curve (TPR vs FPR) can be misleadingly optimistic because TN dominates FP. The PR curve directly shows the precision-recall tradeoff and is more informative when the positive class is rare.

**AUPRC** (area under PR curve) is the preferred summary metric for imbalanced classification. A random classifier has AUPRC equal to the positive class prevalence ($\pi$), while a random classifier has AUROC = 0.5 regardless of class balance.

### Crux

In content safety, precision and recall have *directly interpretable* meanings:
- **Precision** = 1 - (wrongful removal rate). Low precision means creators have content removed unfairly.
- **Recall** = catch rate. Low recall means violating content stays on the platform.

The threshold is a policy lever, not a technical parameter. Moving the threshold changes the precision-recall tradeoff. The optimal threshold depends on the cost ratio: $\frac{C_{FN}}{C_{FP}} = \frac{\text{cost of missed violation}}{\text{cost of wrongful removal}}$.

### Intuition

Precision: "When I say it's a violation, how often am I right?" Recall: "Of all the actual violations, how many did I catch?" A system that flags everything has perfect recall (catches 100% of violations) but terrible precision (also flags innocent content). A system that flags nothing has undefined precision but zero recall.

### TikTok Use Case

For a hate speech classifier deployed on TikTok:
- Precision = 0.85 means 15% of removed content was actually compliant (wrongful removals). Creators file appeals, lose trust.
- Recall = 0.70 means 30% of hate speech stays on the platform. Users experience harm.

**Threshold selection**: If wrongful removal leads to creator churn (cost: lost revenue) and missed hate speech leads to user harm + regulatory fines (cost: brand damage + legal), estimate the cost ratio and set the threshold accordingly:

$$\text{Optimal threshold where} \quad \frac{dP}{dR} = -\frac{C_{FN}}{C_{FP}} \cdot \frac{1-\pi}{\pi}$$

For CSAM: $C_{FN} \gg C_{FP}$, so optimize for recall ($F_2$ or higher). For spam: costs are more balanced, so optimize for $F_1$.

### Python Code Snippet

```python
import numpy as np
from sklearn.metrics import (precision_score, recall_score, f1_score,
                              precision_recall_curve, roc_curve, auc,
                              average_precision_score, confusion_matrix)

np.random.seed(42)

# --- Simulated content classifier output ---
n_content = 100000
violation_rate = 0.005  # 0.5% violation rate (imbalanced)

y_true = np.random.binomial(1, violation_rate, n_content)
# Classifier scores: violations get higher scores on average
scores = np.where(y_true == 1,
                  np.random.beta(5, 2, n_content),    # violations: skewed right
                  np.random.beta(2, 5, n_content))     # clean: skewed left

# --- PR curve and threshold selection ---
precision_arr, recall_arr, thresholds = precision_recall_curve(y_true, scores)
auprc = average_precision_score(y_true, scores)
fpr, tpr, _ = roc_curve(y_true, scores)
auroc = auc(fpr, tpr)

print(f"AUPRC: {auprc:.4f} (random baseline: {violation_rate:.4f})")
print(f"AUROC: {auroc:.4f} (random baseline: 0.5000)")

# --- Different thresholds for different cost structures ---
cost_ratios = {
    'CSAM (recall-heavy)': 100,    # missed violation is 100x worse than false removal
    'Hate speech (balanced)': 5,
    'Spam (precision-heavy)': 1,
}

print(f"\n{'Policy':<30s} | Threshold | Precision | Recall | F-beta")
print("-" * 78)

for policy, cost_ratio in cost_ratios.items():
    beta = np.sqrt(cost_ratio)  # F-beta: beta^2 = C_FN / C_FP
    # Find threshold maximizing F-beta
    best_fb, best_thresh = 0, 0
    for t in np.arange(0.1, 0.9, 0.01):
        y_pred = (scores >= t).astype(int)
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        if p + r == 0:
            continue
        fb = (1 + beta**2) * p * r / (beta**2 * p + r)
        if fb > best_fb:
            best_fb = fb
            best_thresh = t

    y_pred = (scores >= best_thresh).astype(int)
    p = precision_score(y_true, y_pred)
    r = recall_score(y_true, y_pred)
    print(f"{policy:<30s} | {best_thresh:.2f}      | {p:.3f}     | {r:.3f}  | {best_fb:.3f}")

# --- Confusion matrix at balanced threshold ---
threshold = 0.50
y_pred = (scores >= threshold).astype(int)
cm = confusion_matrix(y_true, y_pred)
tn, fp, fn, tp = cm.ravel()
print(f"\nAt threshold={threshold}: TP={tp}, FP={fp}, FN={fn}, TN={tn}")
print(f"  Wrongful removal rate: {fp/(fp+tp):.1%}")
print(f"  Miss rate: {fn/(fn+tp):.1%}")
```

---

## 13. Z-test and T-test

### Theory

**Z-test** (population variance known or large $n$):
$$Z = \frac{\bar{X} - \mu_0}{\sigma / \sqrt{n}} \sim N(0,1)$$

**One-sample t-test** (population variance unknown):
$$t = \frac{\bar{X} - \mu_0}{s / \sqrt{n}} \sim t(n-1)$$

**Two-sample t-test** (equal variances assumed — Student's):
$$t = \frac{\bar{X}_1 - \bar{X}_2}{s_p \sqrt{1/n_1 + 1/n_2}}, \quad s_p = \sqrt{\frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}}$$

**Welch's t-test** (unequal variances — preferred default):
$$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}, \quad df = \frac{(s_1^2/n_1 + s_2^2/n_2)^2}{\frac{(s_1^2/n_1)^2}{n_1-1} + \frac{(s_2^2/n_2)^2}{n_2-1}}$$

**Paired t-test**: Compute differences $d_i = X_{1i} - X_{2i}$, then apply one-sample t-test to $\{d_i\}$:
$$t = \frac{\bar{d}}{s_d / \sqrt{n}} \sim t(n-1)$$

**Assumptions**: (1) Independence (between samples for two-sample; within pairs for paired). (2) Normality (of data for small $n$; of $\bar{X}$ for large $n$ by CLT). (3) Equal variances for Student's t-test (Welch's relaxes this).

**Relationship to F-test**: For two groups, $F = t^2$ with $F(1, n_1+n_2-2)$. ANOVA generalizes the two-sample t-test to $k$ groups.

**When to use which**:
- Known $\sigma$ or very large $n$ ($>$10,000): Z-test (but t-test gives essentially the same result).
- Unknown $\sigma$, small to moderate $n$: t-test.
- Possibly unequal variances: Welch's t-test (always safe — no loss of power when variances are actually equal).
- Before-after comparison on the same units: Paired t-test.

### Crux

**Always use Welch's t-test as the default.** The classical Student's t-test assumes equal variances, which is rarely testable and often violated. Welch's t-test is robust and has almost identical power when variances happen to be equal. There is no good reason to use Student's t-test in practice.

For proportions (content violation rates), use a Z-test for proportions or Fisher's exact test for small counts, not a t-test. The t-test assumes continuous data.

### Intuition

Both Z and t tests ask: "Is the observed difference large relative to the noise?" The Z-test knows the true noise level ($\sigma$). The t-test has to estimate it from data ($s$), which introduces extra uncertainty — that's why t-distributions have heavier tails than the normal. With large $n$, the estimation is precise, and t converges to Z.

### TikTok Use Case

**Two-sample Welch's t-test**: Compare average daily time-to-action between two enforcement systems (automated vs human review). $n_1 = 200$ days of automated data, $n_2 = 200$ days of human review data, with potentially different variances.

**Paired t-test**: Same set of 500 content items reviewed by both Classifier A and Classifier B. Compute per-item score difference and test whether the mean difference is zero.

**Z-test for proportions**: Compare violation detection rates between treatment and control arms in an A/B test with millions of observations.

### Python Code Snippet

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# --- Two-sample Welch's t-test: time-to-action comparison ---
auto_times = np.random.lognormal(mean=2.5, sigma=0.8, size=200)   # automated
human_times = np.random.lognormal(mean=3.0, sigma=1.2, size=200)  # human review

# Welch's t-test (default in scipy)
t_stat, p_value = stats.ttest_ind(auto_times, human_times, equal_var=False)
print(f"Welch's t-test: t={t_stat:.3f}, p={p_value:.4f}")
print(f"  Auto mean: {auto_times.mean():.1f} min, Human mean: {human_times.mean():.1f} min")

# Compare with Student's t-test (assumes equal variance — dangerous)
t_stat_s, p_value_s = stats.ttest_ind(auto_times, human_times, equal_var=True)
print(f"Student's t-test: t={t_stat_s:.3f}, p={p_value_s:.4f}")
print(f"  (Different from Welch's because variances differ: "
      f"{auto_times.var():.1f} vs {human_times.var():.1f})")

# --- Paired t-test: same content, two classifiers ---
n_items = 500
# Classifier scores (0-1) for same content items
scores_A = np.random.beta(3, 2, n_items)
scores_B = scores_A + np.random.normal(0.02, 0.05, n_items)  # B slightly better
scores_B = np.clip(scores_B, 0, 1)

t_paired, p_paired = stats.ttest_rel(scores_B, scores_A)
print(f"\nPaired t-test: t={t_paired:.3f}, p={p_paired:.4f}")
print(f"  Mean improvement (B - A): {(scores_B - scores_A).mean():.4f}")

# --- Z-test for proportions (large sample A/B test) ---
from statsmodels.stats.proportion import proportions_ztest

# Control: 1M views, 1050 violations; Treatment: 1M views, 980 violations
counts = np.array([1050, 980])
nobs = np.array([1000000, 1000000])

z_stat, p_val = proportions_ztest(counts, nobs, alternative='two-sided')
print(f"\nZ-test for proportions: z={z_stat:.3f}, p={p_val:.4f}")
print(f"  Control VVR: {counts[0]/nobs[0]:.6f}")
print(f"  Treatment VVR: {counts[1]/nobs[1]:.6f}")
print(f"  Relative reduction: {1 - counts[1]*nobs[0]/(counts[0]*nobs[1]):.1%}")

# --- Degrees of freedom: Welch vs Student ---
n1, n2 = 15, 30
s1, s2 = 5.0, 12.0  # very different variances
df_student = n1 + n2 - 2
df_welch = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
print(f"\nDegrees of freedom comparison (n1={n1}, n2={n2}, s1={s1}, s2={s2}):")
print(f"  Student: df = {df_student}")
print(f"  Welch:   df = {df_welch:.1f}")
```

---

## 14. Bayesian Formula / Conditional Probability

### Theory

**Bayes' theorem**:

$$P(A \mid B) = \frac{P(B \mid A) \cdot P(A)}{P(B)}$$

In the context of statistical inference:

$$P(\theta \mid \text{data}) = \frac{P(\text{data} \mid \theta) \cdot P(\theta)}{P(\text{data})}$$

- **Prior** $P(\theta)$: Belief about $\theta$ before seeing data.
- **Likelihood** $P(\text{data} \mid \theta)$: Probability of the data given the parameter.
- **Posterior** $P(\theta \mid \text{data})$: Updated belief after seeing data.
- **Evidence** $P(\text{data}) = \int P(\text{data} \mid \theta) P(\theta) d\theta$: Normalizing constant.

**Conjugate priors**: When the prior and posterior belong to the same family, simplifying updates:

| Likelihood | Conjugate Prior | Posterior |
|---|---|---|
| Binomial | Beta($\alpha, \beta$) | Beta($\alpha + k, \beta + n - k$) |
| Poisson | Gamma($\alpha, \beta$) | Gamma($\alpha + \sum x_i, \beta + n$) |
| Normal (known $\sigma$) | Normal($\mu_0, \sigma_0^2$) | Normal($\mu_n, \sigma_n^2$) |

**Naive Bayes classifier**: Assumes feature independence given the class label:

$$P(Y \mid X_1, \ldots, X_p) \propto P(Y) \prod_{j=1}^p P(X_j \mid Y)$$

Despite the "naive" independence assumption, works surprisingly well for text classification due to the "blessing of dimensionality" — errors in individual feature probabilities tend to cancel out.

### Crux

The posterior is a *compromise* between the prior and the data. With little data, the posterior is dominated by the prior. With lots of data, the posterior is dominated by the likelihood (data overwhelms the prior). This is why Bayesian and frequentist methods converge for large samples.

For safety applications, the prior encodes domain knowledge: "We know the base rate of CSAM is approximately 0.001%." This prevents the model from hallucinating extreme estimates from small samples (e.g., seeing 2 CSAM items in 100 reviews and concluding the rate is 2%).

### Intuition

You're a doctor. A patient tests positive for a rare disease (prevalence 1 in 1000). The test has 99% sensitivity and 99% specificity. What's the probability they actually have the disease? Bayes' theorem says: only about 9%. Why? Because the prior (1/1000) is so low that even a good test produces mostly false positives. This is exactly the situation in content safety: violation rates are low, so even a good classifier flags mostly clean content.

### TikTok Use Case

**Updating violation probability**: A new account posts content. The prior probability of violation is 0.5% (base rate). The account triggers a behavioral signal (posting frequency > 100/day) that has $P(\text{signal} \mid \text{violator}) = 0.30$ and $P(\text{signal} \mid \text{non-violator}) = 0.01$.

$$P(\text{violator} \mid \text{signal}) = \frac{0.30 \times 0.005}{0.30 \times 0.005 + 0.01 \times 0.995} = \frac{0.0015}{0.01145} = 0.131$$

The signal raises the probability from 0.5% to 13.1% — a 26x increase, but still far from certain. This justifies escalating to human review rather than auto-removing.

**Bayesian A/B testing**: Instead of a p-value, compute $P(\text{treatment is better} \mid \text{data})$ directly. If this posterior probability exceeds 95%, launch. This is often more intuitive for stakeholders than "reject the null at $\alpha = 0.05$."

-> See `tiktok_integrity_safety.md` for Bayesian approaches to sequential testing.

### Python Code Snippet

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# --- Bayes' theorem: disease screening analogy ---
prevalence = 0.001      # P(disease) = 0.1%
sensitivity = 0.99      # P(positive | disease)
specificity = 0.99      # P(negative | no disease)

p_positive = sensitivity * prevalence + (1 - specificity) * (1 - prevalence)
p_disease_given_positive = sensitivity * prevalence / p_positive

print(f"P(disease | positive test) = {p_disease_given_positive:.4f}")
print(f"  Even with 99% sensitivity/specificity and 0.1% prevalence,")
print(f"  a positive test only means {p_disease_given_positive:.1%} chance of disease.\n")

# --- Bayesian updating for violation rate (Beta-Binomial) ---
# Prior: Beta(1, 999) — expect ~0.1% violation rate
alpha_prior, beta_prior = 1, 999

# Observe: 50 content items reviewed, 3 violations
n_obs, k_obs = 50, 3

# Posterior: Beta(alpha + k, beta + n - k)
alpha_post = alpha_prior + k_obs
beta_post = beta_prior + (n_obs - k_obs)

prior = stats.beta(alpha_prior, beta_prior)
posterior = stats.beta(alpha_post, beta_post)

print(f"Prior:     Beta({alpha_prior}, {beta_prior})")
print(f"  Mean = {prior.mean():.4f}, 95% CI = [{prior.ppf(0.025):.4f}, {prior.ppf(0.975):.4f}]")
print(f"Observed:  {k_obs}/{n_obs} = {k_obs/n_obs:.4f}")
print(f"Posterior: Beta({alpha_post}, {beta_post})")
print(f"  Mean = {posterior.mean():.4f}, 95% CI = [{posterior.ppf(0.025):.4f}, {posterior.ppf(0.975):.4f}]")

# --- Bayesian A/B test ---
# Control: 10000 items, 15 violations. Treatment: 10000 items, 8 violations
alpha_A = 1 + 15
beta_A = 1 + 10000 - 15
alpha_B = 1 + 8
beta_B = 1 + 10000 - 8

# Monte Carlo: P(treatment rate < control rate)
n_mc = 100000
samples_A = np.random.beta(alpha_A, beta_A, n_mc)
samples_B = np.random.beta(alpha_B, beta_B, n_mc)
p_B_better = np.mean(samples_B < samples_A)

print(f"\nBayesian A/B test:")
print(f"  Control violation rate:   {(alpha_A-1)/10000:.4f}")
print(f"  Treatment violation rate: {(alpha_B-1)/10000:.4f}")
print(f"  P(treatment is better) = {p_B_better:.4f}")

# --- Naive Bayes for content classification (toy example) ---
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

texts = [
    "buy cheap followers now", "get free likes instantly",
    "beautiful sunset over the ocean", "my cat is sleeping",
    "click link in bio for deals", "follow for follow back",
    "hiking in the mountains today", "cooking dinner with friends"
]
labels = [1, 1, 0, 0, 1, 1, 0, 0]  # 1=spam, 0=clean

vec = CountVectorizer()
X = vec.fit_transform(texts)
clf = MultinomialNB(alpha=1.0)  # Laplace smoothing
clf.fit(X, labels)

test = vec.transform(["free followers click now"])
prob = clf.predict_proba(test)[0]
print(f"\nNaive Bayes spam classifier:")
print(f"  'free followers click now' -> P(spam) = {prob[1]:.3f}")
```

---

## 15. Maximum Likelihood Estimation

### Theory

**Likelihood function**: Given data $x = (x_1, \ldots, x_n)$ and parameter $\theta$:

$$L(\theta \mid x) = \prod_{i=1}^n f(x_i \mid \theta)$$

**Log-likelihood** (more tractable):

$$\ell(\theta) = \sum_{i=1}^n \log f(x_i \mid \theta)$$

**MLE**: $\hat{\theta}_{MLE} = \arg\max_\theta \ell(\theta)$. Found by solving the score equation: $\frac{\partial \ell}{\partial \theta} = 0$.

**Properties of MLE**:
1. **Consistency**: $\hat{\theta}_{MLE} \xrightarrow{P} \theta_0$ (true parameter).
2. **Asymptotic normality**: $\sqrt{n}(\hat{\theta}_{MLE} - \theta_0) \xrightarrow{d} N(0, I(\theta_0)^{-1})$.
3. **Asymptotic efficiency**: Achieves the Cramer-Rao lower bound.
4. **Invariance**: If $\hat{\theta}$ is MLE of $\theta$, then $g(\hat{\theta})$ is MLE of $g(\theta)$.

**Fisher information**:

$$I(\theta) = -E\left[\frac{\partial^2 \ell}{\partial \theta^2}\right] = E\left[\left(\frac{\partial \ell}{\partial \theta}\right)^2\right]$$

Measures how much information data carries about $\theta$. Higher information means more precise estimation.

**Cramer-Rao bound**: For any unbiased estimator $\hat{\theta}$:

$$\text{Var}(\hat{\theta}) \geq \frac{1}{n \cdot I(\theta)}$$

The MLE achieves this bound asymptotically — it's the most efficient estimator for large samples.

**MLE for common distributions**:
- Bernoulli($p$): $\hat{p} = \bar{x}$
- Poisson($\lambda$): $\hat{\lambda} = \bar{x}$
- Normal($\mu, \sigma^2$): $\hat{\mu} = \bar{x}$, $\hat{\sigma}^2 = \frac{1}{n}\sum(x_i - \bar{x})^2$ (biased for $\sigma^2$)
- Exponential($\lambda$): $\hat{\lambda} = 1/\bar{x}$

**Connection to logistic regression**: Logistic regression coefficients are found by MLE. The log-likelihood is:

$$\ell(\beta) = \sum_{i=1}^n [y_i \log p_i + (1 - y_i) \log(1 - p_i)]$$

where $p_i = \sigma(\beta^T x_i)$. This is the negative cross-entropy loss.

### Crux

MLE is the *foundation* of most parametric statistical methods. When you fit a logistic regression, train a Poisson GLM, or estimate a mixture model, you're doing MLE. Understanding MLE means understanding why these methods work, when they fail (model misspecification, separation in logistic regression, multimodal likelihoods), and how to diagnose problems (checking the Hessian for positive-definiteness, inspecting the likelihood surface).

The key weakness: MLE assumes the model is correctly specified. If the true data-generating process isn't in your model family, MLE finds the closest match in KL divergence, which may still be far from the truth.

### Intuition

MLE asks: "Which parameter value makes the observed data most probable?" If you flip a coin 100 times and get 60 heads, the MLE is $\hat{p} = 0.60$ because that's the value of $p$ that maximizes the probability of seeing exactly 60 heads in 100 flips. It's the most "honest" explanation of the data within the assumed model.

### TikTok Use Case

**Estimating violation rates per content category**: Each category (hate speech, spam, CSAM, etc.) has its own violation rate. MLE gives $\hat{p}_k = \text{violations}_k / \text{total}_k$. Fisher information gives the precision: for a rate of 0.001 with 1M observations, $I(p) = 1/[p(1-p)] \approx 1001$, so $SE = 1/\sqrt{n \cdot I(p)} \approx 0.00003$.

**Logistic regression for violation risk scoring**: Fit a logistic model predicting $P(\text{violation} \mid \text{features})$. The MLE coefficients tell you the log-odds change per unit increase in each feature. "Accounts with > 100 posts/day have a log-odds increase of 2.3 for being spam accounts, meaning $e^{2.3} = 10\times$ higher odds."

### Python Code Snippet

```python
import numpy as np
from scipy import stats, optimize

np.random.seed(42)

# --- MLE for Poisson (closed-form) ---
# Observed daily violation counts
violation_counts = np.random.poisson(lam=45, size=30)

lambda_mle = violation_counts.mean()
lambda_se = np.sqrt(lambda_mle / len(violation_counts))

print(f"Poisson MLE: lambda_hat = {lambda_mle:.2f}")
print(f"  SE = {lambda_se:.2f}")
print(f"  95% CI: [{lambda_mle - 1.96*lambda_se:.2f}, {lambda_mle + 1.96*lambda_se:.2f}]")

# --- MLE for Exponential via numerical optimization ---
# Time between incidents (minutes)
inter_arrival = np.random.exponential(scale=20.0, size=50)

def neg_log_likelihood_exp(lam, data):
    """Negative log-likelihood for Exponential(lambda)."""
    if lam <= 0:
        return np.inf
    return -np.sum(np.log(lam) - lam * data)

result = optimize.minimize_scalar(
    neg_log_likelihood_exp, bounds=(0.001, 1.0), method='bounded',
    args=(inter_arrival,)
)
lambda_mle_exp = result.x
scale_mle = 1 / lambda_mle_exp

print(f"\nExponential MLE (numerical):")
print(f"  lambda_hat = {lambda_mle_exp:.4f} (rate)")
print(f"  scale_hat = {scale_mle:.2f} minutes (mean inter-arrival)")
print(f"  Closed-form: {1/inter_arrival.mean():.4f} (should match)")

# --- Fisher Information and Cramer-Rao bound ---
# For Bernoulli(p): I(p) = 1 / [p(1-p)]
# For n observations: Var(p_hat) >= 1 / [n * I(p)] = p(1-p)/n
p_true = 0.001
n = 1_000_000
fisher_info = 1 / (p_true * (1 - p_true))
cramer_rao_var = 1 / (n * fisher_info)
cramer_rao_se = np.sqrt(cramer_rao_var)

print(f"\nCramer-Rao bound for Bernoulli({p_true}), n={n:,}:")
print(f"  Fisher information: I(p) = {fisher_info:.2f}")
print(f"  Minimum variance: {cramer_rao_var:.2e}")
print(f"  Minimum SE: {cramer_rao_se:.6f}")

# --- MLE for logistic regression (connection to cross-entropy) ---
from sklearn.linear_model import LogisticRegression

# Simulated features: post frequency, account age, follower ratio
n = 5000
X = np.column_stack([
    np.random.exponential(10, n),      # posts per day
    np.random.exponential(180, n),     # account age in days
    np.random.beta(2, 5, n),           # follower/following ratio
])

# True log-odds: high frequency + low age + low ratio -> violation
logits = 0.05 * X[:, 0] - 0.01 * X[:, 1] - 2.0 * X[:, 2] - 1.0
p_violation = 1 / (1 + np.exp(-logits))
y = np.random.binomial(1, p_violation)

model = LogisticRegression(penalty=None, max_iter=1000)
model.fit(X, y)

print(f"\nLogistic Regression MLE coefficients:")
feature_names = ['posts_per_day', 'account_age', 'follower_ratio']
for name, coef in zip(feature_names, model.coef_[0]):
    odds_ratio = np.exp(coef)
    print(f"  {name}: beta={coef:.4f}, OR={odds_ratio:.3f}")
print(f"  intercept: {model.intercept_[0]:.4f}")
```

---

## 16. Regression

### Theory

**Ordinary Least Squares (OLS)**:

$$\hat{\beta} = (X^T X)^{-1} X^T y$$

minimizing $\|y - X\beta\|_2^2$.

**Gauss-Markov assumptions** (for OLS to be BLUE — Best Linear Unbiased Estimator):
1. **Linearity**: $y = X\beta + \epsilon$
2. **Strict exogeneity**: $E[\epsilon \mid X] = 0$
3. **No perfect multicollinearity**: $\text{rank}(X) = p$
4. **Homoscedasticity**: $\text{Var}(\epsilon \mid X) = \sigma^2 I$
5. (For inference) **Normality**: $\epsilon \sim N(0, \sigma^2 I)$

When (4) is violated (heteroscedasticity), OLS is still unbiased and consistent, but standard errors are wrong. Use **Huber-White (HC) robust standard errors**:

$$\text{Var}(\hat{\beta}) = (X^T X)^{-1} X^T \hat{\Sigma} X (X^T X)^{-1}$$

where $\hat{\Sigma} = \text{diag}(\hat{\epsilon}_i^2)$.

**Logistic regression**: For binary outcomes, models the log-odds:

$$\log\frac{P(Y=1 \mid X)}{P(Y=0 \mid X)} = X\beta$$

Coefficients are log-odds ratios: $\beta_j$ = change in log-odds for a 1-unit increase in $X_j$. $e^{\beta_j}$ = odds ratio.

**Regularization**:
- **Ridge** (L2): $\hat{\beta} = \arg\min \|y - X\beta\|_2^2 + \lambda \|\beta\|_2^2$. Closed form: $(X^TX + \lambda I)^{-1}X^Ty$. Shrinks coefficients; handles multicollinearity.
- **Lasso** (L1): $\hat{\beta} = \arg\min \|y - X\beta\|_2^2 + \lambda \|\beta\|_1$. Induces sparsity. No closed form; solved via coordinate descent.
- **ElasticNet**: Combines L1 and L2: $\lambda_1 \|\beta\|_1 + \lambda_2 \|\beta\|_2^2$. Groups correlated features (unlike Lasso, which picks one arbitrarily).

**Diagnostics**:
- **Residual plots**: Residuals vs fitted to check linearity and homoscedasticity.
- **VIF** (Variance Inflation Factor): $VIF_j = 1/(1 - R_j^2)$ where $R_j^2$ is from regressing $X_j$ on all other features. VIF > 10 signals multicollinearity.
- **Cook's distance**: Influence of each observation. Values > $4/n$ suggest influential outliers.

### Crux

**OLS is a workhorse, but know its failure modes:**
1. Omitted variable bias: If a confounder is correlated with both $X$ and $y$ but excluded from the model, $\hat{\beta}$ is biased.
2. Reverse causality: If $y$ causes $X$, OLS gives the wrong answer. Need IV or experimental data.
3. Non-linearity: OLS fits a hyperplane. If the true relationship is nonlinear, include interactions, polynomials, or use a nonparametric method.

For logistic regression: **the coefficients are NOT the marginal effects.** The marginal effect of $X_j$ on $P(Y=1)$ depends on the current level of all features (because of the nonlinear link function). Report odds ratios for relative effects or average marginal effects for absolute effects.

### Intuition

OLS draws the "best" straight line through a scatter plot, where "best" means minimizing the sum of squared vertical distances. Logistic regression draws the "best" S-curve through binary data. Regularization says: "I'd rather have a slightly worse fit to the training data if it means simpler, more generalizable coefficients."

### TikTok Use Case

**Predicting violation risk for content items**: Logistic regression with features (text embeddings, account age, posting frequency, historical violation count, language, region). The model outputs a risk score $P(\text{violation} \mid X)$ that feeds into the enforcement pipeline.

**Interpreting for stakeholders**: "Each additional prior violation increases the odds of a new violation by $e^{0.35} = 1.42\times$ (42% higher odds), holding all else constant. Accounts less than 7 days old have $e^{1.8} = 6.0\times$ higher odds of being spam."

**Heteroscedasticity in practice**: If modeling time-to-action on violations, the variance of enforcement time is higher for ambiguous content (borderline hate speech) than for clear-cut violations (CSAM). OLS standard errors are too small for ambiguous categories and too large for clear-cut ones. Use HC3 robust standard errors.

-> See `tiktok_integrity_safety.md` for logistic regression applied to violation probability modeling and metric decomposition via OLS regression trees.

### Python Code Snippet

```python
import numpy as np
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.metrics import roc_auc_score

np.random.seed(42)

# --- OLS with heteroscedasticity-robust standard errors ---
n = 500
account_age = np.random.exponential(180, n)       # days
post_freq = np.random.exponential(5, n)            # posts/day
prior_violations = np.random.poisson(2, n)

# True model: time_to_action depends on these features
# with heteroscedastic errors (more variance for newer accounts)
noise_scale = 5 + 20 * np.exp(-account_age / 30)  # higher noise for new accounts
time_to_action = 30 - 0.05 * account_age + 3 * post_freq + 5 * prior_violations \
                 + noise_scale * np.random.randn(n)
time_to_action = np.maximum(time_to_action, 1)

X = np.column_stack([account_age, post_freq, prior_violations])
X_with_const = sm.add_constant(X)

# OLS with standard vs robust SE
model_ols = sm.OLS(time_to_action, X_with_const).fit()
model_robust = sm.OLS(time_to_action, X_with_const).fit(cov_type='HC3')

print("=== OLS Regression: Time-to-Action ===")
names = ['const', 'account_age', 'post_freq', 'prior_violations']
print(f"{'Feature':<20s} | {'Coef':>8s} | {'SE (OLS)':>10s} | {'SE (HC3)':>10s} | {'Ratio':>6s}")
print("-" * 68)
for name, coef, se_ols, se_hc3 in zip(names, model_ols.params, model_ols.bse, model_robust.bse):
    print(f"{name:<20s} | {coef:>8.3f} | {se_ols:>10.3f} | {se_hc3:>10.3f} | {se_hc3/se_ols:>6.2f}")

# --- VIF for multicollinearity ---
from statsmodels.stats.outliers_influence import variance_inflation_factor

print("\nVariance Inflation Factors:")
for i, name in enumerate(names[1:], 1):
    vif = variance_inflation_factor(X_with_const, i)
    print(f"  {name}: VIF = {vif:.2f}")

# --- Logistic Regression with interpretation ---
n = 10000
X_log = np.column_stack([
    np.random.exponential(10, n),       # posts per day
    np.random.exponential(180, n),      # account age
    np.random.poisson(1.5, n),          # prior violations
    np.random.binomial(1, 0.3, n),      # is_new_account (< 7 days)
])

logits = (0.04 * X_log[:, 0] - 0.005 * X_log[:, 1]
          + 0.35 * X_log[:, 2] + 1.8 * X_log[:, 3] - 3.0)
p_viol = 1 / (1 + np.exp(-logits))
y = np.random.binomial(1, p_viol)

# Fit with statsmodels for SE and p-values
X_log_const = sm.add_constant(X_log)
logit_model = sm.Logit(y, X_log_const).fit(disp=0)

print("\n=== Logistic Regression: Violation Probability ===")
feat_names = ['const', 'posts_per_day', 'account_age', 'prior_violations', 'is_new_account']
print(f"{'Feature':<20s} | {'Coef':>8s} | {'SE':>8s} | {'OR':>8s} | {'p-value':>8s}")
print("-" * 62)
for name, coef, se, p in zip(feat_names, logit_model.params, logit_model.bse, logit_model.pvalues):
    print(f"{name:<20s} | {coef:>8.3f} | {se:>8.3f} | {np.exp(coef):>8.3f} | {p:>8.4f}")

auc = roc_auc_score(y, logit_model.predict(X_log_const))
print(f"\nAUROC: {auc:.4f}")

# --- Regularization comparison ---
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_log)

print("\n=== Regularization Comparison ===")
for name, model in [
    ("No penalty", LogisticRegression(penalty=None, max_iter=1000)),
    ("L2 (Ridge)", LogisticRegression(penalty='l2', C=1.0, max_iter=1000)),
    ("L1 (Lasso)", LogisticRegression(penalty='l1', C=1.0, solver='liblinear', max_iter=1000)),
    ("ElasticNet", LogisticRegression(penalty='elasticnet', C=1.0, l1_ratio=0.5,
                                       solver='saga', max_iter=5000)),
]:
    model.fit(X_scaled, y)
    coefs = model.coef_[0]
    n_nonzero = np.sum(np.abs(coefs) > 0.001)
    auc_score = roc_auc_score(y, model.predict_proba(X_scaled)[:, 1])
    print(f"  {name:<15s}: coefs={np.round(coefs, 3)}, nonzero={n_nonzero}, AUC={auc_score:.4f}")
```

---

## Quick Reference: Choosing the Right Test

| Scenario | Test | Key Assumption |
|---|---|---|
| Compare two proportions (large $n$) | Z-test for proportions | Independence, $np > 5$ |
| Compare two means (unknown $\sigma$) | Welch's t-test | Independence, approx. normality |
| Before/after on same units | Paired t-test | Paired observations, normal differences |
| Compare $k > 2$ group means | One-way ANOVA / Kruskal-Wallis | Independence, normality (ANOVA) |
| Complex statistic, no closed-form SE | Bootstrap | i.i.d. or paired structure |
| Rare event counts | Poisson test / exact binomial | Events are independent |
| Binary outcome prediction | Logistic regression | Independence, correct functional form |
| Updating beliefs with data | Bayesian posterior | Prior specification |

## Cross-Reference Map

| This Document | Related Content |
|---|---|
| Sec 1 (P-values, CIs) | `tiktok_integrity_safety.md` Sec 3: A/B Testing Framework |
| Sec 5 (Sample Size) | `tiktok_integrity_safety.md` Sec 3: Power Analysis for Rare Events |
| Sec 7 (Simpson's Paradox) | `tiktok_integrity_safety.md` Sec 3: Metric Decomposition |
| Sec 11 (Type I/II Errors) | `tiktok_integrity_safety.md` Sec 3: Error Cost Asymmetry |
| Sec 12 (Precision/Recall) | `tiktok_integrity_safety.md` Sec 3: Classifier Evaluation |
| Sec 14 (Bayesian) | `tiktok_integrity_safety.md` Sec 3: Sequential Testing |
| Sec 16 (Regression) | `tiktok_integrity_safety.md` Sec 3: Violation Risk Modeling |
| All sections (applied) | `applied_ds_tutorial.md` for dashboarding applications |

---

*Last updated: 2026-03-04*
