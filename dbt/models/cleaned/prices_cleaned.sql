{{ config(materialized="table") }}
SELECT
    product_id,
    name,
    price,
    old_price,
    discount_pct,
    rating,
    currency,
    category,
    source,
    scraped_at,
    image_url,
    url
FROM (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY scraped_at DESC) AS rn
    FROM {{ ref('stg_prices') }}
    WHERE price > 0 AND name IS NOT NULL AND product_id IS NOT NULL
)
WHERE rn = 1
