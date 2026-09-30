-- ====================================================================
-- Signify Luminaire Strategic Sourcing & Should-Cost Database Schema
-- Focus: Direct Procurement, Parametric Costing, LME Indexation
-- ====================================================================

DROP TABLE IF EXISTS supplier_quotes;
DROP TABLE IF EXISTS lme_commodity_history;
DROP TABLE IF EXISTS parts_manufacturing_specs;
DROP TABLE IF EXISTS suppliers_procurement;

-- 1. Suppliers Procurement Master
CREATE TABLE suppliers_procurement (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    state_region VARCHAR(50) NOT NULL,
    core_manufacturing_capability VARCHAR(50) NOT NULL, -- 'High Pressure Die Casting', 'Aluminum Extrusion', 'Precision Sheet Metal', 'Plastic Injection'
    supplier_tier VARCHAR(10) NOT NULL, -- 'Tier 1', 'Tier 2'
    annual_spend_allocated_usd DECIMAL(12, 2) NOT NULL,
    esg_sustainability_rating DECIMAL(4, 2) NOT NULL -- Scale 0 to 10
);

-- 2. Parts Detailed Manufacturing Specifications (Engineering Parameters)
CREATE TABLE parts_manufacturing_specs (
    part_id VARCHAR(20) PRIMARY KEY,
    part_description VARCHAR(150) NOT NULL,
    luminaire_platform VARCHAR(50) NOT NULL, -- 'Road & Street', 'Industrial HighBay', 'Office Troffer', 'Architectural'
    material_alloy VARCHAR(50) NOT NULL, -- 'Aluminum ADC12', 'Aluminum 6063-T6', 'CRCA Steel', 'Polycarbonate Optical Grade'
    net_finished_weight_kg DECIMAL(8, 3) NOT NULL,
    gross_shot_weight_kg DECIMAL(8, 3) NOT NULL, -- Total metal poured (includes runners/flash)
    manufacturing_process VARCHAR(50) NOT NULL, -- 'HPDC', 'Extrusion', 'Sheet Metal Stamping', 'Injection Molding'
    machine_clamping_tonnage INT NOT NULL, -- e.g. 250, 400, 650, 800 Ton press
    cycle_time_seconds DECIMAL(6, 1) NOT NULL,
    tooling_cavities INT NOT NULL, -- 1, 2, or 4 cavity mold
    secondary_finish VARCHAR(80) NOT NULL, -- 'Shot Blasting + Powder Coating', 'Chemical Anodizing', 'Electrostatic Painting', 'None'
    annual_projected_volume INT NOT NULL
);

-- 3. Historical Commodity Benchmark Indices (Monthly)
CREATE TABLE lme_commodity_history (
    record_date DATE PRIMARY KEY,
    lme_aluminum_usd_per_kg DECIMAL(6, 3) NOT NULL,
    lme_copper_usd_per_kg DECIMAL(6, 3) NOT NULL,
    crca_steel_usd_per_kg DECIMAL(6, 3) NOT NULL,
    polycarbonate_resin_usd_per_kg DECIMAL(6, 3) NOT NULL
);

-- 4. Supplier Historical Quotations & Negotiations
CREATE TABLE supplier_quotes (
    quote_id VARCHAR(25) PRIMARY KEY,
    part_id VARCHAR(20) NOT NULL,
    supplier_id VARCHAR(20) NOT NULL,
    quote_date DATE NOT NULL,
    quoted_piece_price_usd DECIMAL(10, 2) NOT NULL,
    tooling_amortization_per_unit_usd DECIMAL(6, 2) DEFAULT 0.00,
    packaging_freight_per_unit_usd DECIMAL(6, 2) NOT NULL,
    total_delivered_quote_usd DECIMAL(10, 2) NOT NULL,
    minimum_order_quantity INT NOT NULL,
    validity_period_months INT DEFAULT 12,
    award_status VARCHAR(20) NOT NULL, -- 'Awarded', 'Rejected', 'Under Negotiation', 'Benchmark'
    FOREIGN KEY (part_id) REFERENCES parts_manufacturing_specs(part_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers_procurement(supplier_id)
);

CREATE INDEX idx_sq_part ON supplier_quotes(part_id);
CREATE INDEX idx_sq_supplier ON supplier_quotes(supplier_id);
CREATE INDEX idx_sq_date ON supplier_quotes(quote_date);
