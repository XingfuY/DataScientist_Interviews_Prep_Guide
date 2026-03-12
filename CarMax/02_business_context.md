# CarMax Business Context Deep Dive

## Sr. Data Scientist — Pricing Algorithms

**Purpose**: Morning-of reference for the 10am interview. Every section gives you specific numbers, strategic context, and language you can drop into case study conversations to demonstrate that you have done your homework on the business. Memorize the quick reference table at the end. Read everything else at least once so it is primed in memory.

**Last updated**: March 2026

---

## 1. CARMAX BUSINESS MODEL

### Company Overview

CarMax, Inc. (NYSE: KMX) was founded in 1993 as a subsidiary of Circuit City and spun off as an independent company in 2002. Headquartered in Richmond, Virginia, it is the largest used-car retailer in the United States by volume and revenue. The company was founded on a radical idea for the automotive industry: transparent, no-haggle pricing. At a time when buying a used car meant adversarial negotiations with salespeople working on commission, CarMax offered posted prices, salaried sales consultants, and a 30-day warranty. That positioning remains its core brand differentiator more than three decades later.

### Revenue Streams

CarMax generates revenue through four primary channels:

1. **Retail Used Vehicles**: The core business. CarMax buys, reconditions, prices, and sells used vehicles directly to consumers. This accounts for the vast majority of top-line revenue — approximately $20-21B of the $26.4B total in FY2025.

2. **Wholesale Vehicles**: Vehicles that do not meet CarMax's retail standards (too old, too high mileage, too expensive to recondition) are sold at CarMax-operated wholesale auctions to licensed dealers. CarMax Auctions operates 59 auction locations across the United States and was named the 2025 Auction Group of the Year by Auto Remarketing. In FY2025, CarMax sold approximately 540,000 wholesale units, making it one of the largest wholesale auction operators in the country (second only to Manheim in overall scale). These auctions transitioned to an entirely digital/online format after 25 years of physical sales.

3. **CarMax Auto Finance (CAF)**: CarMax's captive lending arm originates auto loans for CarMax customers. CAF originated more than $8 billion in receivables during FY2025, adding to a portfolio of nearly $18 billion. CAF income is a significant and growing profit center — Q4 FY2025 CAF income was $159.3 million, up 8.2% year-over-year. CAF penetration (the percentage of CarMax buyers who finance through CAF) was approximately 42% in recent quarters, with a strategic target of increasing to 50%. The rest of CarMax's customers finance through third-party lenders that CarMax partners with, or pay cash.

4. **Extended Service Plans (MaxCare)**: CarMax sells extended protection plans on vehicles, generating recurring fee income. While smaller than the other revenue streams, MaxCare generates high-margin revenue and increases customer lifetime value.

### Scale of Operations

- **250+ store locations** across the United States (as of Q3 FY2026, with two new stores opened in Tulalip, WA and Rogers, AR during that quarter)
- **~30,000+ associates** (CarMax calls all employees "associates")
- **~790,000 retail used vehicles sold** in FY2025
- **~540,000 wholesale vehicles sold** in FY2025
- **Total net revenues of $26.35 billion** in FY2025
- **~3.7% share** of the nationwide age 0-10 year old used vehicle market in calendar year 2024

### The No-Haggle Pricing Model

This is the most important thing to understand about CarMax for a pricing algorithms interview. CarMax does not negotiate. The price on the windshield is the price. This means:

- **Every price must be right the first time.** There is no salesperson adjusting in real time based on customer pushback.
- **Pricing algorithms bear enormous responsibility.** A traditional dealership can absorb a bad price by negotiating down. CarMax cannot. If the algorithm overprices a vehicle, it sits on the lot and accumulates holding costs. If it underprices, the margin evaporates.
- **Trust is the product.** Customers come to CarMax specifically because they trust the no-haggle price is fair. The algorithm must produce prices that are competitive enough to generate sales velocity while maintaining margin.
- **The pricing algorithm IS the sales strategy.** At a traditional dealership, pricing is one input into the negotiation process. At CarMax, pricing IS the process.

### The Omnichannel Model

CarMax has invested heavily in blending online and in-store experiences:

- **Digital capabilities support over 80% of sales** — meaning customers use online tools (browsing inventory, comparing vehicles, prequalifying for financing, scheduling test drives) for the majority of transactions, even if they ultimately purchase in-store.
- **Omnichannel sales (mixing online and in-store steps) account for approximately 58-67% of retail unit sales**, depending on how broadly "omnichannel" is defined. Using the narrower definition (customer completes at least one step online and one step in store), it was 58% in Q4 FY2025, up from 55% a year earlier.
- **Fully online sales account for approximately 14-15% of retail unit sales.** These customers complete the entire transaction — selection, financing, and purchase — without visiting a store.
- CarMax offers **home delivery** and **in-store pickup** for online purchases.
- The **Instant Offer** tool allows consumers to get an offer on their current vehicle online in under two minutes, valid for seven days. This is powered by AI/ML pricing models and is a critical acquisition channel.
- CarMax launched a **ChatGPT App Store integration** in February 2026, becoming the first U.S. auto retailer to offer car shopping and selling within the ChatGPT ecosystem. This signals serious commitment to AI-powered customer experiences.
- The virtual assistant **Skye** manages tens of thousands of customer conversations per week on the CarMax website, guiding shoppers through vehicle comparison, financing, and inventory search.

### How CarMax Sources Inventory

CarMax acquires vehicles from three primary channels:

1. **Consumer purchases and trade-ins**: Consumers sell or trade in vehicles to CarMax, either in-store or through the Instant Offer tool. This is the highest-quality acquisition channel because CarMax controls the appraisal and can inspect the vehicle firsthand.
2. **Wholesale auctions**: CarMax buys vehicles at dealer auctions (Manheim, ADESA, etc.) to supplement inventory. Auction purchases carry more risk because inspection is limited.
3. **Dealer-to-dealer**: CarMax acquires vehicles from other dealers, including franchise dealers offloading older trade-ins.

The acquisition cost is the starting point for the pricing algorithm. Getting the acquisition price right is just as important as getting the retail price right — if CarMax overpays for a vehicle, the retail price must be higher to maintain margin, which reduces sales velocity.

---

## 2. KEY FINANCIAL METRICS

### FY2025 Annual Results (Fiscal Year Ended February 28, 2025)

| Metric | Value |
|--------|-------|
| Total net revenues | $26.35 billion |
| Year-over-year revenue change | -0.7% (essentially flat) |
| Retail used vehicles sold | ~790,000 units |
| Wholesale vehicles sold | ~540,000 units |
| Total vehicles sold | ~1.33 million units |
| CAF receivables originated | $8+ billion |
| CAF managed receivables portfolio | ~$18 billion |

### Unit Economics (Q4 FY2025)

| Metric | Value | YoY Change |
|--------|-------|------------|
| Retail gross profit per unit (GPPU) | $2,322 | +$71/unit |
| Wholesale gross profit per unit | $1,045 | (relatively stable) |
| Average retail selling price | ~$26,130 | Down from ~$29,310 in early 2022 |
| Total gross profit (Q4) | $667.9M | +13.9% |
| CAF income (Q4) | $159.3M | +8.2% |
| Net earnings per diluted share (Q4) | $0.58 | +81.3% |

### Profitability Structure

Understanding the profitability waterfall is essential for a pricing algorithms interview:

1. **Revenue per vehicle**: Average retail selling price ~$26,000
2. **Less: Vehicle acquisition cost**: What CarMax paid for the vehicle (auction price, consumer offer, or trade-in value)
3. **Less: Reconditioning cost**: Average ~$1,000-1,500 per vehicle (CarMax spends 12+ hours of inspection and reconditioning per vehicle through a rigorous 125+ point inspection)
4. **Less: Transportation/logistics**: Cost of moving vehicle from acquisition point to the selling store
5. **Equals: Retail gross profit per unit**: ~$2,322 (Q4 FY2025)

At a retail GPPU of ~$2,322 on an average selling price of ~$26,000, the gross margin is approximately 8.9%. This is a thin-margin, high-volume business. Every $100 improvement in GPPU across 790,000 retail units equals $79 million in incremental gross profit. This is why the pricing algorithm matters so much.

### SG&A and Cost Efficiency

- Q4 FY2025 SG&A was $610.5 million, up 5.1% YoY
- SG&A as a percent of gross profit was a key management focus — it decreased from 84.1% to 80.3% in recent quarters due to cost management
- CEO (at the time) Bill Nash announced a target of **at least $150 million in incremental SG&A reductions** over an 18-month period starting from mid-2025
- This cost reduction program signals that CarMax is serious about operational efficiency, which creates demand for ML-driven automation and optimization — including in pricing

### Inventory Metrics

| Metric | Value |
|--------|-------|
| Inventory turnover ratio | ~1.57-1.76 (varies by quarter) |
| Days inventory (days on lot) | ~52 days |

Days on lot is one of the most critical metrics for the pricing team. Every day a vehicle sits unsold costs CarMax in:
- **Depreciation**: The vehicle loses value every day, especially in a declining market
- **Financing cost**: CarMax finances its inventory through floor-plan credit facilities; interest accrues daily
- **Opportunity cost**: The lot space occupied by a slow-selling vehicle could be occupied by a faster-turning vehicle
- **Reconditioning decay**: A reconditioned vehicle gradually needs re-inspection if it sits too long

### FY2026 Quarterly Trends (Year in Progress)

| Quarter | Retail Used Unit Sales | Wholesale Units | Notable |
|---------|----------------------|-----------------|---------|
| Q1 FY2026 | +9.0% YoY | — | Strong rebound; EPS $1.38, up 42.3% |
| Q2 FY2026 | -5.4% YoY | -2.2% | SG&A decreased 1.6% to $601.1M |
| Q3 FY2026 | -8.0% YoY | -6.2% | CEO transition; two new stores opened |

The declining trend in Q2-Q3 FY2026 is important context: the used car market faced headwinds from high interest rates, affordability pressure, and macro uncertainty. This is exactly the environment where pricing algorithms become even more critical — when demand is soft, the margin for pricing error shrinks.

---

## 3. THE PRICING ALGORITHMS TEAM — WHAT THEY ACTUALLY DO

### The Problem

CarMax must price approximately 790,000 unique used vehicles per year for retail sale, plus determine acquisition offers for vehicles consumers want to sell, plus set reserve prices for 540,000 wholesale units. Unlike pricing a commodity (every barrel of oil is identical), every used vehicle is different:

- **Year, make, model, trim**: A 2021 Honda Accord LX is fundamentally different from a 2021 Honda Accord Touring
- **Mileage**: A 20,000-mile vehicle commands a premium over a 60,000-mile identical vehicle
- **Condition**: Interior wear, exterior damage, mechanical issues, tire condition
- **Features**: Sunroof, leather seats, navigation, advanced safety features
- **Color**: Some colors command premiums (white, black, silver are most liquid); unusual colors can suppress demand
- **Geography**: A pickup truck commands different prices in Texas versus Manhattan; a convertible prices differently in Florida versus Minnesota
- **Market timing**: Used car prices fluctuate with new car production, interest rates, seasonality, and consumer confidence
- **Vehicle history**: Accident history, number of previous owners, service records

### The Scale

The pricing team generates recommendations at massive scale. CarMax has referenced its systems producing millions of pricing signals daily across:

- **Retail pricing**: What should this specific vehicle sell for at this specific store?
- **Instant Offer pricing**: What should we offer a consumer for their vehicle?
- **Wholesale reserve pricing**: What is the minimum acceptable price at auction?
- **Transfer pricing**: Should this vehicle be transferred to a different market where it will sell faster or for more?
- **Markdown pricing**: Should we reduce the price on a vehicle that has been on the lot too long? By how much?

### Variables the Models Must Consider

The pricing algorithm ingests signals from multiple domains:

1. **Acquisition cost**: What CarMax paid for the vehicle (the floor below which any price yields a loss)
2. **Reconditioning cost**: Estimated repair and detailing costs (may be predicted before reconditioning is complete)
3. **Market demand signals**: Comparable vehicle sales (CarMax's own + market-wide), search volume on carmax.com, lead-to-sale conversion rates
4. **Competitor pricing**: What other dealers and online platforms are asking for similar vehicles
5. **Days-on-lot curves**: How quickly similar vehicles have historically sold at various price points
6. **Geographic demand**: Regional preferences (trucks in the South, AWD vehicles in the Northeast, fuel-efficient cars in urban markets)
7. **Seasonality**: Convertibles sell better in spring/summer, SUVs and 4WDs sell better before winter, tax refund season (February-April) drives volume
8. **Macro factors**: Interest rates (affect monthly payments and affordability), gas prices (affect demand for SUVs vs. sedans), new car availability (tight new car supply pushes buyers to used)
9. **Vehicle-specific attributes**: Make, model, trim, year, mileage, condition, features, color, accident history
10. **Inventory position**: How many similar vehicles are in stock at this store and nearby stores (avoid self-cannibalization)

### Modeling Challenges

This is what makes the role technically interesting:

- **Heterogeneity**: Every vehicle is unique. Traditional pricing models (e.g., for airline seats or hotel rooms) price a finite set of products. CarMax prices an effectively infinite product space.
- **Sparse data**: For common vehicles (Civic, Camry, F-150), there is abundant transaction data. For rare vehicles (a specific year/trim/color combination of a low-volume model), the data is extremely thin. The model must generalize from similar vehicles.
- **Market regime shifts**: The COVID-era used car bubble demonstrated that historical pricing relationships can break down rapidly. Manheim Used Vehicle Value Index spiked ~50% in 2021-2022, then corrected. Models trained on pre-COVID data would have massively underpriced vehicles during the run-up and overpriced during the correction.
- **Feature interaction effects**: The value of a sunroof depends on the vehicle segment (luxury buyers expect it; economy buyers may not care). The value of low mileage depends on the vehicle's age (low mileage on a 1-year-old car is expected; low mileage on a 10-year-old car signals it sat unused). The models must capture complex non-linear feature interactions.
- **Time sensitivity**: A price set today for a vehicle that arrives at the store in 5 days must anticipate market conditions at the time of sale, not at the time of pricing.
- **Multi-objective optimization**: The algorithm must balance margin (price high) against turn speed (price low). This is not a single objective — it is a Pareto frontier, and the business decides where on that frontier to operate based on strategic priorities.

### Tech Stack

Based on job postings and public information, the CarMax data science organization uses:

- **Cloud**: Microsoft Azure
- **Data Platform**: Databricks (Azure Databricks)
- **Compute**: Apache Spark for distributed data processing
- **ML Experimentation**: MLflow for experiment tracking, model versioning, and model registry
- **ML Frameworks**: TensorFlow for deep learning use cases; likely scikit-learn and XGBoost/LightGBM for tabular pricing models (industry standard for heterogeneous tabular data)
- **Languages**: Python (primary for model development), SQL (data manipulation, feature engineering)
- **Data Storage**: Azure Data Lake Storage, Azure Data Factory for ETL pipelines, Azure Data Catalog for data discovery
- **Production**: Batch and real-time scoring pipelines
- **Experimentation**: A/B testing infrastructure for pricing experiments in production

### What "Sr. Data Scientist — Pricing Algorithms" Actually Means

From the job posting, the role involves:

- Developing and implementing innovative algorithms to optimize pricing strategies for CarMax products and services
- Utilizing advanced statistical and machine learning techniques to analyze large datasets and provide data-driven insights
- Collaborating with cross-functional teams including business stakeholders to identify pricing opportunities
- Using a strategic mindset to identify key business challenges and propose data-driven solutions
- Leading and mentoring junior data scientists
- Communicating complex data science concepts to non-technical stakeholders
- Presenting insights and recommendations to senior leaders to drive change
- Researching innovations and best practices related to data sources, modeling methodologies, and tools
- Influencing the team in developing the modeling capability strategic roadmap

Required qualifications include 3+ years of experience in e-commerce, marketplace, or data-rich environments, strong Python and SQL skills, a solid statistics foundation, and experience with tools like Spark and Databricks.

---

## 4. HOW CARMAX MAKES MONEY ON EACH VEHICLE

### The Unit Economics Waterfall

Walk through this on a whiteboard if asked. This is the anatomy of a single transaction:

```
Step 1: ACQUIRE THE VEHICLE
  ├── Consumer offer (via Instant Offer or in-store appraisal)
  ├── Auction purchase (Manheim, ADESA, other wholesale auctions)
  └── Dealer trade or purchase

  Example: CarMax acquires a 2021 Toyota Camry SE for $20,000

Step 2: INSPECT & RECONDITION
  ├── 125+ point inspection (CarMax proprietary checklist)
  ├── Mechanical repairs, cosmetic detailing, safety items
  ├── Average 12+ hours of labor per vehicle
  ├── Average reconditioning cost: ~$1,000-1,500
  └── Decision gate: Does this vehicle meet retail standards?
        ├── YES → Route to retail inventory
        └── NO → Route to wholesale auction

  Example: Reconditioning costs $1,200 on the Camry
  Running cost basis: $21,200

Step 3: PRICE FOR RETAIL (or WHOLESALE)
  ├── Pricing algorithm generates recommended price
  ├── Considers: acquisition cost, recon cost, market comps,
  │   competitor pricing, geographic demand, seasonality, days-on-lot targets
  ├── Price is posted — no negotiation
  └── May be marked down over time if vehicle does not sell within target window

  Example: Algorithm prices the Camry at $24,500
  Expected gross profit: $24,500 - $21,200 = $3,300

Step 4: SELL TO CUSTOMER
  ├── In-store (customer visits, test drives, purchases same day)
  ├── Online with in-store pickup
  ├── Online with home delivery
  └── Customer may also trade in their current vehicle (feeds Step 1)

  Example: Camry sells at $24,500 after 35 days on lot
  Actual gross profit before holding costs: $3,300

Step 5: ANCILLARY REVENUE (the real margin expansion)
  ├── CarMax Auto Finance (CAF): If customer finances through CAF,
  │   CarMax earns interest income over the life of the loan
  │   CAF penetration: ~42%, target ~50%
  ├── MaxCare (extended service plan): High-margin product
  ├── GAP insurance and other F&I products
  └── These add $500-1,500+ in lifetime value per transaction

  Example: Customer finances $22,000 at 7.5% APR for 60 months through CAF
  CarMax earns ~$4,500 in interest income over the loan term
  Customer also buys MaxCare for $1,800
```

### Where the Pricing Algorithm Directly Impacts

The pricing algorithm touches Steps 1, 3, and 4 directly:

**Step 1 — Acquisition pricing (Instant Offer)**:
- If the offer is too low, the consumer walks and CarMax loses the inventory
- If the offer is too high, CarMax overpays and must either eat the margin loss or overprice at retail
- The Instant Offer algorithm must predict what the vehicle will sell for at retail (or wholesale), subtract target margin and reconditioning cost, and produce an offer that wins the vehicle at the right price

**Step 3 — Retail pricing**:
- Price too high: Vehicle sits on the lot. Days on lot increase. Holding costs accumulate (depreciation, floor plan interest, opportunity cost). Eventually requires markdown, which compresses margin further.
- Price too low: Vehicle sells quickly but leaves money on the table. Gross profit per unit suffers. At 790,000 retail units, even $50 of unnecessary underpricing = $39.5 million in lost gross profit annually.
- The algorithm must find the price that maximizes expected total gross profit, balancing per-unit margin against turn speed.

**Step 4 — Markdown/repricing**:
- As a vehicle ages on the lot, the algorithm must decide when and how much to reduce the price
- Too aggressive markdown: Trains customers to wait for discounts, destroys margin
- Too slow markdown: Vehicle continues to depreciate, holding costs mount
- The optimal markdown curve is a dynamic programming problem: at each time step, the expected marginal benefit of a price reduction (higher probability of sale) must exceed the marginal cost (lower per-unit margin)

### The Margin Sensitivity

Let this sink in: retail GPPU is approximately $2,322. On an average selling price of ~$26,000, that is an ~8.9% gross margin. After SG&A allocation, the operating margin is even thinner. This means:

- A **1% pricing error** on a $26,000 vehicle = $260 per vehicle. Across 790,000 units = **$205 million** in potential impact.
- A **$100 improvement in GPPU** across the full volume = **$79 million** in incremental gross profit.
- **Reducing average days on lot by 5 days** (from 52 to 47) would reduce holding costs and depreciation exposure significantly, potentially worth tens of millions annually.

This is why the pricing algorithms team exists. The return on investment for even marginal pricing accuracy improvements is enormous.

---

## 5. COMPETITIVE LANDSCAPE

### Direct Competitors

**Carvana (CVNA)**
- The most visible competitor. Online-first, known for car vending machines.
- Experienced a near-death experience in 2022 (stock dropped from $370 to $3.55, debt restructuring, massive layoffs) followed by one of the most dramatic corporate turnarounds in recent history.
- By late 2025, Carvana had recovered to ~$472/share, was added to the S&P 500 in December 2025, and posted record profitability.
- Business model: Online purchase with home delivery. No-haggle pricing. No physical stores for browsing (just vending machines and inspection centers).
- Key difference from CarMax: Carvana is pure-play digital. CarMax is omnichannel (stores + online). CarMax has 250+ stores with test drive capability; Carvana does not offer traditional test drives.
- Pricing strategy: Carvana's pricing tends to fall mid-range. Their data infrastructure is different — more focused on online conversion optimization.
- Competitive threat: High. Carvana has proven the all-online model works and is scaling profitably.

**Vroom (VRM)**
- Struggled significantly after going public. Largely exited the retail used car market.
- Had undercut competitors by $1,000-2,000 on comparable vehicles, but the unit economics never worked.
- Not a material competitive threat going forward, but a cautionary tale about aggressive pricing without the margin structure to support it.

**AutoNation (AN)**
- Largest franchise dealer group in the U.S.
- Strong used vehicle operations, but used cars are secondary to their franchise new car business.
- Different model: they have manufacturer franchise relationships that CarMax does not.

**Lithia Motors / Driveway (LAD)**
- Large franchise dealer group with growing digital platform (Driveway).
- Aggressive acquirer of dealerships. Expanding used car footprint.
- Driveway is their online brand, competing with Carvana and CarMax's digital experience.

**Penske Automotive Group (PAG)**
- Large franchise dealer group with used car operations.
- More focused on luxury/premium segments.

**Private Dealers (Fragmented)**
- There are ~40,000+ franchised dealers and ~60,000+ independent used car dealers in the U.S.
- Most are small, fragmented, and do not have sophisticated pricing technology.
- Their pricing model: subjective, experience-based, often negotiable. The opposite of CarMax.
- CarMax's advantage against this segment: **trust and transparency**. Consumers increasingly prefer the no-haggle model.

### CarMax's Competitive Moat

1. **Scale**: 250+ stores, 790K retail units, $26B revenue. The largest transaction dataset in the industry. More data = better pricing models.
2. **Trust and brand**: No-haggle pricing is a consumer trust signal. The CarMax brand means "fair price, no games."
3. **Omnichannel infrastructure**: Unlike Carvana (online only) or traditional dealers (in-store only), CarMax lets customers seamlessly blend channels. 67% of sales mix online and in-store steps.
4. **Wholesale auction operations**: 59 auction locations create a built-in disposal channel for vehicles that do not meet retail standards, reducing inventory risk.
5. **Data infrastructure**: 30+ years of transaction data across all vehicle types, all geographies, all market conditions. This is the moat that matters most for the pricing algorithms team. No competitor has a richer proprietary pricing dataset.
6. **CarMax Auto Finance**: Captive lending allows CarMax to capture the full customer lifetime value (vehicle margin + interest income + ancillary products). Carvana has its own lending arm too, but CarMax's $18B portfolio is mature and well-understood.
7. **Reconditioning capabilities**: In-house reconditioning with standardized processes reduces dependence on third parties and improves quality control.

---

## 6. FY2025-2026 STRATEGIC PRIORITIES

### Leadership Transition

Bill Nash, who had been CEO since 2016, stepped down effective December 1, 2025. David McCreight (a board member) was named Interim President and CEO, and Tom Folliard (former CEO) was appointed Interim Executive Chair. This leadership change occurred during a period of declining same-store sales (Q2 and Q3 FY2026). The permanent CEO search was underway as of Q3 FY2026.

For the interview, this means:
- The incoming leadership will be looking for quick wins and measurable impact
- Cost efficiency and pricing optimization are top priorities
- The pricing algorithms team is positioned to deliver direct revenue impact — exactly what new leadership wants to see

### $150M+ SG&A Reduction Program

Announced in the Q2 FY2026 earnings call, this is one of the most important strategic initiatives:
- Target: At least $150 million in incremental SG&A reductions over 18 months
- This signals investment in automation, ML-driven efficiency, and optimization
- Pricing algorithm improvements directly support this: better pricing reduces days on lot (lower holding costs), reduces markdowns (preserves margin), and improves inventory turn (lower floor plan interest)
- SG&A as a percent of gross profit improved from 84.1% to 80.3% in recent quarters, showing that cost management efforts are working

### Omnichannel Experience Refinement

- Goal: Make the online-to-in-store transition seamless
- 81% of retail sales are already supported by digital capabilities
- Strategic target: increase fully online sales from ~15% to a higher percentage
- Launched ChatGPT App Store integration in February 2026 — first U.S. auto retailer to do so
- Virtual assistant Skye handles tens of thousands of conversations weekly
- This creates rich behavioral data (browse patterns, search queries, financing prequalification, offer interactions) that feeds the pricing models

### EV Readiness

This is a major challenge and opportunity for the pricing team:
- Average used EV prices fell 40% from January 2022 to February 2025 (vs. 12% decline for non-EVs). This makes EV pricing dramatically harder — rapid depreciation curves are difficult to model.
- Consumer interest is surging: EV search volume on carmax.com nearly doubled from 2022 to 2025.
- Top sellers: Tesla Model 3 and Model Y remain #1 and #2; Ford F-150 Lightning and Rivian R1T have entered the top 10.
- CarMax is investing in EV-specific infrastructure:
  - **Battery health assessment tool** (partnering with third parties)
  - **$200 credit toward home charger installation** for EV buyers
  - **CarMax EV Hub** online educational resource
  - Highlighting vehicles eligible for the **federal used EV tax credit**
- Pricing challenge for EVs:
  - Battery degradation is non-linear and depends on usage patterns, climate, charging habits
  - Range anxiety affects resale value differently across geographies
  - Rapid technology improvement means newer models cannibalize older ones faster than in ICE vehicles
  - Federal tax credit eligibility changes create price discontinuities
  - The ICE-to-EV market transition creates regime changes that historical models cannot fully anticipate

### Competitive Pricing and Marketing Push

Under interim leadership, CarMax has adopted a dual strategy:
- **Shrinking the price gap** between CarMax and the broader market, including more aggressive pricing on certain segments
- **Increased marketing spend** to drive traffic and restore sales velocity
- This directly affects the pricing algorithms team: the balance between margin and volume is being recalibrated toward volume in the near term

### CAF Penetration Growth

- Current CAF penetration: ~42% of CarMax retail customers
- Strategic target: 50%
- Higher CAF penetration means more of the customer lifetime value is captured internally
- Pricing algorithms interact with financing: a vehicle's total cost of ownership (price + financing) affects conversion. The pricing team likely coordinates with CAF to optimize the combined offer.

### Wholesale Optimization

- CarMax is one of the largest wholesale auction operators in the country
- 59 locations, all-digital format
- Wholesale margin optimization is a parallel track for the pricing team
- The retail/wholesale routing decision (should this vehicle be retailed or wholesaled?) is itself a pricing algorithm problem: it depends on predicted retail margin, reconditioning cost, and holding cost versus expected wholesale proceeds

---

## 7. KEY CHALLENGES FOR PRICING DATA SCIENTISTS

### Vehicle Heterogeneity

This is the defining challenge. Unlike airline seats or hotel rooms, where the product is well-defined and relatively homogeneous, every used vehicle is unique. A 2022 Honda Civic Sport with 25,000 miles, red exterior, black interior, no accidents, in Dallas, TX is a different product from a 2022 Honda Civic Sport with 25,000 miles, white exterior, gray interior, one minor accident, in Seattle, WA. The pricing model must capture all of these dimensions and their interactions.

Practical implications:
- Tabular gradient-boosted models (XGBoost, LightGBM) are well-suited because they handle feature interactions natively
- Embeddings or entity encodings may be needed for high-cardinality categorical features (make/model/trim combinations)
- Hierarchical models (e.g., Bayesian hierarchical regression) can borrow strength from similar vehicles when data is sparse for a specific combination

### Market Volatility

The COVID-era used car market was a stress test for every pricing model in the industry:
- Manheim Used Vehicle Value Index spiked ~50% in 2021-2022 due to new car supply chain disruptions
- Then corrected ~20-25% as supply normalized
- Models trained on pre-COVID data produced wildly inaccurate predictions during the bubble
- Lesson: The pricing system needs regime-detection mechanisms that identify when historical relationships are breaking down, and can adapt rapidly (online learning, frequent retraining, ensemble methods that blend short-term and long-term signals)

Current volatility factors:
- Interest rate environment: High rates compress affordability, shifting demand toward cheaper vehicles
- Tariff uncertainty: Potential tariffs on imported vehicles affect new car supply, which ripples into used car supply and pricing
- EV transition: Rapid EV depreciation creates unpredictable market dynamics

### Balancing Speed-to-Sale vs. Margin

This is the central tension in pricing:
- **High price**: Higher GPPU per unit, but lower probability of sale, longer days on lot, higher holding costs
- **Low price**: Higher probability of sale, faster turn, lower holding costs, but lower GPPU
- The optimal price maximizes **expected total gross profit per vehicle**, which is: `E[GP] = P(sale at price p, within time t) * (p - cost) - holding_cost(t)`
- This is a continuous optimization problem, and the optimal answer changes daily as market conditions shift

For the interview, frame this as:
- "This is fundamentally a dynamic pricing problem under uncertainty. I would model the probability of sale as a function of price, time on lot, and market conditions, then optimize the price that maximizes expected margin net of holding costs. I have experience with similar problems in scoring 40M+ heterogeneous entities where the model must balance precision against coverage."

### Reconditioning Cost Prediction

Before a vehicle is reconditioned, its reconditioning cost must be estimated to determine:
1. Whether to retail or wholesale the vehicle
2. What the minimum viable retail price is (acquisition + estimated recon + target margin)
3. Whether to even acquire the vehicle in the first place (Instant Offer)

The challenge: reconditioning costs vary dramatically based on vehicle condition, and the full scope of repairs is not known until the vehicle is inspected. There is a 45% rework rate after the initial mechanical inspection (meaning almost half of vehicles need additional repairs beyond what was initially identified). Predicting reconditioning costs accurately is a regression problem with high variance.

### Geographic Demand Variation

The same vehicle can sell for significantly different prices in different markets:
- Pickup trucks: Higher demand and premium in the South, Midwest, and rural areas
- AWD/4WD vehicles: Higher demand in the Northeast, Pacific Northwest, and mountain states
- Convertibles: Higher demand in the South, Florida, and California
- Fuel-efficient vehicles: Higher demand in urban markets with high gas prices
- Luxury vehicles: Higher demand near affluent metro areas

The pricing algorithm must account for geographic demand, and the transfer pricing algorithm must decide when it is profitable to move a vehicle from a low-demand market to a high-demand market (factoring in transportation costs).

### Seasonality

Used car demand follows predictable seasonal patterns:
- **February-April (tax refund season)**: Highest volume period. Tax refunds provide down payment funds. Pricing can be more aggressive (higher) because demand is strong.
- **Spring/Summer**: Convertibles and sporty vehicles sell well. SUVs and trucks sell well for summer activities.
- **Fall**: Back-to-school creates demand for commuter vehicles. Demand for convertibles wanes.
- **Pre-Winter**: SUVs, 4WD, AWD vehicles see increased demand as buyers prepare for winter weather.
- **December-January**: Typically slowest period. Year-end clearance may require deeper markdowns.

The seasonal patterns interact with vehicle type, geography, and macro conditions. A simple monthly adjustment is insufficient — the model must learn segment-specific seasonal curves.

### EV Pricing Uncertainty

This is the frontier challenge:
- Battery degradation follows non-linear curves that depend on factors not visible in standard vehicle data (charging habits, climate exposure, fast-charging frequency)
- Battery health assessment is still an emerging science — CarMax is investing in third-party assessment tools, but the data is new and sparse
- Federal and state incentives create price discontinuities: a vehicle that qualifies for a $4,000 used EV tax credit is effectively worth $4,000 more to the buyer, but eligibility rules change
- Technology improvement velocity in EVs is faster than in ICE vehicles, causing older EVs to depreciate faster (a 2021 EV with 250-mile range is less attractive when 2024 EVs get 350+ miles)
- The used EV market is small but growing rapidly — models trained on limited EV transaction data may not generalize

### Cannibalization Between Stores

CarMax often has multiple stores in the same metropolitan area. If Store A and Store B both have similar Camrys, they compete with each other for the same customer. The pricing algorithm must consider:
- Inventory overlap between nearby stores
- Whether reducing the price at Store A will cannibalize a sale at Store B (where the vehicle might have sold at a higher price)
- Optimal inventory allocation: should similar vehicles be distributed across stores or concentrated?

This is a spatial pricing problem with network effects — similar to optimizing pricing across a multi-location retail chain.

---

## 8. CARMAX TECH STACK

### Data and Cloud Infrastructure

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Cloud Platform | Microsoft Azure | Primary cloud infrastructure |
| Data Platform | Azure Databricks | Unified analytics and ML platform |
| Distributed Compute | Apache Spark | Large-scale data processing, feature engineering |
| Data Storage | Azure Data Lake Storage | Raw and processed data storage |
| ETL/Orchestration | Azure Data Factory | Data pipeline orchestration |
| Data Catalog | Azure Data Catalog | Data discovery and governance |

### Machine Learning Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Experiment Tracking | MLflow | Track experiments, compare models, manage model lifecycle |
| Model Registry | MLflow Model Registry | Version control, staging, production deployment of models |
| Deep Learning | TensorFlow | Neural network-based models (demand forecasting, embeddings) |
| Gradient Boosted Trees | XGBoost / LightGBM (likely) | Tabular pricing models — industry standard for heterogeneous features |
| Classical ML | scikit-learn (likely) | Preprocessing, simpler models, baseline comparisons |
| Languages | Python, SQL | Model development, data manipulation |

### Production Systems

| Component | Description |
|-----------|-------------|
| Batch Pricing | Overnight / periodic repricing of entire inventory |
| Real-time Scoring | Instant Offer and dynamic pricing adjustments |
| A/B Testing | Infrastructure for running pricing experiments in production |
| Monitoring | Model performance monitoring, drift detection, alert systems |

### Why This Stack Matters for the Interview

- CarMax has invested in Databricks + MLflow, which means they value experiment reproducibility and model lifecycle management. If asked about your workflow, describe: "I use MLflow to track every experiment — hyperparameters, metrics, artifacts — so that any model in production can be traced back to the exact training run that produced it."
- Apache Spark signals large data volumes. Be prepared to discuss distributed feature engineering and how you handle data that does not fit in memory.
- A/B testing infrastructure means they run controlled experiments on pricing strategies. Your experiment design experience (power analysis, multiple comparison corrections, sequential testing) is directly relevant.

### AI and ML Investment Signals

CarMax has been using AI/ML in pricing for 12-13 years according to their top tech executive. Recent AI investments include:
- **Instant Offer**: AI-powered vehicle valuation tool that gives consumers an offer in under 2 minutes
- **Skye**: AI-powered virtual assistant handling tens of thousands of customer conversations weekly
- **ChatGPT integration**: First U.S. auto retailer in the ChatGPT App Store (launched February 2026)
- **Predictive analytics**: Demand forecasting, inventory optimization, reconditioning cost estimation
- **Personalization**: Search and recommendation algorithms for the online shopping experience

---

## 9. CARMAX VALUES & CULTURE

### Core Values

CarMax was built on a set of values that continue to define the culture:

1. **Integrity**: Do the right thing, even when no one is watching. The no-haggle pricing model is itself an expression of integrity — the price is the same for every customer regardless of their negotiating skill, socioeconomic background, or demographics. This is a genuine differentiator, not just marketing.

2. **Transparency**: Related to integrity. CarMax publishes its prices. It discloses vehicle history. It does not hide fees. The pricing algorithms team is an extension of this value — the algorithm must produce prices that are defensibly fair.

3. **Respect**: CarMax treats customers and associates with respect. The no-pressure sales environment (salaried consultants, no-commission model) removes the adversarial dynamic of traditional car buying.

4. **Associate-first culture**: CarMax calls all employees "associates," not "employees" or "workers." This is not just terminology — it reflects a culture that invests in career development, training, and internal promotion. Many store managers started as sales consultants.

### Industry Recognition

- **Fortune 100 Best Companies to Work For**: CarMax has been on this list for **21 consecutive years** (as of 2025). This is one of the longest streaks of any company.
- **Fortune's Best Workplaces in Retail**: Named for 11 consecutive years, ranked #6 in the large company category (2025).
- **PEOPLE Companies That Care**: Ranked #38 (2025).
- **Great Place to Work**: 88% of employees say CarMax is a great place to work (vs. 57% at a typical U.S. company).

### What This Means for the Interview

CarMax interviewers care about cultural fit. Key signals to send:

- **Integrity over expedience**: "When I caught the look-ahead bias bug in my feature pipeline, I did not just fix it — I quantified the $222K impact and built monitoring to prevent recurrence. I reported the full scope of the problem, including the financial damage, rather than minimizing it."

- **Data-driven transparency**: "I believe in showing my work. When my validation framework revealed that the GAN model was not statistically significant on diagnostic accuracy despite looking great on image quality metrics, I presented both results. The decision-making improved because the full picture was visible."

- **Collaborative problem-solving**: While you lead with technical depth (per the lessons from your TikTok prep), frame it within a collaborative context. CarMax is a team-oriented culture. "I built the experimentation framework and then drove adoption across three teams by making it easier to use than to not use."

- **Respect for domain expertise**: "Pricing is a domain I am excited to learn deeply. My track record shows I can rapidly acquire domain expertise — I transitioned from medical imaging to fraud detection to content safety, each time building models that reflected deep understanding of the problem domain."

---

## 10. NUMBERS TO KNOW — QUICK REFERENCE TABLE

Print this table or review it 30 minutes before the interview. These are the numbers that let you speak with specificity about CarMax's business.

### Company Fundamentals

| Metric | Value | Context |
|--------|-------|---------|
| Founded | 1993 (as Circuit City subsidiary) | Spun off 2002 |
| HQ | Richmond, Virginia | Also the primary tech hub |
| NYSE Ticker | KMX | |
| Stores | 250+ | Two new stores opened Q3 FY2026 |
| Associates | 30,000+ | All employees called "associates" |
| Auction locations | 59 | All-digital format |
| Fortune 100 Best | 21 consecutive years | One of the longest streaks |

### Volume and Revenue

| Metric | Value | Period |
|--------|-------|--------|
| Total net revenues | $26.35 billion | FY2025 |
| Retail vehicles sold | ~790,000 | FY2025 |
| Wholesale vehicles sold | ~540,000 | FY2025 |
| Total vehicles sold | ~1.33 million | FY2025 |
| Used vehicle market share | ~3.7% (age 0-10 vehicles) | CY2024 |
| CAF receivables originated | $8+ billion | FY2025 |
| CAF managed portfolio | ~$18 billion | FY2025 |

### Unit Economics

| Metric | Value | Period |
|--------|-------|--------|
| Retail GPPU | $2,322 | Q4 FY2025 |
| Wholesale GPPU | $1,045 | Q4 FY2025 |
| Average retail selling price | ~$26,130 | Early 2025 |
| Retail gross margin | ~8.9% | Derived |
| Avg. reconditioning cost | ~$1,000-1,500 | Approximate |
| Avg. reconditioning time | 12+ hours | Per vehicle |
| Inspection checklist | 125+ points | Proprietary |
| Rework rate after initial inspection | ~45% | Internal metric |

### Operational Metrics

| Metric | Value | Period |
|--------|-------|--------|
| Days inventory (days on lot) | ~52 days | Recent quarters |
| Inventory turnover ratio | ~1.57-1.76 | Varies by quarter |
| Digital-supported sales | 80%+ | Q4 FY2025 |
| Omnichannel sales | ~58-67% | Q4 FY2025 |
| Fully online sales | ~14-15% | Q4 FY2025 |
| CAF penetration | ~42% | Recent; target 50% |

### Financial Health

| Metric | Value | Period |
|--------|-------|--------|
| Q4 FY2025 net revenues | $6.0 billion | Up 6.7% YoY |
| Q4 FY2025 total gross profit | $667.9 million | Up 13.9% YoY |
| Q4 FY2025 CAF income | $159.3 million | Up 8.2% YoY |
| Q4 FY2025 EPS (diluted) | $0.58 | Up 81.3% YoY |
| Q1 FY2026 EPS (diluted) | $1.38 | Up 42.3% YoY |
| SG&A reduction target | $150M+ over 18 months | Announced Q2 FY2026 |
| SG&A as % of gross profit | ~80.3% | Improved from 84.1% |

### EV Market Data

| Metric | Value | Period |
|--------|-------|--------|
| Used EV price decline | -40% | Jan 2022 to Feb 2025 |
| Non-EV price decline | -12% | Same period |
| EV search volume growth | Nearly doubled | Jan 2022 to Feb 2025 |
| Top used EVs | Tesla Model 3, Model Y | 3 consecutive years |

### Competitive Context

| Competitor | Position | Key Difference |
|-----------|----------|----------------|
| Carvana | Online-first, S&P 500 (Dec 2025) | No physical stores for browsing |
| Vroom | Largely exited retail | Cautionary tale |
| AutoNation | Largest franchise group | New cars primary |
| Lithia/Driveway | Growing digital platform | Franchise + digital |
| Private dealers | ~100,000+ fragmented | No transparency |

---

## 11. CONNECTING YOUR EXPERIENCE TO CARMAX

### The Core Narrative

Your experience maps to CarMax's needs through a common thread: **building ML systems that value heterogeneous entities at scale under uncertainty**. At your previous roles, you scored 40M+ entities. At CarMax, you would price 790K+ unique vehicles. The statistical and engineering challenges are structurally identical — the domain is different, but the methodology transfers.

### Experience-to-Role Mapping

Use this table to prepare bridges. When the interviewer asks about a CarMax-specific challenge, reach for the analogous experience and translate.

| Your Experience | CarMax Need | Bridge Language |
|----------------|-------------|-----------------|
| **Scoring 40M+ heterogeneous entities** | Pricing 790K unique vehicles per year | "I built models that valued diverse entities where every instance had different features — the same challenge as pricing used vehicles where every car has a different combination of make, model, mileage, condition, and location." |
| **AutoML platform for rapid model iteration** | Rapid experimentation on pricing algorithms | "I built an AutoML framework that reduced model development cycle time, enabling faster iteration — the same need the pricing team has for testing new model architectures and feature sets quickly." |
| **A/B testing frameworks with power analysis** | A/B testing pricing strategies in production | "I designed experiment frameworks with proper power analysis, multiple comparison corrections, and sequential testing — directly applicable to running controlled pricing experiments where you need to detect a $50 GPPU change with statistical confidence." |
| **Fraud detection under extreme class imbalance (0.1%)** | Pricing rare/unusual vehicles with sparse data | "Fraud detection at 0.1% positive rate taught me how to build models that generalize from limited signal. Pricing a rare vehicle trim with only 10 comparable transactions is the same sparse-data challenge." |
| **Temporal feature engineering (velocity, entropy, z-scores)** | Market signal feature engineering for pricing | "I engineered 12 temporal features for fraud detection using sliding window aggregations. For vehicle pricing, the same approach captures market momentum — price velocity of comparable vehicles over 7/14/30-day windows, demand signal trends, and supply-side indicators." |
| **Cross-functional collaboration with business stakeholders** | Working with buyers, operations, and finance teams | "I have experience translating model outputs into business decisions. At CarMax, the pricing model serves buyers (acquisition pricing), operations (reconditioning routing), and finance (margin and turn targets). I have worked at that intersection of ML and business decision-making." |
| **PhD statistical rigor (Bonferroni, bootstrap CIs, effect sizes)** | Sound mathematical reasoning for pricing under uncertainty | "My PhD trained me to think about uncertainty quantitatively. Every pricing recommendation should come with a confidence interval, and every pricing experiment should be designed with proper statistical power." |
| **Catching data pipeline bugs ($222K impact, 23% VVR inflation)** | Data quality for pricing models | "In pricing, a data pipeline bug that corrupts comparable vehicle prices or misattributes vehicle features could systematically misprice thousands of vehicles. I have experience building monitoring systems that detect exactly these kinds of silent failures." |
| **Real-time anomaly detection (18h to 4.2 min latency)** | Detecting market shifts that require pricing adjustments | "I reduced anomaly detection latency from 18 hours to 4.2 minutes. For CarMax, detecting a sudden market shift (like COVID-era price spikes or a competitor repricing) and propagating that signal to the pricing model quickly is the same real-time detection problem." |
| **Experiment design template adopted by 3 teams** | Standardizing pricing experimentation practices | "I built an experimentation framework with pre-registration, CUPED variance reduction, and sequential testing that was adopted across multiple teams. The same infrastructure would accelerate pricing experiments at CarMax while maintaining statistical rigor." |

### Key Talking Points to Drop in Conversation

Practice saying these naturally. Each one demonstrates business-specific knowledge:

1. **On pricing complexity**: "What makes CarMax's pricing problem uniquely challenging is the no-haggle model. Traditional dealers have a negotiation buffer — if they overprice, the salesperson can adjust. CarMax does not have that luxury. The algorithm has to be right the first time, which means the confidence interval around each price recommendation directly determines margin."

2. **On unit economics**: "With a retail GPPU of about $2,300 on a $26,000 average selling price, we are talking about an 8-9% gross margin. At 790,000 units, a $100 improvement in GPPU is a $79 million impact. That is the scale of opportunity for the pricing algorithms team."

3. **On days on lot**: "Days on lot is effectively the hidden cost in the pricing equation. A vehicle sitting at 52 days when it could sell at 45 days is accumulating depreciation, floor plan interest, and opportunity cost. The pricing algorithm has to optimize not just price level but price trajectory — the markdown curve that minimizes total cost of time-on-lot."

4. **On the EV challenge**: "Used EV pricing is the hardest frontier problem in the space right now. Prices fell 40% in three years while ICE vehicles fell only 12%. Battery degradation is non-linear and depends on factors we cannot observe in standard vehicle data. The models need new features — battery health assessments, charging history, regional climate data — and they need to handle the uncertainty that comes with limited EV transaction history."

5. **On the data advantage**: "CarMax's competitive moat in pricing is its 30 years of proprietary transaction data across every vehicle type, geography, and market condition. No one else has that dataset. The pricing algorithms team is the group that converts that data advantage into margin advantage."

6. **On the SG&A reduction target**: "The $150 million SG&A reduction target announced last year signals that leadership is investing in automation and optimization. Pricing algorithm improvements reduce days on lot, reduce markdowns, and improve inventory turn — all of which directly support the SG&A efficiency goals."

7. **On wholesale routing**: "The retail vs. wholesale routing decision is itself a pricing problem. A vehicle that would produce $1,500 gross profit at retail after $2,000 in reconditioning costs might produce $1,100 gross profit at wholesale with zero reconditioning cost. The expected value calculation depends on reconditioning cost prediction accuracy and retail demand prediction — both ML problems."

8. **On geographic optimization**: "Transfer pricing — deciding whether to move a pickup truck from a coastal market where it is a slow seller to a Southern market where it commands a premium — is an optimization problem where the expected margin uplift must exceed the transportation cost. At CarMax's scale, even small improvements in transfer decisions aggregate into significant margin gains."

9. **On CAF synergies**: "I find the CAF interaction interesting. The customer does not care whether they get a $500 discount on the vehicle price or a 0.5% lower interest rate — both reduce their monthly payment. The pricing algorithm and the financing offer could theoretically be jointly optimized to maximize total customer lifetime value across both the vehicle margin and the loan income."

10. **On the competitive landscape**: "Carvana's recovery and S&P 500 addition shows that the all-digital model works. CarMax's advantage is the omnichannel model — 67% of buyers blend online and in-store steps. The pricing algorithm supports both channels: it must produce prices that are competitive when a customer is comparing online and compelling when they are standing in front of the vehicle."

### What the Interviewer Wants to Hear

The Sr. Data Scientist — Pricing Algorithms role requires someone who can:

1. **Think in unit economics**: Every model improvement must be translated into dollars per unit or total margin impact. Never talk about model accuracy in isolation — always connect it to GPPU, days on lot, or inventory turn.

2. **Handle messy, heterogeneous data**: Your medical imaging and fraud detection experience proves you can work with complex, high-dimensional data where no two instances are the same.

3. **Design and run experiments rigorously**: A/B testing pricing strategies is high-stakes — a poorly designed experiment can cost millions in lost margin. Your experiment design credentials (power analysis, multiple comparison corrections, sequential testing, CUPED) are directly applicable.

4. **Communicate to non-technical stakeholders**: The pricing team's recommendations go to store operations, finance, and executive leadership. You must be able to explain "why this price" in business terms, not just model terms.

5. **Navigate uncertainty**: Pricing under uncertainty is the entire job. Your statistical training (confidence intervals, Bayesian reasoning, effect size estimation) is the right foundation.

6. **Move fast without breaking things**: The $150M SG&A reduction target and declining Q2-Q3 sales create urgency. The team needs someone who can deliver impact quickly while maintaining model quality and statistical rigor.

---

## APPENDIX: TIMELINE OF KEY EVENTS

| Date | Event | Significance |
|------|-------|-------------|
| 1993 | CarMax founded as Circuit City subsidiary | Pioneer of no-haggle used car retail |
| 2002 | CarMax spun off as independent company | KMX begins trading on NYSE |
| 2004 | First appearance on Fortune 100 Best Companies | Beginning of 21-year streak |
| ~2012 | Began investing in AI/ML for pricing | 12+ years of ML-powered pricing |
| 2020-2022 | COVID used car price bubble | Manheim Index spiked ~50%; stress test for all pricing models |
| 2022-2023 | Used car price correction | Prices corrected ~20-25% from peak |
| FY2025 (Feb 2025) | Annual revenue $26.35B; 790K retail units | Flat YoY; stable but not growing |
| Q1 FY2026 (May 2025) | Retail unit sales +9.0%; EPS $1.38 (+42%) | Strong start to fiscal year |
| Q2 FY2026 (Aug 2025) | Retail unit sales -5.4%; $150M SG&A target | Sales decelerate; cost focus begins |
| Nov 2025 | CEO Bill Nash steps down | David McCreight interim CEO; Tom Folliard interim Chair |
| Dec 2025 | Q3 FY2026: retail unit sales -8.0% | Continued deceleration |
| Dec 2025 | Carvana added to S&P 500 | Key competitor reaches milestone |
| Feb 2026 | CarMax launches ChatGPT App Store integration | First U.S. auto retailer in ChatGPT ecosystem |
| Mar 2026 | Your interview | They need someone who can move the needle now |

---

## APPENDIX: GLOSSARY OF CARMAX-SPECIFIC TERMS

| Term | Definition |
|------|-----------|
| **GPPU** | Gross Profit Per Unit — the primary measure of per-vehicle profitability |
| **CAF** | CarMax Auto Finance — the captive lending arm |
| **MaxCare** | CarMax's extended service plan product |
| **Instant Offer** | Online tool that gives consumers a firm offer for their vehicle in under 2 minutes |
| **Omnichannel** | Sales that blend online and in-store steps (browsing online, buying in store, or vice versa) |
| **Days on lot (DOL)** | Number of days from when a vehicle is available for sale to when it sells |
| **Floor plan** | The credit facility CarMax uses to finance its inventory — interest accrues daily on every vehicle |
| **Reconditioning** | The inspection and repair process that brings a vehicle to CarMax retail standards |
| **Wholesale** | Vehicles that do not meet retail standards, sold at CarMax-operated auctions to dealers |
| **Transfer** | Moving a vehicle from one CarMax store to another to match geographic demand |
| **Markdown** | Reducing the price of a vehicle that has not sold within the target days-on-lot window |
| **SG&A** | Selling, General & Administrative expenses — the primary operating cost measure |
| **Net interest margin (NIM)** | For CAF: the spread between what CAF earns on loans and what it pays on funding |
| **Manheim Index** | The Manheim Used Vehicle Value Index — the industry benchmark for wholesale used car prices |
| **Skye** | CarMax's AI-powered virtual assistant on the website |
| **KMX** | CarMax's NYSE ticker symbol |

---

## APPENDIX: QUESTIONS YOU MIGHT ASK THE INTERVIEWER

Asking smart questions demonstrates preparation. Pick 2-3 from this list based on what feels natural in the conversation:

1. "How does the pricing team handle the transition from ICE to EV? I imagine the depreciation curves and feature importance are fundamentally different for EVs, and the training data is much sparser."

2. "What is the current balance between batch pricing (overnight repricing of inventory) and real-time pricing adjustments? Is there a strategic direction toward more real-time dynamic pricing?"

3. "How do you think about the interaction between the retail pricing algorithm and the Instant Offer acquisition pricing? Are these separate models or jointly optimized?"

4. "With the $150 million SG&A reduction target, how is the pricing team expected to contribute? Is the focus on reducing days on lot, improving GPPU, or both?"

5. "What does the experiment lifecycle look like for a pricing strategy change? How long does a typical A/B test run, and what is the decision framework for shipping or rolling back?"

6. "How does the team handle geographic cannibalization — pricing similar vehicles across multiple CarMax stores in the same metro area?"

7. "What is the biggest model performance gap today — is it on common vehicles where even small improvements at scale are valuable, or on rare vehicles where the model struggles with sparse data?"

8. "How does the team think about model interpretability? For a no-haggle pricing model, can you explain to a customer or to operations why a specific vehicle is priced the way it is?"

---

*Last reviewed: Night of March 11, 2026. Good luck tomorrow.*
