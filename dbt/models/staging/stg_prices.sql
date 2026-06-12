{{ config(materialized="view") }}
SELECT
    MD5(CONCAT(COALESCE(product_name, ''), COALESCE(source, ''))) AS product_id,
    TRIM(product_name)                              AS name,
    CAST(price AS FLOAT64)                          AS price,
    CAST(old_price AS FLOAT64)                      AS old_price,
    CAST(discount_pct AS FLOAT64)                   AS discount_pct,
    CAST(rating AS FLOAT64)                         AS rating,
    COALESCE(currency, 'MAD')                       AS currency,
    COALESCE(category, '')                          AS category,
    source,
    SAFE_CAST(scraped_at AS TIMESTAMP)              AS scraped_at,
    CAST(image_url AS STRING)                       AS image_url,
    CAST(url AS STRING)                             AS url
FROM {{ source('price_intelligence_dbt', 'prices_raw') }}
