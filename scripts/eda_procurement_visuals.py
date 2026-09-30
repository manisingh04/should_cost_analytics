"""
Signify Strategic Sourcing - Seaborn Visualizations Engine
Author: GET (Supply Chain - Strategic Sourcing)
Tech Stack: Python, Seaborn, Matplotlib, Pandas, NumPy
Generates 5 executive figures for direct procurement and supplier negotiation strategy.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
plt.rcParams["figure.dpi"] = 300

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FIGURES_DIR = os.path.join(BASE_DIR, "reports", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Load data
df_should_cost = pd.read_csv(os.path.join(OUTPUT_DIR, "fact_part_should_cost.csv"))
df_variance = pd.read_csv(os.path.join(OUTPUT_DIR, "fact_supplier_pricing_variance.csv"))
df_commodity = pd.read_csv(os.path.join(DATA_DIR, "lme_commodity_history.csv"))
df_sensitivity = pd.read_csv(os.path.join(OUTPUT_DIR, "fact_commodity_sensitivity.csv"))

# -----------------------------------------------------------------------------
# CHART 1: Quoted Price vs. Engineered Should-Cost Distribution
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.5))

sns.kdeplot(
    data=df_variance["engineered_should_cost_usd"],
    label=f"Engineered Should-Cost (Mean: ${df_variance['engineered_should_cost_usd'].mean():.2f})",
    color="#1b9e77",
    linewidth=2.5,
    fill=True,
    alpha=0.2,
    ax=ax
)

sns.kdeplot(
    data=df_variance["quoted_piece_price_usd"],
    label=f"Supplier Quoted Price (Mean: ${df_variance['quoted_piece_price_usd'].mean():.2f})",
    color="#d95f02",
    linewidth=2.5,
    fill=True,
    alpha=0.2,
    ax=ax
)

ax.set_title("Figure 1: Distribution of Supplier Quoted Prices vs. Engineered Should-Cost Baseline", fontsize=12, fontweight="bold", pad=12)
ax.set_xlabel("Delivered Unit Piece Price ($ USD)", fontsize=11, fontweight="semibold")
ax.set_ylabel("Probability Density", fontsize=11, fontweight="semibold")
ax.legend(frameon=True, facecolor="white", loc="upper right")
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
chart1_path = os.path.join(FIGURES_DIR, "fig1_quote_vs_should_cost_distribution.png")
plt.savefig(chart1_path, dpi=300)
plt.close()
print(f"Saved: {chart1_path}")

# -----------------------------------------------------------------------------
# CHART 2: Commodity Benchmark Indices (24-Month Trend)
# -----------------------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(10, 5.5))
df_commodity["record_date"] = pd.to_datetime(df_commodity["record_date"])

ax1.plot(df_commodity["record_date"], df_commodity["lme_aluminum_usd_per_kg"], label="LME Aluminum Cash ($/kg)", color="#2b5c8f", linewidth=2.5)
ax1.plot(df_commodity["record_date"], df_commodity["polycarbonate_resin_usd_per_kg"], label="Polycarbonate Resin ($/kg)", color="#7570b3", linewidth=2.0, linestyle="--")
ax1.plot(df_commodity["record_date"], df_commodity["crca_steel_usd_per_kg"], label="CRCA Steel Sheet ($/kg)", color="#666666", linewidth=1.8, linestyle=":")

ax1.set_title("Figure 2: 24-Month Raw Material Commodity Volatility Benchmark (2024–2025)", fontsize=12, fontweight="bold", pad=12)
ax1.set_xlabel("Time Horizon (Monthly Index)", fontsize=11, fontweight="semibold")
ax1.set_ylabel("Commodity Benchmark Price ($/kg)", fontsize=11, fontweight="semibold")
ax1.legend(frameon=True, facecolor="white", loc="upper left")
ax1.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
chart2_path = os.path.join(FIGURES_DIR, "fig2_commodity_correlation_matrix.png")
plt.savefig(chart2_path, dpi=300)
plt.close()
print(f"Saved: {chart2_path}")

# -----------------------------------------------------------------------------
# CHART 3: Supplier Margin Variance Scatter Matrix
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6))

scatter = sns.scatterplot(
    data=df_variance,
    x="engineered_should_cost_usd",
    y="pricing_variance_pct",
    hue="supplier_name",
    size="annual_projected_volume",
    sizes=(60, 400),
    alpha=0.85,
    edgecolor="black",
    linewidth=0.8,
    ax=ax
)

ax.axhline(0, color="green", linestyle="-", linewidth=1.5, label="Target Should-Cost (0% Variance)")
ax.axhline(15, color="red", linestyle="--", linewidth=1.2, label="High Markup Threshold (+15%)")
ax.axhline(-5, color="orange", linestyle=":", linewidth=1.2, label="Dumping / Quality Risk Threshold (-5%)")

ax.set_title("Figure 3: Supplier Pricing Variance vs. Engineered Baseline Across Luminaire Portfolio", fontsize=12, fontweight="bold", pad=12)
ax.set_xlabel("Engineered Should-Cost ($ USD)", fontsize=11, fontweight="semibold")
ax.set_ylabel("Pricing Variance % (Quoted vs. Should-Cost)", fontsize=11, fontweight="semibold")
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0, fontsize=8.5)
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
chart3_path = os.path.join(FIGURES_DIR, "fig3_supplier_margin_variance_scatter.png")
plt.savefig(chart3_path, dpi=300)
plt.close()
print(f"Saved: {chart3_path}")

# -----------------------------------------------------------------------------
# CHART 4: Flagship Luminaire Housing (StreetStar ADC12) Cost Teardown
# -----------------------------------------------------------------------------
flagship_part = df_should_cost[df_should_cost["part_id"] == "PRT-STR-01"].iloc[0]

cost_elements = [
    ("Net Raw Aluminum", flagship_part["net_material_cost_usd"]),
    ("Machine Processing (650T HPDC)", flagship_part["machine_processing_cost_usd"]),
    ("Direct Labor", flagship_part["direct_labor_cost_usd"]),
    ("Shot Blast + Powder Coat", flagship_part["secondary_finish_cost_usd"]),
    ("SG&A Overhead (8%)", flagship_part["sga_overhead_usd"]),
    ("Fair Supplier Margin (10%)", flagship_part["fair_supplier_margin_usd"]),
]

labels, values = zip(*cost_elements)
colors = ["#2b5c8f", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02"]

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(labels, values, color=colors, edgecolor="black", height=0.6)

ax.set_title(f"Figure 4: Bottom-Up Should-Cost Teardown: {flagship_part['part_description']}\n(Total Engineered Cost: ${flagship_part['engineered_should_cost_usd']:.2f})", fontsize=12, fontweight="bold", pad=12)
ax.set_xlabel("Cost Contribution ($ USD per Piece)", fontsize=11, fontweight="semibold")
ax.grid(True, axis="x", linestyle="--", alpha=0.5)

for bar in bars:
    w = bar.get_width()
    pct = (w / flagship_part["engineered_should_cost_usd"]) * 100
    ax.annotate(f"${w:.2f} ({pct:.1f}%)", (w + 0.15, bar.get_y() + bar.get_height()/2),
                va="center", fontsize=9, fontweight="bold")

plt.tight_layout()
chart4_path = os.path.join(FIGURES_DIR, "fig4_luminaire_cost_breakdown_waterfall.png")
plt.savefig(chart4_path, dpi=300)
plt.close()
print(f"Saved: {chart4_path}")

# -----------------------------------------------------------------------------
# CHART 5: LME Aluminum Sensitivity & Spend at Risk
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))

x_shifts = df_sensitivity["LME_Aluminum_Shift_Pct"]
y_spend = df_sensitivity["Total_Adjusted_Procurement_Spend_USD"] / 1e6 # $ Millions

bars = ax.bar(x_shifts, y_spend, color="#1f77b4", edgecolor="black", width=0.55)

# Highlight base case
base_idx = list(x_shifts).index("+0%") if "+0%" in list(x_shifts) else 3
bars[base_idx].set_color("#2ca02c")
bars[base_idx].set_edgecolor("black")

ax.set_title("Figure 5: Signify Direct Aluminum Portfolio Spend Sensitivity (±15% LME Shock)", fontsize=12, fontweight="bold", pad=12)
ax.set_xlabel("LME Aluminum Price Shock (%)", fontsize=11, fontweight="semibold")
ax.set_ylabel("Total Aluminum Portfolio Spend ($ Millions USD)", fontsize=11, fontweight="semibold")
ax.grid(True, axis="y", linestyle="--", alpha=0.5)

for bar in bars:
    h = bar.get_height()
    ax.annotate(f"${h:.2f}M", (bar.get_x() + bar.get_width()/2, h + 0.05),
                ha="center", fontsize=9, fontweight="bold")

plt.tight_layout()
chart5_path = os.path.join(FIGURES_DIR, "fig5_lme_price_passthrough_sensitivity.png")
plt.savefig(chart5_path, dpi=300)
plt.close()
print(f"Saved: {chart5_path}")

print("All Strategic Sourcing Seaborn charts generated successfully.")
