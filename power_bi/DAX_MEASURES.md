# Signify Strategic Sourcing & Should-Cost Power BI DAX Measures

Production-ready DAX formulas designed for the **Strategic Sourcing & Cost-Out Control Tower** in Power BI Desktop.

---

### 1. Procurement Spend & Should-Cost Measures (Table: `fact_supplier_pricing_variance`)

```dax
Total Quoted Spend = 
SUM(fact_supplier_pricing_variance[annual_spend_at_quote_usd])
```

```dax
Total Engineered Should-Cost Spend = 
SUMX(
    fact_supplier_pricing_variance,
    fact_supplier_pricing_variance[engineered_should_cost_usd] * fact_supplier_pricing_variance[annual_projected_volume]
)
```

```dax
Total Cost-Out Opportunity ($) = 
SUM(fact_supplier_pricing_variance[annual_cost_out_opportunity_usd])
```

```dax
Average Pricing Variance % = 
DIVIDE(
    [Total Quoted Spend] - [Total Engineered Should-Cost Spend],
    [Total Engineered Should-Cost Spend],
    0
) * 100
```

```dax
Critical Negotiation Parts Count = 
CALCULATE(
    DISTINCTCOUNT(fact_supplier_pricing_variance[part_id]),
    fact_supplier_pricing_variance[pricing_variance_pct] > 15
)
```

```dax
Fair Priced Parts Count = 
CALCULATE(
    DISTINCTCOUNT(fact_supplier_pricing_variance[part_id]),
    fact_supplier_pricing_variance[pricing_variance_pct] >= -3 && fact_supplier_pricing_variance[pricing_variance_pct] <= 5
)
```

---

### 2. Commodity Exposure & Metal Weight Measures (Table: `fact_part_should_cost`)

```dax
Total Annual Finished Metal (MT) = 
SUMX(
    fact_part_should_cost,
    fact_part_should_cost[net_finished_weight_kg] * fact_part_should_cost[annual_projected_volume]
) / 1000
```

```dax
Total Annual Process Scrap (MT) = 
SUMX(
    fact_part_should_cost,
    (fact_part_should_cost[gross_shot_weight_kg] - fact_part_should_cost[net_finished_weight_kg]) * fact_part_should_cost[annual_projected_volume]
) / 1000
```

```dax
Total Recoverable Scrap Credit ($) = 
SUMX(
    fact_part_should_cost,
    fact_part_should_cost[scrap_credit_usd] * fact_part_should_cost[annual_projected_volume]
)
```

---

### 3. Conditional Formatting & KPI Indicators

```dax
Variance Status Color = 
SWITCH(
    TRUE(),
    [Average Pricing Variance %] > 15, "#d62728", -- Red: Excessive markup
    [Average Pricing Variance %] > 5, "#ff7f0e",  -- Orange: Moderate opportunity
    [Average Pricing Variance %] >= -3, "#2ca02c",-- Green: Fair benchmark
    "#1f77b4"                                      -- Blue: Below should cost
)
```
