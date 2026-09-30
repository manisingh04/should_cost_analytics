"""
Signify Strategic Sourcing - Parametric Should-Cost & Negotiation Engine
Author: GET (Supply Chain - Strategic Sourcing)
Tech Stack: Python, Pandas, NumPy, OpenPyXL, SQLite3
"""

import os
import sqlite3
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "signify_sourcing.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Load Data
# -----------------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)

df_suppliers = pd.read_sql_query("SELECT * FROM suppliers_procurement", conn)
df_parts = pd.read_sql_query("SELECT * FROM parts_manufacturing_specs", conn)
df_quotes = pd.read_sql_query("SELECT * FROM supplier_quotes", conn)
df_commodity = pd.read_sql_query("SELECT * FROM lme_commodity_history ORDER BY record_date DESC", conn)

conn.close()

# -----------------------------------------------------------------------------
# 2. Benchmark Commodity & Rate Cards (Signify Global Procurement Standards)
# -----------------------------------------------------------------------------
# Latest benchmark rates (Dec 2025)
latest_comm = df_commodity.iloc[0]
BENCHMARK_RATES = {
    "Aluminum ADC12": float(latest_comm["lme_aluminum_usd_per_kg"]),
    "Aluminum 6063-T6": float(latest_comm["lme_aluminum_usd_per_kg"]) + 0.15, # Premium for 6063 extrusion billet
    "CRCA Steel": float(latest_comm["crca_steel_usd_per_kg"]),
    "Polycarbonate Optical Grade": float(latest_comm["polycarbonate_resin_usd_per_kg"]),
}

SCRAP_RECOVERY_FACTORS = {
    "Aluminum ADC12": 0.65, # 65% of LME recovered from aluminum runner/dross
    "Aluminum 6063-T6": 0.70,
    "CRCA Steel": 0.45,
    "Polycarbonate Optical Grade": 0.40, # Regrind degraded value
}

def get_machine_hourly_rate(tonnage, process):
    if process == "Sheet Metal Stamping":
        return 30.0 if tonnage <= 200 else 42.0
    elif process == "HPDC":
        if tonnage <= 250:
            return 38.0
        elif tonnage <= 400:
            return 54.0
        elif tonnage <= 650:
            return 76.0
        else:
            return 98.0
    elif process == "Extrusion":
        return 50.0 if tonnage <= 400 else 82.0
    else: # Injection Molding
        return 34.0 if tonnage <= 200 else 48.0

LABOR_HOURLY_RATE = 16.0 # Blended operator rate ($/hr)

# -----------------------------------------------------------------------------
# 3. Parametric Bottom-Up Should-Cost Calculation
# -----------------------------------------------------------------------------
should_cost_records = []

for _, p in df_parts.iterrows():
    mat = p["material_alloy"]
    net_wt = p["net_finished_weight_kg"]
    gross_wt = p["gross_shot_weight_kg"]
    tonnage = p["machine_clamping_tonnage"]
    proc = p["manufacturing_process"]
    cycle = p["cycle_time_seconds"]
    cav = p["tooling_cavities"]
    finish = p["secondary_finish"]
    vol = p["annual_projected_volume"]
    
    mat_rate = BENCHMARK_RATES.get(mat, 2.40)
    scrap_factor = SCRAP_RECOVERY_FACTORS.get(mat, 0.60)
    
    # 1. Material Economics
    gross_mat_cost = gross_wt * mat_rate
    scrap_wt = max(0.0, gross_wt - net_wt)
    scrap_credit = scrap_wt * mat_rate * scrap_factor
    net_mat_cost = gross_mat_cost - scrap_credit
    
    # 2. Machine Processing Economics
    m_rate = get_machine_hourly_rate(tonnage, proc)
    effective_cycle_per_unit = cycle / (3600.0 * cav)
    machine_cost = effective_cycle_per_unit * m_rate
    
    # 3. Direct Labor Economics (Assumes 1 operator per 2 machines)
    labor_cost = effective_cycle_per_unit * (LABOR_HOURLY_RATE * 0.5)
    
    # 4. Secondary Operations Cost
    if "Anodizing" in finish:
        finish_cost = 0.65 * net_wt
    elif "Powder Coating" in finish or "Painting" in finish:
        finish_cost = 0.45 * net_wt
    else:
        finish_cost = 0.0
        
    mfg_cost = net_mat_cost + machine_cost + labor_cost + finish_cost
    sga_overhead = 0.08 * mfg_cost # 8% SG&A
    fair_margin = 0.10 * (mfg_cost + sga_overhead) # 10% fair EBIT margin
    total_should_cost = mfg_cost + sga_overhead + fair_margin
    
    should_cost_records.append({
        "part_id": p["part_id"],
        "part_description": p["part_description"],
        "luminaire_platform": p["luminaire_platform"],
        "material_alloy": mat,
        "manufacturing_process": proc,
        "net_finished_weight_kg": net_wt,
        "gross_shot_weight_kg": gross_wt,
        "material_benchmark_usd_kg": round(mat_rate, 3),
        "gross_material_cost_usd": round(gross_mat_cost, 2),
        "scrap_credit_usd": round(scrap_credit, 2),
        "net_material_cost_usd": round(net_mat_cost, 2),
        "machine_hourly_rate_usd": round(m_rate, 2),
        "machine_processing_cost_usd": round(machine_cost, 2),
        "direct_labor_cost_usd": round(labor_cost, 2),
        "secondary_finish_cost_usd": round(finish_cost, 2),
        "total_mfg_cost_usd": round(mfg_cost, 2),
        "sga_overhead_usd": round(sga_overhead, 2),
        "fair_supplier_margin_usd": round(fair_margin, 2),
        "engineered_should_cost_usd": round(total_should_cost, 2),
        "annual_projected_volume": vol,
        "annual_should_cost_spend_usd": round(total_should_cost * vol, 2)
    })

df_should_cost = pd.DataFrame(should_cost_records)

# -----------------------------------------------------------------------------
# 4. Supplier Quote Variance & Pricing Arbitrage Analytics
# -----------------------------------------------------------------------------
# Extract latest RFQ quotes (2025-09-15)
latest_rfq_date = df_quotes["quote_date"].max()
df_quotes_latest = df_quotes[df_quotes["quote_date"] == latest_rfq_date].copy()

df_variance = df_quotes_latest.merge(
    df_should_cost[["part_id", "part_description", "luminaire_platform", "material_alloy", "engineered_should_cost_usd", "annual_projected_volume"]],
    on="part_id",
    how="left"
)
df_variance = df_variance.merge(
    df_suppliers[["supplier_id", "supplier_name", "country", "supplier_tier", "core_manufacturing_capability"]],
    on="supplier_id",
    how="left"
)

# Calculate variance metrics
df_variance["pricing_variance_usd"] = df_variance["quoted_piece_price_usd"] - df_variance["engineered_should_cost_usd"]
df_variance["pricing_variance_pct"] = np.round(
    (df_variance["pricing_variance_usd"] / df_variance["engineered_should_cost_usd"]) * 100, 2
)
df_variance["annual_spend_at_quote_usd"] = df_variance["quoted_piece_price_usd"] * df_variance["annual_projected_volume"]
df_variance["annual_cost_out_opportunity_usd"] = np.maximum(
    0.0, df_variance["pricing_variance_usd"] * df_variance["annual_projected_volume"]
)

def assign_negotiation_priority(var_pct):
    if var_pct > 15.0:
        return "CRITICAL_NEGOTIATION (Excessive Markup >15%)"
    elif var_pct > 5.0:
        return "MODERATE_OPPORTUNITY (5% to 15%)"
    elif var_pct >= -3.0:
        return "FAIR_BENCHMARKED (±5%)"
    else:
        return "BELOW_SHOULD_COST (Quality/Dumping Risk)"

df_variance["negotiation_status"] = df_variance["pricing_variance_pct"].apply(assign_negotiation_priority)

# -----------------------------------------------------------------------------
# 5. Top Cost-Out Opportunities (Executive Sourcing Target List)
# -----------------------------------------------------------------------------
top_cost_out_targets = df_variance[df_variance["annual_cost_out_opportunity_usd"] > 0].sort_values(
    by="annual_cost_out_opportunity_usd", ascending=False
).reset_index(drop=True)

# -----------------------------------------------------------------------------
# 6. LME Commodity Pass-Through Sensitivity Simulator
# -----------------------------------------------------------------------------
# Model Signify contractual formula:
# Price Adjustment = (Current LME - Base LME) * Net Metal Weight
al_parts = df_should_cost[df_should_cost["material_alloy"].str.contains("Aluminum")].copy()
total_al_annual_net_kg = (al_parts["net_finished_weight_kg"] * al_parts["annual_projected_volume"]).sum()
base_lme = BENCHMARK_RATES["Aluminum ADC12"]

lme_shifts = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15]
sensitivity_rows = []

for shift in lme_shifts:
    sim_lme = base_lme * (1.0 + shift)
    delta_spend = (sim_lme - base_lme) * total_al_annual_net_kg
    total_al_spend = (al_parts["engineered_should_cost_usd"] * al_parts["annual_projected_volume"]).sum() + delta_spend
    sensitivity_rows.append({
        "LME_Aluminum_Shift_Pct": f"{shift*100:+.0f}%",
        "Simulated_LME_USD_kg": round(sim_lme, 3),
        "Total_Annual_Aluminum_Purchased_MT": round(total_al_annual_net_kg / 1000.0, 1),
        "Annual_Spend_Delta_USD": round(delta_spend, 2),
        "Total_Adjusted_Procurement_Spend_USD": round(total_al_spend, 2)
    })

df_commodity_sensitivity = pd.DataFrame(sensitivity_rows)

# -----------------------------------------------------------------------------
# 7. Export to Multi-Tab Excel Workbook & Clean CSVs
# -----------------------------------------------------------------------------
excel_path = os.path.join(OUTPUT_DIR, "Signify_Should_Cost_Negotiation_Model.xlsx")

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    df_should_cost.to_excel(writer, sheet_name="Part_Should_Cost_Master", index=False)
    df_variance.to_excel(writer, sheet_name="Supplier_Pricing_Variance", index=False)
    top_cost_out_targets.head(20).to_excel(writer, sheet_name="Negotiation_Targets_Top20", index=False)
    df_commodity_sensitivity.to_excel(writer, sheet_name="LME_Indexation_Sensitivity", index=False)

# Export clean CSVs for Power BI ingestion
df_should_cost.to_csv(os.path.join(OUTPUT_DIR, "fact_part_should_cost.csv"), index=False)
df_variance.to_csv(os.path.join(OUTPUT_DIR, "fact_supplier_pricing_variance.csv"), index=False)
df_commodity_sensitivity.to_csv(os.path.join(OUTPUT_DIR, "fact_commodity_sensitivity.csv"), index=False)

total_cost_out = top_cost_out_targets["annual_cost_out_opportunity_usd"].sum()
total_spend = df_variance["annual_spend_at_quote_usd"].sum()
avg_variance = df_variance["pricing_variance_pct"].mean()

print(f"Should-Cost Engine execution completed.")
print(f"Excel Model generated at: {excel_path}")
print(f"Total Quoted Portfolio Spend: ${total_spend:,.2f}")
print(f"Average Supplier Pricing Variance: {avg_variance:.2f}%")
print(f"Total Identified Cost-Out Potential: ${total_cost_out:,.2f}")
