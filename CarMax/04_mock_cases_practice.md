# CarMax Sr. Data Scientist (Pricing Algorithms) — Mock Case Practice

## How to Use This Document

These five cases simulate the analytical problems you would face in a CarMax pricing
interview. Each case is designed to be solved in 15-20 minutes using mental math only.
Practice them out loud — narrate your thinking as if an interviewer were listening.

**Scoring yourself:**
- Did you ask clarifying questions before diving in?
- Did you structure your approach before calculating?
- Was your mental math correct (or close enough)?
- Did you give a clear recommendation with reasoning?
- Could you handle the follow-ups?

---

## Case 1: The Optimal Stopping Problem (Known CarMax Variant)

### Problem Statement

*"You're a CarMax buyer at a wholesale auction. There are 100 cars that will come across
the auction block one at a time, in random order. For each car, you can see its true
market value and must immediately decide: buy or pass. Once you pass on a car, you
cannot go back and buy it later. Your goal is to buy the single most valuable car out
of the 100. What strategy maximizes your probability of selecting the best car?"*

### Good Clarifying Questions to Ask

1. "Just to confirm — I must buy exactly one car, and my only goal is to maximize
   the probability that the one I buy is the absolute best of the 100?"
2. "Are the cars in a completely random order, or is there any pattern to the
   sequencing?"
3. "Do I know anything about the distribution of car values ahead of time, or am I
   learning purely from observation?"
4. "Is there a cost to waiting, or is the only cost the risk of missing the best car?"
5. "Can I assume that I can perfectly assess each car's value when I see it?"

*Why these matter:* The problem changes drastically if you can buy multiple cars, if
there is a known distribution, or if there is a time cost. Confirming the constraints
shows the interviewer you think before you calculate.

### Structured Approach

"This is a classic optimal stopping problem, sometimes called the secretary problem.
The core tension is: if I buy too early, I haven't seen enough cars to know what 'good'
looks like. If I wait too long, the best car may have already passed. I need a strategy
that balances exploration against exploitation."

**Framework:**
1. Define the observation phase (how many cars to watch without buying)
2. Define the action rule (what triggers a buy after the observation phase)
3. Calculate the probability of success
4. Verify with intuition

### Step-by-Step Solution

**Step 1: The Observation-Then-Act Strategy**

The mathematically optimal strategy is:

- **Phase 1 (Observe):** Watch the first *k* cars without buying any. Track the
  highest value you see.
- **Phase 2 (Act):** Starting with car *k+1*, buy the first car whose value exceeds
  the best value observed in Phase 1.
- If no car in Phase 2 beats the Phase 1 maximum, you are forced to buy the last car
  (car 100).

**Step 2: Finding the Optimal k**

The optimal *k* is n/e, where n = 100 and e ≈ 2.718.

Mental math:
- 100 / 2.718
- 100 / 2.72 (rounding for convenience)
- 2.72 x 36 = 97.92
- 2.72 x 37 = 100.64
- So k ≈ 37

**Observe the first 37 cars. Then buy the first car that beats all 37.**

**Step 3: Probability of Success**

The probability of selecting the best car with this strategy converges to 1/e.

- 1/e ≈ 1/2.718 ≈ 0.368
- **Roughly a 37% chance of picking the absolute best car**

To verify this is remarkable: if you picked randomly, your chance would be 1/100 = 1%.
This strategy gives you a 37x improvement.

**Step 4: Intuition Check**

Why does this work? The observation phase calibrates your sense of what "excellent"
looks like. By seeing 37% of the field, you have a strong baseline. The action rule
is aggressive — you grab the first thing that exceeds that baseline, which prevents
you from being too greedy and missing the best car.

The 37% observation window is optimal because:
- Too short (say 10 cars): you don't have a good baseline and may buy something
  mediocre thinking it is great.
- Too long (say 80 cars): your baseline is excellent, but you have already passed
  the best car with 80% probability.

### Recommendation

"My recommendation is the 37-then-act strategy. Observe the first 37 cars at auction
without bidding on any of them. Record the highest value you see. Then, starting with
car 38, immediately buy the first car whose value exceeds that maximum. This gives a
37% probability of getting the single best car — far better than any other strategy.
The key insight is that you must accept an exploration cost upfront to make a better
decision later."

### Possible Follow-ups

**Q: "What if you want to buy the top 3 cars instead of just 1?"**

A: The problem generalizes. You still observe roughly n/e cars, but now your action
rule changes — you are tracking the top 3 seen so far, and you buy whenever a car
would rank in your top 3. The observation window shrinks slightly because you have
more "slots" to fill, reducing the cost of an early mistake. The math is more complex,
but the intuition holds: observe first, then act decisively.

**Q: "What if there's a reserve price — you can't buy below $5,000?"**

A: The reserve price effectively reduces the pool of eligible cars. If roughly 20% of
cars are below the reserve, you are really choosing from ~80 cars, so your observation
window drops to about 80/e ≈ 29 cars. But those 29 include the cars below reserve that
you observe but would never buy anyway.

**Q: "How does this apply to CarMax's actual auction strategy?"**

A: CarMax buyers attend Manheim and ADESA auctions where hundreds of cars cross the
block in a day. They cannot pause the auction to re-evaluate earlier cars. While they
can buy multiple vehicles and have price models to guide them, the core tension is
identical: you must decide in real-time with imperfect information. The optimal stopping
framework teaches that gathering information before committing has measurable value —
and that there is an optimal amount of information gathering before it becomes
counterproductive.

**Q: "What if car values are not independent — say the best cars tend to come early
because dealers unload premium inventory first?"**

A: If there is a known ordering bias, the observation window should shrink. If the best
cars tend to appear in the first 30% of the auction, you need to start buying earlier
or you will miss them during your observation phase. This is where domain expertise and
historical auction data become essential — the theoretical model assumes random order,
but CarMax buyers should calibrate against actual auction sequencing patterns.

### Common Mistakes and Traps

- **Jumping to "just buy the first good car"** without defining what "good" means.
  The interviewer wants to see that you recognize the need for calibration.
- **Forgetting to state the probability.** Always quantify your result.
- **Not connecting to CarMax.** This is not a pure math exercise — relate it back to
  how CarMax actually operates at auctions.
- **Getting lost in the derivation of 1/e.** You do not need to prove the calculus.
  State the result, show the mental math, and explain the intuition.

---

## Case 2: Store Expansion Decision

### Problem Statement

*"CarMax is evaluating three cities for a new store. Here are the key metrics:*

| Metric | City A | City B | City C |
|--------|--------|--------|--------|
| Monthly unit sales (est.) | 300 | 450 | 180 |
| Gross profit per unit (GPPU) | $2,200 | $2,200 | $2,200 |
| Monthly operating expense | $400K | $600K | $300K |
| Land + build cost | $4M | $7M | $3M |
| Population | 500K | 800K | 300K |
| Avg household income | $65K | $55K | $80K |
| Existing competitors | 2 | 5 | 0 |

*Which city should CarMax expand into? Walk me through your analysis."*

### Good Clarifying Questions to Ask

1. "Are these monthly unit sales estimates based on CarMax's internal models, or are
   they market-level estimates that we would capture a share of?"
2. "Does the $400-600K operating expense include financing costs on the land
   investment, or is that separate?"
3. "Is there a corporate hurdle rate or payback period target I should use?"
4. "Are there strategic considerations beyond financial — for example, is there a
   geographic gap in CarMax's footprint that one of these cities fills?"
5. "Can I assume GPPU is constant across cities, or might the mix of vehicles differ?"

### Structured Approach

"I'll evaluate each city on four dimensions:

1. **Monthly profitability** — gross profit minus operating costs
2. **Payback period** — how long to recoup the land/build investment
3. **Return on investment** — annualized return on the upfront capital
4. **Qualitative factors** — competition, growth potential, strategic fit

Let me work through the numbers city by city."

### Step-by-Step Solution

**Step 1: Monthly Gross Profit**

Gross Profit = Units x GPPU

- City A: 300 x $2,200 = $660,000/month
- City B: 450 x $2,200 = $990,000/month
- City C: 180 x $2,200 = $396,000/month

Mental math check for City B: 450 x 2,200 = 450 x 2,000 + 450 x 200 = 900,000 +
90,000 = 990,000. Confirmed.

**Step 2: Monthly Net Profit**

Net Profit = Gross Profit - Operating Expense

- City A: $660K - $400K = **$260K/month**
- City B: $990K - $600K = **$390K/month**
- City C: $396K - $300K = **$96K/month**

City B has the highest absolute monthly profit. City A is solid. City C is thin.

**Step 3: Monthly Operating Margin**

Operating Margin = Net Profit / Gross Profit

- City A: $260K / $660K ≈ 39%
- City B: $390K / $990K ≈ 39%
- City C: $96K / $396K ≈ 24%

Interesting — A and B have similar margins. C is significantly lower, meaning more
of its gross profit is consumed by fixed costs.

**Step 4: Payback Period**

Payback = Land Cost / Monthly Net Profit

- City A: $4,000K / $260K ≈ 15.4 months ≈ **1.3 years**
- City B: $7,000K / $390K ≈ 17.9 months ≈ **1.5 years**
- City C: $3,000K / $96K ≈ 31.3 months ≈ **2.6 years**

Mental math for City A: $4,000 / $260 — $260 x 15 = $3,900, remainder $100,
$100/$260 ≈ 0.4, so 15.4 months. Confirmed.

Mental math for City B: $7,000 / $390 — $390 x 18 = $7,020, so just under 18 months.
Confirmed.

City A has the fastest payback, followed closely by B. City C takes over twice as long.

**Step 5: Annualized ROI**

Annual Net Profit / Upfront Investment

- City A: ($260K x 12) / $4,000K = $3,120K / $4,000K = **78%**
- City B: ($390K x 12) / $7,000K = $4,680K / $7,000K = **67%**
- City C: ($96K x 12) / $3,000K = $1,152K / $3,000K = **38%**

City A has the highest ROI. B is strong. C lags significantly.

**Step 6: Summary Table**

| Metric | City A | City B | City C |
|--------|--------|--------|--------|
| Monthly Net Profit | $260K | $390K | $96K |
| Operating Margin | 39% | 39% | 24% |
| Payback Period | 1.3 years | 1.5 years | 2.6 years |
| Annualized ROI | 78% | 67% | 38% |

**Step 7: Qualitative Assessment**

- **City A**: Mid-sized market, moderate competition (2 competitors), good income.
  Lower risk, very high returns. The 2 competitors suggest a proven market.
- **City B**: Largest market with the highest absolute profit, but 5 competitors
  means market share is fragmented. The $55K income is the lowest — customers may
  be more price-sensitive, compressing GPPU over time. Highest capital requirement.
- **City C**: No competition is a double-edged sword — it could mean an untapped
  market, or it could mean there is not enough demand to sustain a dealership.
  The small population (300K) and the thin $96K monthly profit leave little margin
  for error. However, the high household income ($80K) is attractive.

### Recommendation

"My recommendation is **City A**, with City B as a strong second option.

City A offers the best risk-adjusted return: 78% annualized ROI, a 1.3-year payback,
and a manageable $4M investment. The moderate competitive landscape (2 existing
dealers) validates that demand exists without oversaturating the market.

City B generates more absolute dollars ($390K/month vs $260K/month), so if CarMax is
optimizing for scale and market presence rather than capital efficiency, B is the pick.
But it requires nearly double the investment for only 50% more monthly profit.

City C is the weakest option on every quantitative metric. I would not recommend it
unless there is a compelling strategic reason — for example, if it fills a critical
gap in CarMax's logistics network or if there is strong evidence that the zero-
competition market is underserved rather than non-existent.

If CarMax has the capital and bandwidth, the best play might be to open both A and B.
Combined investment of $11M generating $650K/month in net profit — payback on the
combined investment in 17 months."

### Possible Follow-ups

**Q: "What if City B's volume estimate drops by 20% due to competition?"**

A: New volume = 450 x 0.8 = 360 units. New gross profit = 360 x $2,200 = $792K.
New net profit = $792K - $600K = $192K/month. Payback = $7,000K / $192K ≈ 36.5
months ≈ 3 years. ROI drops to ($192K x 12) / $7,000K = $2,304K / $7,000K ≈ 33%.
This makes B worse than C and far worse than A. Sensitivity to volume is a real risk
in a 5-competitor market.

**Q: "What other data would you want before making a final decision?"**

A: (1) Historical performance of CarMax stores in similar-sized markets with similar
competition. (2) Population growth trends — a fast-growing City C could look much
better in 3-5 years. (3) Specific site location and visibility/traffic counts.
(4) Regional vehicle mix — if City C skews toward trucks/SUVs with higher GPPU, the
$2,200 average may understate its potential. (5) Competitive intelligence — are the 5
competitors in City B all strong, or are some vulnerable?

**Q: "How would you model this more rigorously?"**

A: I would build a Monte Carlo simulation with distributions around unit sales, GPPU,
and operating costs for each city. Run 10,000 scenarios and compare the distribution
of 5-year NPV across cities. This captures the risk profile — City A likely has a
tighter distribution (lower variance) while City B has a wider range of outcomes.

### Common Mistakes and Traps

- **Only looking at absolute profit** and missing ROI/payback. City B "wins" on
  monthly profit but not on capital efficiency. The interviewer wants to see you
  consider multiple lenses.
- **Ignoring qualitative factors.** Pure math is not enough — CarMax cares about
  competitive dynamics, strategic positioning, and growth potential.
- **Not doing a sensitivity check.** Saying "City A generates $260K/month" as if
  that number is certain. Always acknowledge uncertainty and test key assumptions.

---

## Case 3: Auction Bidding Strategy

### Problem Statement

*"CarMax is bidding on a popular mid-size SUV at a wholesale auction. Here is what we
know from historical data:*

| Metric | Value |
|--------|-------|
| Average auction price | $18,000 |
| Average retail selling price | $24,500 |
| Average reconditioning cost | $1,200 |
| Holding cost | $50/day |
| Average days to sell | 30 days |

*Question 1: What is the expected profit on this vehicle at the average auction price?*

*Question 2: A competitor starts bidding aggressively. The price is now at $20,500.
Should you keep bidding?*

*Question 3: You learn that a supply shock has flooded the market — 30% more of this
model are available than usual. How does this change your bidding strategy?"*

### Good Clarifying Questions to Ask

1. "Is the $24,500 retail price based on current market conditions, or is it a
   trailing average that might be stale?"
2. "Does the $1,200 reconditioning cost include transportation from the auction
   to our facility?"
3. "What is CarMax's minimum acceptable margin per vehicle for this segment?"
4. "Is this a vehicle we have strong demand signals for — are customers searching
   for it on carmax.com?"
5. "How confident are we in the 30-day average time to sell? What is the standard
   deviation?"

### Structured Approach

"I'll build a unit-level P&L from auction purchase through retail sale, identify the
maximum bid price, then stress-test it under competitive pressure and supply shocks.
The key equation is:

**Net Profit = Retail Price - Auction Price - Reconditioning - Holding Cost**

Let me work through each scenario."

### Step-by-Step Solution

**Question 1: Expected Profit at Average Auction Price**

Starting with the basic unit economics:

- Retail price: $24,500
- Auction price: $18,000
- Reconditioning: $1,200
- Holding cost: $50/day x 30 days = $1,500

Net Profit = $24,500 - $18,000 - $1,200 - $1,500

Mental math:
- $24,500 - $18,000 = $6,500
- $6,500 - $1,200 = $5,300
- $5,300 - $1,500 = **$3,800**

Profit margin: $3,800 / $24,500 ≈ 15.5%

Mental math check: $3,800 / $24,500 — $24,500 x 0.15 = $3,675, $24,500 x 0.16 =
$3,920. So between 15% and 16%. Call it ~15.5%.

"At the average auction price of $18,000, this vehicle generates $3,800 in net profit,
which is a 15.5% margin. That is a healthy margin for a popular SUV."

**Question 2: Competitor Pushes Price to $20,500**

New unit economics:

- Retail price: $24,500
- Auction price: $20,500
- Reconditioning: $1,200
- Holding cost: $1,500

Net Profit = $24,500 - $20,500 - $1,200 - $1,500

Mental math:
- $24,500 - $20,500 = $4,000
- $4,000 - $1,200 = $2,800
- $2,800 - $1,500 = **$1,300**

Profit margin: $1,300 / $24,500 ≈ 5.3%

"At $20,500, the profit drops to $1,300, or about 5.3% margin. The question is whether
this meets CarMax's minimum threshold.

Here is how I would think about the decision:

**Arguments to keep bidding:**
- $1,300 is still positive profit
- If this is a high-demand vehicle with strong customer interest, the 30-day average
  might be conservative — it could sell in 15-20 days, saving $500-750 in holding costs
  and boosting profit to $1,800-$2,050
- Letting a competitor get this vehicle may mean losing the retail sale entirely

**Arguments to stop bidding:**
- $1,300 leaves almost no buffer for unexpected reconditioning costs or a slower sale
- If the car takes 45 days instead of 30, holding cost rises to $2,250, and profit
  drops to $550
- At $20,500, we are paying 84% of the retail price ($20,500 / $24,500) — that is tight
- CarMax's capital could earn more deployed on a different vehicle with better margins

My decision framework: I would stop bidding unless we have (a) strong demand signals
for this specific model in our local market and (b) limited alternative inventory to
deploy this capital on."

**Maximum Bid Calculation:**

Working backwards from a minimum acceptable margin:

If CarMax targets $2,000 minimum profit:
- Max bid = $24,500 - $1,200 - $1,500 - $2,000 = **$19,800**

If CarMax targets $1,000 minimum profit:
- Max bid = $24,500 - $1,200 - $1,500 - $1,000 = **$20,800**

"I would set my walk-away price at $19,800 for a standard vehicle, or up to $20,800
if we have specific customer demand and confidence in a faster-than-average sale."

**Question 3: Supply Shock — 30% More Inventory Available**

A 30% increase in supply with stable demand has two effects:

**Effect 1: Retail price compression.**
More supply pushes retail prices down. A reasonable estimate: if supply increases 30%,
prices might drop 8-12%. Using 10%:
- New retail price: $24,500 x 0.90 = **$22,050**

Mental math: $24,500 x 0.10 = $2,450, so $24,500 - $2,450 = $22,050.

**Effect 2: Days to sell increases.**
More options for buyers means longer decision cycles. If days to sell increases by 30%
(proportional to supply increase):
- New days to sell: 30 x 1.30 = **39 days**
- New holding cost: 39 x $50 = **$1,950**

**New unit economics at original auction price ($18,000):**

Net Profit = $22,050 - $18,000 - $1,200 - $1,950

Mental math:
- $22,050 - $18,000 = $4,050
- $4,050 - $1,200 = $2,850
- $2,850 - $1,950 = **$900**

"The supply shock crushes profitability from $3,800 to $900. My revised strategy:

1. **Lower the maximum bid.** At $900 profit from an $18,000 purchase, the margin is
   only 4%. I need to buy cheaper to maintain acceptable returns. Target auction price
   should drop to roughly $16,000-$17,000.
2. **Buy fewer units.** With margins compressed, each unit ties up capital less
   efficiently. Shift capital toward models that are not affected by the supply glut.
3. **Monitor the supply shock duration.** If this is temporary (a model-year
   transition, fleet liquidation), prices will recover. If structural (new competitor
   model launched), adjust the pricing model permanently.
4. **Accelerate existing inventory.** Any units already on the lot should be marked
   down proactively to sell before the full price impact hits retail."

### Possible Follow-ups

**Q: "How would you build a real-time model to set maximum bid prices at auction?"**

A: The model takes as inputs: (1) current market retail price for this specific
vehicle (year, make, model, trim, mileage), (2) estimated reconditioning cost based
on condition report, (3) predicted days to sell from our demand model, (4) current
inventory levels of this model at the target store, and (5) a target margin floor.
Maximum bid = predicted retail price - predicted recon - predicted holding cost -
target margin. Update daily using pricing feeds from Manheim Market Report and
CarMax's own sales data.

**Q: "What is the winner's curse and how does it apply here?"**

A: The winner's curse says that in a competitive auction, the winner tends to be the
bidder who most overestimates the item's value. If five dealers are bidding on this
SUV and we win, we should ask: did we win because we have better information, or
because we overestimated the retail price? CarMax mitigates this with superior data
(millions of transactions) and disciplined maximum bid rules. But the instinct to
"just win this one" is the exact emotional bias that the winner's curse exploits.

### Common Mistakes and Traps

- **Forgetting holding costs.** Many candidates calculate profit as retail minus
  auction minus recon and stop there. The $1,500 holding cost is real and material.
- **Treating the retail price as fixed.** The $24,500 is an average, not a guarantee.
  Acknowledge that retail price has a distribution around it.
- **Binary thinking on the $20,500 decision.** Don't just say "yes bid" or "no stop."
  Lay out the framework and conditions under which each answer is correct.
- **Ignoring the opportunity cost of capital.** The money spent on this vehicle at
  $20,500 cannot be spent on the next vehicle at the same auction that might have
  better margins.

---

## Case 4: Email Marketing Campaign Optimization

### Problem Statement

*"CarMax is planning a promotional email campaign. Here are our three customer segments:*

| Segment | Description | Size | Conv. Rate | Avg GPPU |
|---------|-------------|------|------------|----------|
| A | Recent browsers, no purchase | 50,000 | 3.0% | $2,000 |
| B | Purchased 2+ years ago | 100,000 | 1.5% | $2,500 |
| C | Service customers, never bought | 30,000 | 0.8% | $1,800 |

*Each email costs $0.50 to send (creative, platform, analytics). Total budget is $40,000.
How should we allocate the budget across segments? What is the expected ROI?"*

### Good Clarifying Questions to Ask

1. "Is the conversion rate defined as 'makes a purchase within 30 days of receiving
   the email,' or some other window?"
2. "Is GPPU the gross profit on the vehicle they buy, and does it vary by segment
   because different segments buy different vehicles?"
3. "Is there any risk of customer churn from over-emailing — could sending to segment
   C irritate service-only customers?"
4. "Are these conversion rates from past email campaigns specifically, or from any
   marketing touchpoint?"
5. "Can we A/B test within segments, or do we need to commit the full allocation
   upfront?"

### Structured Approach

"I'll calculate the expected value per email for each segment, rank them, then allocate
budget greedily — filling the highest-EV segment first, then the next, and so on. Then
I will calculate total expected profit and ROI for the campaign."

### Step-by-Step Solution

**Step 1: Expected Gross Profit per Email**

Expected GP per email = Conversion Rate x GPPU

- Segment A: 0.03 x $2,000 = **$60.00**
- Segment B: 0.015 x $2,500 = **$37.50**
- Segment C: 0.008 x $1,800 = **$14.40**

**Step 2: Expected Net Value per Email**

Net Value = Expected GP - Cost per Email

- Segment A: $60.00 - $0.50 = **$59.50**
- Segment B: $37.50 - $0.50 = **$37.00**
- Segment C: $14.40 - $0.50 = **$13.90**

All three segments are profitable to email. The priority ranking is A > B > C.

**Step 3: Budget Allocation**

Total budget: $40,000
Cost per email: $0.50
Maximum emails: $40,000 / $0.50 = **80,000 emails**

Greedy allocation (fill highest-EV first):

1. **Segment A**: Send to all 50,000 customers
   - Cost: 50,000 x $0.50 = $25,000
   - Remaining budget: $40,000 - $25,000 = $15,000

2. **Segment B**: Send to 30,000 of the 100,000 customers
   - Cost: 30,000 x $0.50 = $15,000
   - Remaining budget: $0

3. **Segment C**: No budget remaining — 0 emails sent

**Step 4: Expected Results**

Segment A (50,000 emails):
- Conversions: 50,000 x 0.03 = **1,500 sales**
- Gross profit: 1,500 x $2,000 = **$3,000,000**
- Cost: $25,000

Segment B (30,000 emails):
- Conversions: 30,000 x 0.015 = **450 sales**
- Gross profit: 450 x $2,500 = **$1,125,000**
- Cost: $15,000

**Total campaign results:**
- Total conversions: 1,500 + 450 = **1,950 sales**
- Total gross profit: $3,000,000 + $1,125,000 = **$4,125,000**
- Total cost: $40,000
- **Net profit: $4,085,000**
- **ROI: $4,085,000 / $40,000 = 10,213%**

Mental math check on ROI: $4,000,000 / $40,000 = 100x = 10,000%. Add the extra
$85K and you get roughly 10,200%. Confirmed.

**Step 5: Should We Request More Budget?**

The remaining 70,000 customers in Segment B have an EV of $37.00 per email:
- Cost to email all remaining: 70,000 x $0.50 = $35,000
- Expected GP: 70,000 x 0.015 x $2,500 = 1,050 x $2,500 = $2,625,000

And Segment C (30,000 customers):
- Cost: 30,000 x $0.50 = $15,000
- Expected GP: 30,000 x 0.008 x $1,800 = 240 x $1,800 = $432,000

Additional budget needed: $35,000 + $15,000 = $50,000
Additional expected GP: $2,625,000 + $432,000 = $3,057,000

"I would strongly recommend requesting an additional $50,000 in budget to cover all
three segments completely. The incremental $50K would generate over $3M in expected
gross profit — a 60x return. In fact, I would question why the budget is only $40,000
when every segment generates massive positive ROI."

### Recommendation

"Allocate the full $40,000 budget to Segment A first (50,000 emails, $25,000), then
Segment B (30,000 emails, $15,000). Expected outcome: 1,950 vehicle sales generating
$4.1M in gross profit on a $40K investment.

However, my stronger recommendation is to increase the budget. Every unfunded email
has a positive expected value. Leaving 70,000 Segment B customers and 30,000 Segment C
customers un-emailed means leaving approximately $3M in expected gross profit on the
table. The marginal ROI of the next dollar spent is enormous.

If forced to stay at $40K, I would also recommend selecting the 30,000 Segment B
recipients strategically — pick those with the highest predicted conversion probability
using CarMax's CRM data (recency of purchase, browsing history, geographic proximity
to a store) rather than randomly."

### Possible Follow-ups

**Q: "These conversion rates seem high. What if the true conversion rate is half of
what is estimated?"**

A: Let me recalculate at half rates:
- Segment A: 0.015 x $2,000 = $30.00 per email, net $29.50. Still hugely profitable.
- Segment B: 0.0075 x $2,500 = $18.75 per email, net $18.25. Still profitable.
- Segment C: 0.004 x $1,800 = $7.20 per email, net $6.70. Still profitable.

Even at half the estimated conversion rates, every segment has an ROI above 1,000%.
The strategy is robust to estimation error. This is because the email cost ($0.50) is
trivially small relative to the gross profit per conversion ($1,800-$2,500).

**Q: "How would you measure whether the email actually caused the purchase, versus
the customer was going to buy anyway?"**

A: This is the causal inference question. I would design a randomized holdout
experiment: within each segment, randomly withhold the email from 10% of customers.
Compare the purchase rate in the emailed group versus the holdout group. The difference
is the incremental lift attributable to the email. If Segment A has 3% conversion in
the emailed group but 2.5% in the holdout, the email's true incremental effect is only
0.5%, which dramatically changes the ROI calculation.

This is the single most important thing to get right. Without a holdout, you are
likely overstating the campaign's value by counting organic purchases as email-driven.

**Q: "What if there is email fatigue — sending to Segment B customers who were
already emailed last month?"**

A: I would check the email history for each customer and apply a frequency cap — no
more than one promotional email per 2-week period, for example. Over-emailing
increases unsubscribe rates and decreases conversion rates for future campaigns. The
$37 expected value per Segment B email assumes a customer who has not been recently
contacted. If they were emailed last week, the true EV is much lower.

### Common Mistakes and Traps

- **Splitting the budget equally across segments.** This is the naive approach and
  leaves money on the table. The interviewer wants to see you rank by marginal value.
- **Forgetting to subtract the email cost.** It is small ($0.50) but shows rigor.
- **Not questioning the conversion rates.** Acknowledging that these are estimates
  with uncertainty shows maturity.
- **Missing the holdout/incrementality point.** If you do not mention causal
  attribution, you are missing a key data science concept.
- **Ignoring that Segment C could be strategically valuable.** Even though it ranks
  last on EV, converting service customers into vehicle buyers could have a high
  lifetime value that is not captured in single-transaction GPPU.

---

## Case 5: Pricing Markdown Strategy

### Problem Statement

*"A vehicle has been on the lot for 45 days. Here is the situation:*

| Metric | Value |
|--------|-------|
| Current listed price | $22,000 |
| Current margin (at $22,000) | $3,000 |
| Holding cost | $50/day |
| Time on lot so far | 45 days |

*Historical sell-through rates for this vehicle type:*

| Period | Cumulative % Sold | Typical Markdown |
|--------|-------------------|------------------|
| Days 0-30 | 60% | 0% (full price) |
| Days 31-60 | 85% (25% incremental) | 5% |
| Days 61-90 | 95% (10% incremental) | 12% total |
| After 90 days | Remaining sent to wholesale | ~40% below original |

*Question 1: Should you markdown now or wait?*
*Question 2: How much should you markdown?*
*Question 3: At what price point is it better to wholesale than to continue retailing?"*

### Good Clarifying Questions to Ask

1. "When the data says '25% sell in days 31-60 after a 5% markdown,' does that mean
   25% of all vehicles, or 25% of the remaining 40% that did not sell in the first
   30 days?"
2. "Has this specific vehicle already received any markdown, or is it still at the
   original price?"
3. "Is the $3,000 margin calculated from our total cost basis (acquisition + recon +
   holding to date), or just from acquisition + recon?"
4. "What is the typical wholesale auction recovery for this vehicle type?"
5. "Do we have any customer interest signals — online views, test drives, offers?"

*Critical clarification:* I will assume the sell-through rates are cumulative (60% by
day 30, then 25% of the original 100 sell during days 31-60, etc.) and that this
vehicle has not yet been marked down.

### Structured Approach

"This is an expected value problem. I need to compare the expected profit from several
strategies:

- **Option A**: Hold at the current $22,000 price and wait
- **Option B**: Markdown 5% now
- **Option C**: Markdown 10% now
- **Option D**: Send to wholesale immediately

For each option, I need to calculate the expected profit considering the probability
of sale in each time window and the holding costs incurred.

The sunk cost of 45 days of holding ($2,250) is already spent. I should only consider
future costs and revenues from today forward."

### Step-by-Step Solution

**Establishing the Baseline**

First, let me figure out the current cost basis. If margin at $22,000 is $3,000:
- Total cost (acquisition + recon): $22,000 - $3,000 = $19,000
- Holding cost already incurred: 45 x $50 = $2,250 (sunk, ignore going forward)
- All-in cost basis including sunk holding: $19,000 + $2,250 = $21,250
- True remaining margin: $22,000 - $21,250 = $750

But for decision-making, I should focus on the margin excluding sunk costs: $3,000.
Sunk costs are irrelevant to the forward-looking decision.

**Key framing**: This vehicle is at day 45. Of the 40% of vehicles that do not sell
by day 30, we need to know what fraction sell in each subsequent window. Let me
reinterpret the data:

- 40 out of 100 vehicles remain unsold at day 30 (our vehicle is one of these)
- Of those 40, 25 sell during days 31-60 (with a 5% markdown)
- Of the remaining 15, 10 sell during days 61-90 (with a 12% total markdown)
- The final 5 go to wholesale

Conditional probabilities for our vehicle (unsold at day 45):
- We are in the days 31-60 window. Roughly half this window has passed.
- Assume the 25 sales in days 31-60 are uniformly distributed: about 12-13 sell in
  days 31-45, about 12-13 sell in days 46-60.
- So of the 40 unsold at day 30, about 12.5 have sold by day 45, leaving ~27.5.
- Conditional sell-through rates from day 45 forward:
  - Days 46-60 (next 15 days): ~12.5 of 27.5 ≈ **45% probability**
  - Days 61-90 (next 30 days after that): 10 of 27.5 ≈ **36% probability**
  - Wholesale: 5 of 27.5 ≈ **18% probability**

These sum to 99% (rounding) — close enough.

**Option A: Hold at $22,000 (No Markdown)**

Without a markdown, the sell-through rate is likely lower. The 25% that sell in days
31-60 are selling because of the 5% markdown. If we do not markdown, assume sell
probability drops by roughly half.

Scenario A outcomes:
- Sell in days 46-60 at $22,000 (probability ~22%, since no markdown cuts it roughly
  in half): Profit = $3,000 - (avg 8 more days x $50) = $3,000 - $400 = $2,600
- Sell in days 61-90 after eventual markdown of 12% (probability ~25%):
  Price = $22,000 x 0.88 = $19,360. Profit = $19,360 - $19,000 - (avg 30 more days
  x $50) = $360 - $1,500 = **-$1,140** (a loss!)
- Wholesale at day 90+ (probability ~53%): Price = $22,000 x 0.60 = $13,200.
  Profit = $13,200 - $19,000 - (45 more days x $50) = -$5,800 - $2,250 = **-$8,050**

Expected Profit for Option A:
= 0.22 x $2,600 + 0.25 x (-$1,140) + 0.53 x (-$8,050)

Mental math:
- 0.22 x $2,600 = $572
- 0.25 x (-$1,140) = -$285
- 0.53 x (-$8,050) = -$4,267

Total = $572 - $285 - $4,267 = **-$3,980**

Holding at $22,000 with no markdown has a deeply negative expected value because the
high probability of eventually wholesaling destroys value.

**Option B: Markdown 5% Now (Price = $20,900)**

New price: $22,000 x 0.95 = $20,900
New margin: $20,900 - $19,000 = $1,900

With the standard 5% markdown that drives the typical 31-60 day sales:
- Sell in days 46-60 (probability ~45%): Profit = $1,900 - (avg 8 days x $50)
  = $1,900 - $400 = $1,500
- Sell in days 61-90 with additional markdown to 12% total (probability ~36%):
  Price = $22,000 x 0.88 = $19,360. Profit = $19,360 - $19,000 - (avg 30 more
  days x $50) = $360 - $1,500 = -$1,140
- Wholesale (probability ~18%): $13,200 - $19,000 - (45 more days x $50)
  = -$5,800 - $2,250 = -$8,050

Expected Profit for Option B:
= 0.45 x $1,500 + 0.36 x (-$1,140) + 0.18 x (-$8,050)

Mental math:
- 0.45 x $1,500 = $675
- 0.36 x (-$1,140) = -$410
- 0.18 x (-$8,050) = -$1,449

Total = $675 - $410 - $1,449 = **-$1,184**

Still negative, but much better than holding.

**Option C: Markdown 10% Now (Price = $19,800)**

New price: $22,000 x 0.90 = $19,800
New margin: $19,800 - $19,000 = $800

A steeper markdown should accelerate the sale. Assume sell probability in days 46-60
increases to ~60% (the deeper discount attracts more buyers), days 61-90 drops to ~25%,
wholesale drops to ~15%.

- Sell in days 46-60 (probability ~60%): Profit = $800 - $400 = $400
- Sell in days 61-90 at 12% total markdown (probability ~25%): Price = $19,360,
  but we are already below this, so let us say we hold at $19,800.
  Profit = $800 - (30 more days x $50) = $800 - $1,500 = -$700
- Wholesale (probability ~15%): -$8,050 (same as before)

Expected Profit for Option C:
= 0.60 x $400 + 0.25 x (-$700) + 0.15 x (-$8,050)

Mental math:
- 0.60 x $400 = $240
- 0.25 x (-$700) = -$175
- 0.15 x (-$8,050) = -$1,208

Total = $240 - $175 - $1,208 = **-$1,143**

Roughly the same as Option B. The deeper discount increases sale probability but
reduces margin — the effects roughly offset.

**Option D: Wholesale Immediately**

Wholesale price: $22,000 x 0.60 = $13,200
Profit = $13,200 - $19,000 = **-$5,800**

No additional holding cost. Immediate certainty.

**Comparison Table:**

| Option | Expected Profit | Certainty |
|--------|-----------------|-----------|
| A: Hold at $22K | -$3,980 | Low (high wholesale risk) |
| B: Markdown 5% | -$1,184 | Moderate |
| C: Markdown 10% | -$1,143 | Moderate-High |
| D: Wholesale now | -$5,800 | Certain loss |

**Question 2 Answer: How Much to Markdown?**

"Options B and C are close in expected value. I would recommend the **5% markdown to
$20,900** because:

1. It preserves more margin if the car sells quickly ($1,500 profit vs $400)
2. It follows the standard pricing playbook that the historical data is based on,
   so our probability estimates are more reliable
3. We retain the option to do a further markdown at day 60 if needed
4. The EV difference between B and C is only $41 — not meaningful given our
   uncertainty in the probability estimates

The key insight is that **any markdown is vastly better than holding at the current
price.** Option A loses nearly $4,000 in expected value because it dramatically
increases the probability of wholesaling."

**Question 3: Wholesale Breakeven Price Point**

At what retail price is it better to wholesale immediately than to continue retailing?

The wholesale option gives a certain outcome of $13,200 in revenue (minus cost basis
of $19,000 = -$5,800 loss).

For continued retailing to be worse than -$5,800, the expected profit from retailing
must be below -$5,800. We showed that at a 5% markdown, expected profit is -$1,184.
Even at a 12% markdown, retailing is better than wholesaling.

Let me find the break-even differently. The question is really: **at what day does
wholesaling become optimal?**

At day 75 (15 days left before 90-day wholesale deadline):
- Remaining probability of retail sale: very low, maybe 15-20%
- Additional holding cost: 15 days x $50 = $750
- If we can sell retail at, say, $19,360 (12% markdown), profit = $360
- Expected value of continued retail: 0.20 x ($360 - average 8 more days holding)
  + 0.80 x (-$5,800 - $750) = 0.20 x $-40 + 0.80 x (-$6,550) = -$8 - $5,240
  = -$5,248
- Wholesale now: -$5,800

At day 75, continued retailing is still slightly better (-$5,248 vs -$5,800).

At day 85 (5 days left):
- Probability of retail sale: maybe 5%
- Additional holding cost: 5 x $50 = $250
- Expected retail: 0.05 x ($360 - $150) + 0.95 x (-$5,800 - $250)
  = 0.05 x $210 + 0.95 x (-$6,050) = $10.50 - $5,748 = -$5,737
- Wholesale now: -$5,800

Almost identical. The crossover is around day 82-85.

"My rule of thumb: **if a vehicle reaches day 80 without selling, send it to wholesale
immediately.** The additional holding costs and negligible sale probability do not
justify keeping it on the lot. But between days 45 and 75, aggressive markdown is
always preferable to wholesale."

### Recommendation

"For this specific vehicle at day 45:

1. **Mark down 5% today** to $20,900. This is the highest-EV decision.
2. **If unsold at day 60**, mark down to 12% total ($19,360). Reassess wholesale
   option at this point.
3. **If unsold at day 80**, route to wholesale immediately. Each additional day of
   holding costs $50 with minimal probability of retail sale.

The broader insight for CarMax's pricing algorithm: every day a vehicle sits unsold,
the optimal strategy shifts incrementally toward wholesale. The algorithm should
continuously calculate the expected value of 'markdown and hold' versus 'wholesale
now' and trigger the transition automatically when the curves cross."

### Possible Follow-ups

**Q: "How would you incorporate customer browsing data into this model?"**

A: If CarMax's website shows that 200 people viewed this vehicle in the last week,
that is a strong signal of demand — the probability of a near-term sale is higher
than the baseline, and we can afford to hold at a higher price. Conversely, if only
5 people viewed it, demand is weaker than baseline, and we should markdown more
aggressively. I would build a feature in the pricing model that uses page views,
saves, and test drive requests as real-time demand signals to dynamically adjust the
markdown schedule.

**Q: "This analysis assumed independent decisions. What if marking down this SUV
affects the perceived value of similar SUVs on the lot?"**

A: Excellent point. If CarMax has three similar SUVs on the lot and marks down one
aggressively, customers may anchor on the lower price and expect discounts on the
others. The pricing algorithm needs to consider inventory-level effects — the optimal
price for any one vehicle depends on what else is available. This is a multi-item
pricing problem, not a single-item decision.

**Q: "What data science techniques would you use to build the markdown model?"**

A: I would use a survival analysis framework. The target variable is time-to-sale, with
price and vehicle characteristics as covariates. A Cox proportional hazards model would
estimate how markdown size affects the hazard rate (probability of selling on any given
day). Combined with a cost model (holding costs + markdown losses), I can optimize the
markdown schedule that maximizes expected total profit. For the real-time component,
I would layer in a reinforcement learning approach where the agent learns the optimal
markdown policy from historical outcomes.

### Common Mistakes and Traps

- **Sunk cost fallacy.** Do not say "we have already spent $2,250 in holding costs
  so we need to hold out for a higher price to recoup it." Sunk costs are irrelevant.
  Only future costs and revenues matter.
- **Ignoring the time value of holding.** $50/day does not sound like much, but over
  45 days it is $2,250 — a significant portion of the original $3,000 margin.
- **Not using expected value.** Saying "we should hold because we could get $22,000"
  ignores the probability distribution. The expected value framework forces you to
  weight outcomes by their likelihood.
- **Treating wholesale as "giving up."** Wholesale is a legitimate exit strategy that
  eliminates future holding costs. Sometimes the optimal decision is to cut losses.

---

## General Tips for Case Interviews

### Managing Time in a 30-Minute Case

**First 3 minutes: Clarify and Structure**
- Ask 2-3 clarifying questions. Do not ask more than 4 — it starts to look like stalling.
- State your framework out loud: "I am going to approach this in three steps..."
- Write down the key numbers. You will refer back to them.

**Minutes 3-20: Calculate and Analyze**
- Talk through your math. The interviewer cannot give you credit for work they cannot see.
- Round aggressively for mental math. $24,500 becomes $25,000 unless precision matters.
- If you get stuck, state what you are trying to calculate and why. The interviewer may
  give hints.
- Check your answers for reasonableness. If you calculate that CarMax makes $50,000
  profit per car, something is wrong.

**Minutes 20-25: Synthesize and Recommend**
- Lead with the recommendation: "I recommend X because..."
- Support with 2-3 key numbers from your analysis.
- Acknowledge limitations and what additional data you would want.

**Minutes 25-30: Handle Follow-ups**
- The interviewer will probe your assumptions. Do not get defensive.
- If they change a number, recalculate quickly and see if it changes your recommendation.
- "That is a great point" is a fine thing to say while you think.

### When to Round vs. When to Be Precise

**Round aggressively when:**
- Comparing options where the difference is large (Case 2: City A vs City C)
- Doing back-of-envelope calculations to check feasibility
- The interviewer says "approximately" or "rough estimate"
- Intermediate calculations that feed into a comparison

**Be precise when:**
- The answer depends on a close comparison (Case 5: Option B vs Option C were $41 apart)
- Calculating break-even points or thresholds
- The interviewer specifically asks for a number
- Unit economics matter (GPPU, holding cost per day)

**Mental math shortcuts:**
- Multiply by 0.95 = subtract 5%. For $22,000: $22,000 - $1,100 = $20,900.
- Divide by 3 ≈ multiply by 0.333. For $7,000/3 ≈ $2,333.
- 1/e ≈ 0.37. Know this cold for optimal stopping problems.
- Rule of 72: to find doubling time, divide 72 by the growth rate. At 8% growth,
  doubles in 72/8 = 9 years.
- For percentages of large numbers: 1% of $22,000 = $220. Scale from there.

### How to Recover From a Math Error

**If you catch your own error:**
- "Wait, let me check that. I said $660K but 300 times $2,200 is... $660K. Actually,
  that is right." (Shows diligence even when correct.)
- "Actually, I made an error. Let me redo that. 450 times $2,200 is not $900K, it is
  $990K. Let me propagate that correction." (Fix it, move on, do not dwell.)

**If the interviewer catches your error:**
- "Thank you for catching that. Let me recalculate." (Gracious, fast.)
- Do NOT say "that does not change my answer" unless you have verified it does not.
- Recalculate the affected steps, state the corrected answer, and check whether your
  recommendation changes.

**Prevention:**
- Repeat key numbers aloud after calculating them: "So monthly gross profit for City B
  is $990,000."
- Do a sanity check: "That is about $1M per month in gross profit for a store selling
  450 cars at $2,200 GPPU. Does that make sense? Yes — 450 times roughly $2K is about
  $900K, so $990K checks out."

### Handling "What Else Would You Consider?"

This question tests whether you can think beyond the numbers. Have these frameworks
ready:

**For pricing problems:**
- Competitive dynamics (what are competitors pricing at?)
- Customer price sensitivity / elasticity
- Seasonality (SUVs sell differently in winter vs summer)
- Regional variation (prices differ by geography)
- Vehicle-specific factors (color, mileage, accident history, trim level)
- Online vs in-store customer behavior differences

**For business decisions:**
- Second-order effects (how does this decision affect other parts of the business?)
- Implementation risk (can we actually execute this strategy?)
- Customer experience impact (does this harm trust or brand perception?)
- Regulatory constraints (state-level pricing and disclosure laws)
- Data availability (can we actually measure what we need to measure?)
- Scalability (does this strategy work at 200 stores or just 1?)

**For marketing/campaign problems:**
- Long-term customer lifetime value (not just this transaction)
- Channel interaction effects (does email cannibalize other channels?)
- Attribution and incrementality (would they have bought anyway?)
- Customer experience and brand (are we annoying people?)
- Testing and learning (should we A/B test before scaling?)

**A strong closing statement for any case:**

"Beyond the quantitative analysis, I would want to validate these assumptions with
real data, run a small-scale test before full deployment, and build in monitoring to
catch cases where our model assumptions break down. The numbers give us a starting
point, but the real value comes from iterating quickly as we learn from outcomes."

---

## Quick Reference: Key Numbers to Have Ready

| Metric | Typical Value | Source |
|--------|---------------|--------|
| CarMax avg GPPU | $2,000-$2,500 | Public filings |
| CarMax units sold/store/month | 150-400 | Varies by store size |
| Avg days to sell | 30-40 days | Industry benchmark |
| Holding cost per day | $30-$60 | Interest + depreciation + lot cost |
| Wholesale discount | 30-45% below retail | Auction data |
| 1/e (optimal stopping) | 0.368 (≈37%) | Math constant |
| Email campaign cost | $0.25-$1.00 per send | Industry benchmark |
| Typical conversion rate (email) | 0.5-3% | Depends on segment warmth |
| CarMax annual revenue | ~$30B | Public filings |
| CarMax stores | ~250 | Public filings |

---

## Practice Schedule

| Day | Activity | Time |
|-----|----------|------|
| Day 1 | Read all 5 cases, understand the frameworks | 60 min |
| Day 2 | Solve Case 1 and Case 4 from memory (out loud) | 40 min |
| Day 3 | Solve Case 2 and Case 3 from memory (out loud) | 40 min |
| Day 4 | Solve Case 5 from memory, then attempt all follow-ups | 45 min |
| Day 5 | Full mock: have someone read you a case, solve cold | 30 min |
| Day 6 | Review mistakes, re-solve any case that gave trouble | 30 min |
| Day 7 | Final full mock with timer (20 min hard cap) | 20 min |

The goal is not to memorize solutions. The goal is to internalize the frameworks so
that when you see a new problem in the interview, you automatically: clarify, structure,
calculate, recommend, and extend.
