{{ config(materialized="table") }}
SELECT
    source,
    category,
    ROUND(STDDEV(price), 2) AS price_stddev,
    ROUND(AVG(price), 2) AS mean_price,
    ROUND(STDDEV(price) / NULLIF(AVG(price), 0), 4) AS volatility_index,
    MAX(price) - MIN(price) AS price_range
FROM {{ ref('prices_cleaned') }}
GROUP BY 1, 2