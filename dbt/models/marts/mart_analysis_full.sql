{{ config(materialized="table") }}
SELECT
    product_id,
    name,
    category,
    source,
    price,
    discount_pct,
    rating,
    -- Préparation pour l'analyse de régression
    CASE WHEN source = 'amazon.com' THEN 1 ELSE 0 END AS is_amazon,
    CASE WHEN source = 'jumia.ma' THEN 1 ELSE 0 END AS is_jumia
FROM {{ ref('prices_cleaned') }}
WHERE price IS NOT NULL AND discount_pct IS NOT NULL