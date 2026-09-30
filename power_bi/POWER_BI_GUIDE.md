# Power BI Dashboard Setup & Visual Layout Guide
### Strategic Sourcing & Should-Cost Control Tower

This guide provides instructions to build an executive procurement dashboard in **Power BI Desktop**.

---

### 1. Data Ingestion
Load the following CSV files into Power BI:
1. `output/fact_part_should_cost.csv` (Primary Part Manufacturing & Should-Cost Dimension)
2. `output/fact_supplier_pricing_variance.csv` (Fact Table: Supplier Quotes vs Baseline)
3. `data/suppliers_procurement.csv` (Supplier Dimension Table)
4. `output/fact_commodity_sensitivity.csv` (Sensitivity Fact Table)

---

### 2. Star Schema Relationship Modeling
In the **Model View**, configure:
* `fact_part_should_cost[part_id]` ──(1:*)──► `fact_supplier_pricing_variance[part_id]`
* `suppliers_procurement[supplier_id]` ──(1:*)──► `fact_supplier_pricing_variance[supplier_id]`

---

### 3. Recommended 3-Page Dashboard Layout

#### 📄 Page 1: Sourcing Cost-Out Control Tower (Executive Overview)
* **Top KPI Cards:**
  * Card 1: `Total Quoted Spend ($)` (e.g., \$9.27M)
  * Card 2: `Total Cost-Out Opportunity ($)` (e.g., \$354.7K identified savings)
  * Card 3: `Average Pricing Variance %`
  * Card 4: `Critical Negotiation Parts Count`
* **Visual 1 (Donut Chart):** Total Spend by Manufacturing Process (HPDC Die-Casting vs Extrusion vs Stamping vs Injection).
* **Visual 2 (Bar Chart):** Top 10 Suppliers Ranked by Total Overpricing Variance ($).
* **Visual 3 (Interactive Table):** High-priority parts filtered where `pricing_variance_pct > 15%`.

#### 📄 Page 2: Luminaire Cost Teardown & Bottom-Up Engineering
* **Visual 1 (Waterfall / Stacked Bar):** Cost Element Contribution (Net Material, Machine Processing, Direct Labor, Secondary Finish, SG&A, Supplier Margin).
* **Visual 2 (Scatter Plot):** Net Finished Weight (kg) vs Quoted Price ($), with Should-Cost trendline.
* **Slicers:** Slicer for `luminaire_platform` (Road & Street, Industrial HighBay, Troffer, Architectural) and `material_alloy`.

#### 📄 Page 3: Commodity Exposure & LME Price Pass-Through
* **Visual 1 (Clustered Column Chart):** Total Adjusted Procurement Spend under $-15\%$ to $+15\%$ LME Aluminum swings.
* **Visual 2 (Table):** Supplier Raw Metal Consumption (Gross MT, Net MT, Scrap Credit MT).
* **Visual 3 (Card):** Total Recoverable Scrap Credit ($).
