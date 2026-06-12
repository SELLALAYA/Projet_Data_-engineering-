{{ config(materialized="table") }}
SELECT
    source,
    category,
    COUNT(*) AS volume,
    ROUND(AVG(price), 2) AS avg_price,
    ROUND(PERCENTILE_CONT(price, 0.5) OVER(PARTITION BY source, category), 2) AS median_price
FROM {{ ref('prices_cleaned') }}
GROUP BY 1, 2, price