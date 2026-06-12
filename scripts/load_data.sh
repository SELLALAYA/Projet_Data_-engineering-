#!/bin/bash
docker cp /opt/airflow/data/processed/all_products.csv price_postgres:/tmp/all_products.csv
psql -U airflow -d airflow -c "\COPY products_raw FROM '/tmp/all_products.csv' CSV HEADER;"