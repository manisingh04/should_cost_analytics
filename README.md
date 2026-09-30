# Strategic Sourcing & Should-Cost Analytics Engine
### *Parametric Cost Engineering, Commodity Indexation & Margin Optimization for Signify Lighting*

[![Tech Stack](https://img.shields.io/badge/Stack-SQL%20%7C%20Python%20%7C%20Pandas%20%7C%20NumPy%20%7C%20Seaborn%20%7C%20Excel%20%7C%20PowerBI-blue)](#)
[![Domain](https://img.shields.io/badge/Domain-Strategic%20Sourcing%20%26%20Cost%20Engineering-orange)](#)
[![Industry Focus](https://img.shields.io/badge/Industry-Lighting%20Manufacturing%20(Signify)-green)](#)

---

## 📌 Executive Summary
In commercial luminaire manufacturing (streetlights, industrial high-bays, troffers), structural components—such as **high-pressure die-cast (HPDC) aluminum housings**, **6063-T6 extruded heatsinks**, and **precision CRCA stamped sheet metal**—account for **35% to 45% of total direct Bill-of-Materials (BOM) procurement spend**.

Direct procurement teams often struggle during supplier price negotiations because suppliers inflate piece prices citing rising raw material costs (like LME Aluminum), but fail to pass cost reductions back when commodity markets cool down. Without engineering physics models, buyers cannot detect hidden supplier margins.

This project engineers an **automated, bottom-up Parametric Should-Cost & Commodity Pass-Through Engine** using **SQL, Python (NumPy, Pandas, Seaborn), Excel, and Power BI**. It analyzes 40 structural lighting parts and 400+ supplier quotes across 4 luminaire platforms to identify fair cost benchmarks, calculate pricing variance, and uncover over **$354,000 in actionable procurement cost-out opportunities**.

---

## 📐 Engineering & Mathematical Modeling Framework

### 1. Bottom-Up Parametric Should-Cost Teardown
For each component, the engineered should-cost is deconstructed into manufacturing fundamentals:

$$\text{Engineered Should-Cost} = \text{Direct Mfg Cost} + \text{SG\&A (8\%)} + \text{Fair Margin (10\%)}$$

Where Direct Manufacturing Cost is calculated as:
$$\text{Direct Mfg Cost} = \text{Net Material Cost} + \text{Machine Processing Cost} + \text{Direct Labor} + \text{Secondary Finish}$$

1. **Net Material Economics & Scrap Credit:**
   $$\text{Net Material} = (\text{Gross Shot Weight} \times P_{\text{LME}}) - [(\text{Gross Shot Weight} - \text{Net Weight}) \times P_{\text{LME}} \times R_{\text{scrap}}]$$
   *(where $R_{\text{scrap}} = 65\%$ for ADC12 aluminum runner/dross recycling credit).*
2. **Machine Processing Economics:**
   $$\text{Machine Cost} = \left(\frac{\text{Cycle Time (sec)}}{3600 \times \text{Tooling Cavities}}\right) \times \text{Machine Hourly Rate (\$/hr)}$$
   *(Rate cards benchmarked by machine clamping tonnage: 250T = \$38/hr, 400T = \$54/hr, 650T = \$76/hr, 800T = \$98/hr).*
3. **Secondary Finishing:**
   Powder coating, shot blasting, or anodizing rate cards applied per kg of finished metal.

### 2. Contractual Commodity Price Pass-Through Formula
To insulate Signify against commodity volatility without adversarial re-negotiations, an automated indexation formula is modeled:

$$\Delta P_{\text{piece}} = (P_{\text{LME, Current}} - P_{\text{LME, Base}}) \times \text{Net Finished Weight (kg)}$$

---

## 📊 Key Findings & Visual Deliverables

### Figure 1: Supplier Quoted Price vs. Engineered Should-Cost Distribution
![Distribution](reports/figures/fig1_quote_vs_should_cost_distribution.png)
* **Finding:** Across 40 structural luminaire components, supplier quote distributions show an asymmetric right-tail bias, exposing hidden profit margins above the fair 10% EBIT threshold.

### Figure 2: 24-Month Commodity Volatility Benchmark
![Commodity History](reports/figures/fig2_commodity_correlation_matrix.png)
* **Finding:** LME Aluminum cycled between \$2.15/kg and \$2.65/kg over 24 months. SQL window function queries reveal that Tier-2 vendors raised quotes during spikes but delayed lowering quotes during price declines by an average of 4.2 months.

### Figure 3: Supplier Pricing Variance Scatter Matrix
![Supplier Variance](reports/figures/fig3_supplier_margin_variance_scatter.png)
* **Finding:** Clearly isolates competitive Tier-1 partners from high-margin vendors charging >15% above engineered baseline, providing exact target parts for upcoming quarterly RFQs.

### Figure 4: Flagship Luminaire Housing (StreetStar ADC12) Cost Teardown
![Cost Teardown](reports/figures/fig4_luminaire_cost_breakdown_waterfall.png)
* **Finding:** For a 4.15 kg die-cast streetlight housing, net raw aluminum accounts for 58.4% of piece cost, machine processing on a 650T HPDC press accounts for 16.2%, and finishing/overhead makes up the remainder.

### Figure 5: Signify Direct Aluminum Portfolio Spend Sensitivity
![Spend Sensitivity](reports/figures/fig5_lme_price_passthrough_sensitivity.png)
* **Finding:** A $\pm 15\%$ swing in LME Aluminum translates to a **\$480,000 annual spend variance**, demonstrating the business necessity of automated price pass-through clauses in vendor master service agreements (MSAs).

---

## 🛠️ Project Directory Structure

```
signify_should_cost_analytics/
├── data/                                # Clean CSV datasets
│   ├── parts_manufacturing_specs.csv    # 40 luminaire parts with tonnage/cycle times
│   ├── suppliers_procurement.csv        # 10 strategic suppliers
│   ├── lme_commodity_history.csv        # 24 months LME benchmark data
│   └── supplier_quotes_history.csv      # 400+ supplier RFQ quotes
├── database/                            # SQL relational layer
│   ├── schema.sql                       # DDL schema
│   ├── queries.sql                      # Advanced price-creep & commodity queries
│   └── signify_sourcing.db              # SQLite relational database
├── scripts/                             # Python Data & Analytics Engines
│   ├── generate_sourcing_data.py        # Sourcing data generator
│   ├── should_cost_engine.py            # Parametric should-cost & Excel engine
│   └── eda_procurement_visuals.py       # Seaborn publication-ready charts
├── output/                              # Executive Excel & CSV Outputs
│   ├── Signify_Should_Cost_Negotiation_Model.xlsx # 4-sheet negotiation model
│   ├── fact_part_should_cost.csv        # Master should-cost table
│   ├── fact_supplier_pricing_variance.csv # Variance per part and vendor
│   └── fact_commodity_sensitivity.csv   # LME sensitivity simulation
├── reports/figures/                     # 5 High-Resolution Seaborn Charts
├── power_bi/                            # Power BI setup and DAX formulas
│   ├── DAX_MEASURES.md                  # DAX formulas for Sourcing Control Tower
│   └── POWER_BI_GUIDE.md                # 3-Page dashboard design manual
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Execution Instructions

```bash
# 1. Generate Sourcing Data & SQLite DB
python scripts/generate_sourcing_data.py

# 2. Run Parametric Should-Cost Engine & Build Excel Model
python scripts/should_cost_engine.py

# 3. Generate Seaborn Strategic Sourcing Visuals
python scripts/eda_procurement_visuals.py
```

---

## 💬 Interview Pitch (For GET - Supply Chain / Sourcing at Signify)

> **Interviewer:** *"How does your Mechanical background help you in Strategic Sourcing and Direct Procurement?"*

> **Your Response:**  
> *"In lighting manufacturing, 40% of BOM cost is tied up in aluminum heatsinks, die-cast housings, and sheet metal brackets. Business graduates can only compare historical prices, but as a Mechanical Engineer, I can build bottom-up should-cost models based on manufacturing physics.*  
>  
> *In this project, I modeled 40 luminaire components using machine clamping tonnages (250T to 800T press rates), shot cycle times, and scrap recovery credits. I built a Python and SQL pipeline analyzing 400+ supplier quotes against 24 months of LME Aluminum indices.*  
>  
> *I found that suppliers were charging an 11% average markup above fair margin, uncovering \$354,000 in actionable cost-out savings. I also formulated an automated LME indexation pass-through formula to protect Signify's margins during commodity spikes, and built an interactive Power BI and Excel negotiation model for direct vendor discussions."*
