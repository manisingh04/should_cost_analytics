-- ====================================================================
-- Signify Strategic Sourcing - Advanced Procurement SQL Queries
-- Focus: Should-Cost Teardown, Commodity Volatility & Vendor Arbitrage
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Supplier Price Creep & Quote Trend Analysis (Window Functions)
-- Evaluates whether suppliers dropped their quotes when raw aluminum dropped.
-- --------------------------------------------------------------------
WITH QuoteHistoryWithCommodity AS (
    SELECT 
        sq.quote_id,
        sq.part_id,
        p.part_description,
        p.material_alloy,
        sq.supplier_id,
        s.supplier_name,
        sq.quote_date,
        sq.quoted_piece_price_usd,
        c.lme_aluminum_usd_per_kg,
        -- Window function: Previous quote price for this part from same supplier
        LAG(sq.quoted_piece_price_usd, 1) OVER (
            PARTITION BY sq.part_id, sq.supplier_id 
            ORDER BY sq.quote_date
        ) AS prev_quote_price,
        -- Window function: Previous LME price at that quote date
        LAG(c.lme_aluminum_usd_per_kg, 1) OVER (
            PARTITION BY sq.part_id, sq.supplier_id 
            ORDER BY sq.quote_date
        ) AS prev_lme_price
    FROM supplier_quotes sq
    JOIN parts_manufacturing_specs p ON sq.part_id = p.part_id
    JOIN suppliers_procurement s ON sq.supplier_id = s.supplier_id
    LEFT JOIN lme_commodity_history c ON strftime('%Y-%m', sq.quote_date) = strftime('%Y-%m', c.record_date)
)
SELECT 
    quote_id,
    part_id,
    part_description,
    supplier_name,
    quote_date,
    quoted_piece_price_usd,
    prev_quote_price,
    ROUND(quoted_piece_price_usd - prev_quote_price, 2) AS price_delta_usd,
    ROUND(((quoted_piece_price_usd - prev_quote_price) / prev_quote_price) * 100, 2) AS price_change_pct,
    lme_aluminum_usd_per_kg AS current_lme,
    ROUND(((lme_aluminum_usd_per_kg - prev_lme_price) / prev_lme_price) * 100, 2) AS lme_change_pct,
    CASE 
        WHEN ((lme_aluminum_usd_per_kg - prev_lme_price) < 0) AND ((quoted_piece_price_usd - prev_quote_price) >= 0)
        THEN 'PRICE GOUGING: LME fell but quote rose/stayed flat'
        WHEN ((quoted_piece_price_usd - prev_quote_price) / prev_quote_price) > 1.2 * ((lme_aluminum_usd_per_kg - prev_lme_price) / prev_lme_price)
        THEN 'DISPROPORTIONATE HIKE: Quote increased faster than LME'
        ELSE 'INDEX ALIGNED: Fair commodity pass-through'
    END AS negotiation_flag
FROM QuoteHistoryWithCommodity
WHERE prev_quote_price IS NOT NULL
ORDER BY price_change_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 2: Competitive Quote Spread by Component & Cost Variance
-- Identifies parts with large price differences across multiple bidders.
-- --------------------------------------------------------------------
SELECT 
    p.part_id,
    p.part_description,
    p.luminaire_platform,
    p.material_alloy,
    p.net_finished_weight_kg,
    COUNT(sq.supplier_id) AS total_bidders,
    MIN(sq.quoted_piece_price_usd) AS lowest_bid_usd,
    MAX(sq.quoted_piece_price_usd) AS highest_bid_usd,
    ROUND(AVG(sq.quoted_piece_price_usd), 2) AS avg_bid_usd,
    ROUND(MAX(sq.quoted_piece_price_usd) - MIN(sq.quoted_piece_price_usd), 2) AS bid_spread_usd,
    ROUND(((MAX(sq.quoted_piece_price_usd) - MIN(sq.quoted_piece_price_usd)) / MIN(sq.quoted_piece_price_usd)) * 100, 1) AS bid_spread_pct,
    p.annual_projected_volume,
    ROUND((MAX(sq.quoted_piece_price_usd) - MIN(sq.quoted_piece_price_usd)) * p.annual_projected_volume, 2) AS annual_arbitrage_opportunity_usd
FROM parts_manufacturing_specs p
JOIN supplier_quotes sq ON p.part_id = sq.part_id
GROUP BY p.part_id, p.part_description, p.luminaire_platform, p.material_alloy, p.net_finished_weight_kg, p.annual_projected_volume
HAVING COUNT(sq.supplier_id) >= 2
ORDER BY annual_arbitrage_opportunity_usd DESC;


-- --------------------------------------------------------------------
-- QUERY 3: Supplier Portfolio Exposure to Raw Material Categories
-- Breaks down total allocated spend across alloys to assess commodity risk.
-- --------------------------------------------------------------------
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.country,
    s.core_manufacturing_capability,
    COUNT(DISTINCT p.part_id) AS parts_supplied_count,
    ROUND(SUM(p.net_finished_weight_kg * p.annual_projected_volume), 1) AS total_annual_finished_metal_kg,
    ROUND(SUM(p.gross_shot_weight_kg * p.annual_projected_volume), 1) AS total_annual_gross_metal_kg,
    ROUND(SUM((p.gross_shot_weight_kg - p.net_finished_weight_kg) * p.annual_projected_volume), 1) AS total_annual_process_scrap_kg,
    ROUND(SUM(sq.quoted_piece_price_usd * p.annual_projected_volume), 2) AS total_annual_spend_usd
FROM suppliers_procurement s
JOIN supplier_quotes sq ON s.supplier_id = sq.supplier_id
JOIN parts_manufacturing_specs p ON sq.part_id = p.part_id
WHERE sq.award_status IN ('Awarded', 'Benchmark')
GROUP BY s.supplier_id, s.supplier_name, s.country, s.core_manufacturing_capability
ORDER BY total_annual_spend_usd DESC;
