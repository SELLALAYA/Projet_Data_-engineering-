{{ config(materialized="table") }}

SELECT
    source,
    category,
    COUNT(*)                    AS total_products,
    ROUND(AVG(price), 2)        AS avg_price,
    ROUND(MIN(price), 2)        AS min_price,
    ROUND(MAX(price), 2)        AS max_price,
    ROUND(AVG(discount_pct), 2) AS avg_discount,
    ROUND(AVG(rating), 2)       AS avg_rating,
    DATE(MAX(scraped_at))       AS last_scraped_date
FROM {{ ref('prices_cleaned') }}
GROUP BY source, category
