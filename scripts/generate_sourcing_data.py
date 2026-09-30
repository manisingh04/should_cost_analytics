"""
Signify Strategic Sourcing - Realistic Procurement & Sourcing Data Generator
Generates parts manufacturing parameters, LME commodity history, supplier master,
and historical RFQ quotations. Populates SQLite DB and exports CSVs.
"""

import os
import sqlite3
import random
import datetime
import pandas as pd
import numpy as np

random.seed(101)
np.random.seed(101)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "database", "signify_sourcing.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Suppliers Procurement Master
# -----------------------------------------------------------------------------
suppliers_data = [
    ("VND-MEC-01", "Bharat Precision Die-Casting", "India", "Maharashtra (Pune)", "High Pressure Die Casting", "Tier 1", 1850000.0, 9.1),
    ("VND-MEC-02", "Apex Light Alloy Foundries", "India", "Tamil Nadu (Coimbatore)", "High Pressure Die Casting", "Tier 1", 1420000.0, 8.8),
    ("VND-MEC-03", "Ningbo SuperCast Technology", "China", "Zhejiang (Ningbo)", "High Pressure Die Casting", "Tier 2", 2100000.0, 7.3),
    ("VND-EXT-01", "Gujarat Extrusions & Profiles", "India", "Gujarat (Vadodara)", "Aluminum Extrusion", "Tier 1", 1650000.0, 9.3),
    ("VND-EXT-02", "EuroProfile Aluminium GmbH", "Germany", "Baden-Württemberg", "Aluminum Extrusion", "Tier 1", 950000.0, 9.6),
    ("VND-EXT-03", "Mekong Delta Extrusions", "Vietnam", "Binh Duong", "Aluminum Extrusion", "Tier 2", 820000.0, 8.1),
    ("VND-STP-01", "Capital Stamping & Sheet Metal", "India", "Haryana (Faridabad)", "Precision Sheet Metal", "Tier 1", 1250000.0, 8.9),
    ("VND-STP-02", "Southern Press Tools & Parts", "India", "Tamil Nadu (Chennai)", "Precision Sheet Metal", "Tier 2", 740000.0, 8.4),
    ("VND-INJ-01", "PolyPlast Precision Optics", "India", "Karnataka (Bangalore)", "Plastic Injection", "Tier 1", 920000.0, 9.0),
    ("VND-INJ-02", "Dongguan ClearTech Molding", "China", "Guangdong (Dongguan)", "Plastic Injection", "Tier 2", 680000.0, 7.6),
]

df_suppliers = pd.DataFrame(suppliers_data, columns=[
    "supplier_id", "supplier_name", "country", "state_region",
    "core_manufacturing_capability", "supplier_tier", "annual_spend_allocated_usd", "esg_sustainability_rating"
])

# -----------------------------------------------------------------------------
# 2. Parts Detailed Manufacturing Specifications (40 Luminaire Parts)
# -----------------------------------------------------------------------------
# Columns: part_id, part_description, luminaire_platform, material_alloy,
# net_finished_weight_kg, gross_shot_weight_kg, manufacturing_process,
# machine_clamping_tonnage, cycle_time_seconds, tooling_cavities, secondary_finish, annual_projected_volume

parts_spec_data = [
    # Road & Street (ADC12 Die-Casting & Sheet Metal)
    ("PRT-STR-01", "StreetStar 150W Die-Cast Main Housing", "Road & Street", "Aluminum ADC12", 4.150, 5.100, "HPDC", 650, 48.0, 1, "Shot Blasting + Powder Coating", 25000),
    ("PRT-STR-02", "StreetStar Top Access Maintenance Canopy", "Road & Street", "Aluminum ADC12", 1.850, 2.300, "HPDC", 400, 36.0, 1, "Shot Blasting + Powder Coating", 25000),
    ("PRT-STR-03", "Adjustable Tenon Mast Arm Spigot Adapter", "Road & Street", "Aluminum ADC12", 1.250, 1.550, "HPDC", 350, 32.0, 2, "Shot Blasting + Powder Coating", 30000),
    ("PRT-STR-04", "Galvanized Steel Mast Clamp Bracket", "Road & Street", "CRCA Steel", 0.950, 1.150, "Sheet Metal Stamping", 200, 14.0, 1, "Electrostatic Painting", 35000),
    ("PRT-STR-05", "Optical Polycarbonate Road Lens Plate", "Road & Street", "Polycarbonate Optical Grade", 0.320, 0.410, "Injection Molding", 180, 28.0, 4, "None", 40000),
    ("PRT-STR-06", "Internal Gear Tray Stamped Galvanized Base", "Road & Street", "CRCA Steel", 0.780, 0.920, "Sheet Metal Stamping", 160, 12.0, 1, "None", 28000),
    ("PRT-STR-07", "Roadway Luminaire Hinge Latch Assembly", "Road & Street", "Aluminum ADC12", 0.280, 0.390, "HPDC", 150, 22.0, 4, "Shot Blasting + Powder Coating", 50000),
    ("PRT-STR-08", "Surge Protector Retaining Saddle Clamp", "Road & Street", "CRCA Steel", 0.120, 0.150, "Sheet Metal Stamping", 80, 8.0, 2, "None", 30000),
    ("PRT-STR-09", "Streetlight Exterior Protective Visor Frame", "Road & Street", "Aluminum ADC12", 0.850, 1.100, "HPDC", 250, 26.0, 2, "Shot Blasting + Powder Coating", 20000),
    ("PRT-STR-10", "Tenon Angle Calibration Dial Plate", "Road & Street", "Aluminum ADC12", 0.180, 0.250, "HPDC", 100, 18.0, 4, "Shot Blasting + Powder Coating", 30000),

    # Industrial HighBay (Extruded 6063 Aluminum & Die-Casting)
    ("PRT-HBY-01", "CoreLine Finned Thermal Heatsink 200W", "Industrial HighBay", "Aluminum 6063-T6", 4.850, 5.250, "Extrusion", 800, 65.0, 1, "Chemical Anodizing", 18000),
    ("PRT-HBY-02", "HighBay Central Electrical Gear Enclosure", "Industrial HighBay", "Aluminum ADC12", 1.650, 2.100, "HPDC", 400, 34.0, 1, "Shot Blasting + Powder Coating", 20000),
    ("PRT-HBY-03", "IP65 Sealed Cable Gland Entry Flange", "Industrial HighBay", "Aluminum ADC12", 0.340, 0.450, "HPDC", 150, 20.0, 2, "Shot Blasting + Powder Coating", 22000),
    ("PRT-HBY-04", "Spun Anodized Aluminum 90-Deg Reflector", "Industrial HighBay", "Aluminum 6063-T6", 0.620, 0.780, "Extrusion", 250, 25.0, 1, "Chemical Anodizing", 15000),
    ("PRT-HBY-05", "Suspension Hook Attachment Yoke Bracket", "Industrial HighBay", "CRCA Steel", 0.550, 0.680, "Sheet Metal Stamping", 150, 11.0, 1, "Electrostatic Painting", 25000),
    ("PRT-HBY-06", "Polycarbonate High-Impact Protective Bell", "Industrial HighBay", "Polycarbonate Optical Grade", 0.480, 0.590, "Injection Molding", 220, 32.0, 2, "None", 18000),
    ("PRT-HBY-07", "Auxiliary Emergency Battery Cradle Bracket", "Industrial HighBay", "CRCA Steel", 0.420, 0.520, "Sheet Metal Stamping", 120, 9.0, 1, "None", 12000),
    ("PRT-HBY-08", "HighBay 100W Radial Finned Heatsink Base", "Industrial HighBay", "Aluminum 6063-T6", 2.950, 3.250, "Extrusion", 600, 48.0, 1, "Chemical Anodizing", 22000),
    ("PRT-HBY-09", "Rotatable Pipe Mount Swivel Bracket", "Industrial HighBay", "Aluminum ADC12", 0.780, 1.020, "HPDC", 250, 24.0, 2, "Shot Blasting + Powder Coating", 16000),
    ("PRT-HBY-10", "Driver Heat Dissipation Backing Plate", "Industrial HighBay", "Aluminum 6063-T6", 0.880, 0.980, "Extrusion", 300, 20.0, 1, "Chemical Anodizing", 24000),

    # Office Troffer & Cleanroom (CRCA Sheet Metal & Extruded Trim)
    ("PRT-TRF-01", "CleanSky 2x2 Deep Drawn Main Troffer Pan", "Office Troffer", "CRCA Steel", 3.200, 3.750, "Sheet Metal Stamping", 400, 18.0, 1, "Electrostatic Painting", 45000),
    ("PRT-TRF-02", "Longitudinal Snap-In Reflector Baffle", "Office Troffer", "CRCA Steel", 0.850, 1.020, "Sheet Metal Stamping", 200, 12.0, 2, "Electrostatic Painting", 90000),
    ("PRT-TRF-03", "Architectural Perimeter Extruded Trim 600mm", "Office Troffer", "Aluminum 6063-T6", 0.420, 0.480, "Extrusion", 250, 16.0, 2, "Chemical Anodizing", 60000),
    ("PRT-TRF-04", "Cleanroom Hermetic Gasket Clamp Strip", "Office Troffer", "CRCA Steel", 0.380, 0.450, "Sheet Metal Stamping", 120, 10.0, 2, "Electrostatic Painting", 35000),
    ("PRT-TRF-05", "Microprismatic Optical Diffuser Frame", "Office Troffer", "Polycarbonate Optical Grade", 0.650, 0.780, "Injection Molding", 250, 34.0, 2, "None", 45000),
    ("PRT-TRF-06", "T-Bar Ceiling Grid Mounting Clips (Set of 4)", "Office Troffer", "CRCA Steel", 0.150, 0.180, "Sheet Metal Stamping", 80, 7.0, 4, "None", 80000),
    ("PRT-TRF-07", "Removable Gear Access Cover Plate", "Office Troffer", "CRCA Steel", 0.520, 0.610, "Sheet Metal Stamping", 150, 9.0, 1, "Electrostatic Painting", 40000),
    ("PRT-TRF-08", "Recessed Flange Trim Corner Key Joints", "Office Troffer", "Aluminum ADC12", 0.085, 0.120, "HPDC", 100, 15.0, 8, "None", 120000),
    ("PRT-TRF-09", "Linear Batten Continuous Trunking Channel 1.2m", "Office Troffer", "CRCA Steel", 1.850, 2.150, "Sheet Metal Stamping", 300, 16.0, 1, "Electrostatic Painting", 30000),
    ("PRT-TRF-10", "End-Cap Snap Fit Closure with Conduit Knockout", "Office Troffer", "Polycarbonate Optical Grade", 0.075, 0.095, "Injection Molding", 120, 18.0, 4, "None", 60000),

    # Architectural & Decorative (Spun Aluminum & Precision Casting)
    ("PRT-ARC-01", "Metronomis Spun Aluminum Canopy Dome", "Architectural", "Aluminum 6063-T6", 2.450, 2.850, "Extrusion", 500, 45.0, 1, "Chemical Anodizing", 8000),
    ("PRT-ARC-02", "UrbanPark Fluted Column Base Cast Skirt", "Architectural", "Aluminum ADC12", 3.100, 3.850, "HPDC", 600, 42.0, 1, "Shot Blasting + Powder Coating", 9000),
    ("PRT-ARC-03", "Curved Swan-Neck Wall Bracket Arm", "Architectural", "Aluminum ADC12", 1.950, 2.450, "HPDC", 400, 38.0, 1, "Shot Blasting + Powder Coating", 11000),
    ("PRT-ARC-04", "Vandal-Resistant Cylindrical Polycarbonate Globe", "Architectural", "Polycarbonate Optical Grade", 1.350, 1.620, "Injection Molding", 350, 48.0, 1, "None", 10000),
    ("PRT-ARC-05", "Decorative Finial Top Crown Spire", "Architectural", "Aluminum ADC12", 0.450, 0.620, "HPDC", 180, 24.0, 2, "Shot Blasting + Powder Coating", 12000),
    ("PRT-ARC-06", "Internal Optical Louver Ring Shield", "Architectural", "Aluminum 6063-T6", 0.380, 0.440, "Extrusion", 200, 18.0, 2, "Chemical Anodizing", 14000),
    ("PRT-ARC-07", "Heavy-Duty Ground Anchor Base Flange", "Architectural", "CRCA Steel", 2.800, 3.250, "Sheet Metal Stamping", 400, 18.0, 1, "Electrostatic Painting", 12000),
    ("PRT-ARC-08", "Twin Luminaire Cross-Arm Header Beam", "Architectural", "Aluminum 6063-T6", 2.650, 2.950, "Extrusion", 500, 38.0, 1, "Chemical Anodizing", 6000),
    ("PRT-ARC-09", "Pole Access Door Flush Service Hatch", "Architectural", "Aluminum ADC12", 0.520, 0.680, "HPDC", 200, 22.0, 2, "Shot Blasting + Powder Coating", 15000),
    ("PRT-ARC-10", "Anti-Glare Frosted Ring Acrylic Diffuser", "Architectural", "Polycarbonate Optical Grade", 0.280, 0.340, "Injection Molding", 180, 26.0, 4, "None", 18000),
]

df_parts = pd.DataFrame(parts_spec_data, columns=[
    "part_id", "part_description", "luminaire_platform", "material_alloy",
    "net_finished_weight_kg", "gross_shot_weight_kg", "manufacturing_process",
    "machine_clamping_tonnage", "cycle_time_seconds", "tooling_cavities",
    "secondary_finish", "annual_projected_volume"
])

# -----------------------------------------------------------------------------
# 3. LME Commodity History (24 Months: Jan 2024 to Dec 2025)
# -----------------------------------------------------------------------------
dates = pd.date_range(start="2024-01-01", end="2025-12-01", freq="MS")

# Simulated realistic commodity cycle
# Aluminum starts ~2.20 $/kg, peaks at 2.65 $/kg in early 2025, settles ~2.35 $/kg
t = np.linspace(0, 2 * np.pi, len(dates))
al_prices = 2.30 + 0.25 * np.sin(t) + np.random.normal(0, 0.04, len(dates))
cu_prices = 8.50 + 0.80 * np.sin(t + 0.5) + np.random.normal(0, 0.12, len(dates))
steel_prices = 0.95 + 0.12 * np.sin(t - 0.3) + np.random.normal(0, 0.02, len(dates))
resin_prices = 2.75 + 0.30 * np.sin(t + 0.2) + np.random.normal(0, 0.05, len(dates))

commodity_records = []
for i, d in enumerate(dates):
    commodity_records.append((
        d.strftime("%Y-%m-%d"),
        round(float(al_prices[i]), 3),
        round(float(cu_prices[i]), 3),
        round(float(steel_prices[i]), 3),
        round(float(resin_prices[i]), 3)
    ))

df_commodity = pd.DataFrame(commodity_records, columns=[
    "record_date", "lme_aluminum_usd_per_kg", "lme_copper_usd_per_kg",
    "crca_steel_usd_per_kg", "polycarbonate_resin_usd_per_kg"
])

# -----------------------------------------------------------------------------
# 4. Supplier RFQ Quotations History (~480 quotes)
# -----------------------------------------------------------------------------
# Each part has 2 to 3 suppliers quoting across 4 RFQ cycles in 2024-2025
quotes_records = []
quote_id_num = 20001

# Capable suppliers by process
process_supplier_map = {
    "HPDC": ["VND-MEC-01", "VND-MEC-02", "VND-MEC-03"],
    "Extrusion": ["VND-EXT-01", "VND-EXT-02", "VND-EXT-03"],
    "Sheet Metal Stamping": ["VND-STP-01", "VND-STP-02"],
    "Injection Molding": ["VND-INJ-01", "VND-INJ-02"]
}

rfq_dates = [
    datetime.date(2024, 2, 15),
    datetime.date(2024, 8, 20),
    datetime.date(2025, 2, 10),
    datetime.date(2025, 9, 15),
]

commodity_dict = df_commodity.set_index("record_date").to_dict("index")

for _, p in df_parts.iterrows():
    p_id = p["part_id"]
    proc = p["manufacturing_process"]
    mat = p["material_alloy"]
    net_wt = p["net_finished_weight_kg"]
    gross_wt = p["gross_shot_weight_kg"]
    cycle = p["cycle_time_seconds"]
    tonnage = p["machine_clamping_tonnage"]
    cav = p["tooling_cavities"]
    vol = p["annual_projected_volume"]
    
    capable_sups = process_supplier_map[proc]
    
    for rfq_d in rfq_dates:
        # Match nearest commodity price
        d_str = rfq_d.strftime("%Y-%m-01")
        comm_row = commodity_dict.get(d_str, commodity_dict["2024-02-01"])
        
        if "Aluminum" in mat:
            mat_benchmark = comm_row["lme_aluminum_usd_per_kg"]
        elif "Steel" in mat:
            mat_benchmark = comm_row["crca_steel_usd_per_kg"]
        else:
            mat_benchmark = comm_row["polycarbonate_resin_usd_per_kg"]
            
        # Theoretical baseline cost
        mat_cost = (gross_wt * mat_benchmark) - ((gross_wt - net_wt) * mat_benchmark * 0.65)
        
        # Machine rate by tonnage
        if tonnage <= 200:
            m_rate = 32.0 # $/hr
        elif tonnage <= 400:
            m_rate = 48.0
        elif tonnage <= 650:
            m_rate = 72.0
        else:
            m_rate = 98.0
            
        cycle_cost = (cycle / (3600.0 * cav)) * m_rate
        finish_cost = 0.45 * net_wt if p["secondary_finish"] != "None" else 0.0
        baseline_mfg = mat_cost + cycle_cost + finish_cost
        should_cost_base = baseline_mfg * 1.20 # 8% SG&A + 12% margin
        
        for sup_id in capable_sups:
            # Different supplier markup strategies
            # VND-MEC-03 & VND-EXT-02 charge premium; VND-MEC-01 is competitive; VND-MEC-02 has price creep
            if sup_id in ["VND-MEC-03", "VND-EXT-02"]:
                markup = random.uniform(1.12, 1.28) # Higher hidden margin
            elif sup_id == "VND-MEC-02" and rfq_d.year == 2025:
                markup = random.uniform(1.15, 1.25) # Price creeping up in 2025
            else:
                markup = random.uniform(0.98, 1.10) # Fair, competitive quote
                
            quoted_piece = round(should_cost_base * markup, 2)
            tooling_amort = round(random.choice([0.15, 0.25, 0.40, 0.0]), 2)
            freight = round(random.uniform(0.20, 0.65), 2)
            total_quote = round(quoted_piece + tooling_amort + freight, 2)
            
            moq = int(vol * random.uniform(0.05, 0.15))
            
            status = "Under Negotiation"
            if rfq_d == datetime.date(2025, 9, 15):
                status = "Under Negotiation"
            elif markup < 1.06:
                status = "Awarded"
            else:
                status = "Rejected"
                
            quotes_records.append((
                f"RFQ-{quote_id_num}",
                p_id,
                sup_id,
                rfq_d.strftime("%Y-%m-%d"),
                quoted_piece,
                tooling_amort,
                freight,
                total_quote,
                moq,
                12,
                status
            ))
            quote_id_num += 1

df_quotes = pd.DataFrame(quotes_records, columns=[
    "quote_id", "part_id", "supplier_id", "quote_date",
    "quoted_piece_price_usd", "tooling_amortization_per_unit_usd",
    "packaging_freight_per_unit_usd", "total_delivered_quote_usd",
    "minimum_order_quantity", "validity_period_months", "award_status"
])

# -----------------------------------------------------------------------------
# 5. Export to CSV & SQLite DB
# -----------------------------------------------------------------------------
df_suppliers.to_csv(os.path.join(DATA_DIR, "suppliers_procurement.csv"), index=False)
df_parts.to_csv(os.path.join(DATA_DIR, "parts_manufacturing_specs.csv"), index=False)
df_commodity.to_csv(os.path.join(DATA_DIR, "lme_commodity_history.csv"), index=False)
df_quotes.to_csv(os.path.join(DATA_DIR, "supplier_quotes_history.csv"), index=False)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(SCHEMA_PATH, "r") as f:
    cursor.executescript(f.read())

df_suppliers.to_sql("suppliers_procurement", conn, if_exists="append", index=False)
df_parts.to_sql("parts_manufacturing_specs", conn, if_exists="append", index=False)
df_commodity.to_sql("lme_commodity_history", conn, if_exists="append", index=False)
df_quotes.to_sql("supplier_quotes", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Strategic Sourcing & Should-Cost Data Generation Complete.")
print(f"Database created at: {DB_PATH}")
print(f"Parts count: {len(df_parts)}")
print(f"Quotes count: {len(df_quotes)}")
print(f"Commodity monthly records: {len(df_commodity)}")
