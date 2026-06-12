{{ config(materialized="table") }}
SELECT
    DATE(scraped_at) AS date,
    source,
    category,
    ROUND(AVG(price), 2) AS daily_avg_price
FROM {{ ref('prices_cleaned') }}
GROUP BY 1, 2, 3