# Price Intelligence Platform

This project is a world-class, academic Fullstack application for e-commerce price monitoring in Morocco, built with FastAPI and Angular 17. 
This project serves as the presentation layer for a complete Data Engineering pipeline (Scrapy → Apache NiFi → Google Bigtable → Apache Airflow → dbt → Google BigQuery).

Supervised by: **Prof. ELAACHAK** (FSTT Tanger - Universite Abdelmalek Essaadi)

## Core Market Verticals

The platform is strictly optimized for 5 key market segments in Morocco:
- **Informatique**: Laptops, components, and enterprise networking hardware.
- **Smartphones**: Mobile devices and smart wearables.
- **Tablets**: iPads and Android tablets.
- **TVs**: Smart TVs and home cinema displays.
- **Electromenager**: Household appliances and high-tech consumer electronics.

## Strategic Analytical Layers

The application provides a deep-dive into market dynamics across three distinct layers:

### 1. Descriptive Performance Metrics
- **Pricing Index**: Weighted average market prices in MAD across Jumia, Avito, and Connecto.
- **Market Concentration**: Relative inventory share across retailers.
- **Volatility Analysis**: Coefficient of variation tracking price instability.

### 2. Inferential Statistical Modeling
- **Retailer Comparison**: T-Tests and Mann-Whitney U tests comparing price distributions between retailers.
- **ANOVA**: Analysis of variance across sources and product categories to detect market significance.
- **Confidence Intervals**: 95% CI modeling for true market price means.
- **Statistical Power**: Computing the reliability of detected market variances.

### 3. Multivariate Regression (Predictive)
- **Model Fit (R-Squared)**: Gauging the predictive power of discounts and ratings on market prices.
- **OLS Regression**: Multivariate model predicting price behavior based on discount depth, user ratings, and temporal factors.
- **Residual Analysis**: Error distribution tracking for model validation.

## Architecture Overview

- **`api/`**: FastAPI Backend (Connected to Google BigQuery via SciPy & Statsmodels).
- **`frontend/`**: Angular 17 Frontend (Premium Glassmorphism UI with Plotly.js).
- **`docker-compose.yml`**: Production Docker deployment orchestration.

## Prerequisites

- Docker and Docker Compose
- Google Cloud BigQuery credentials (`api/credentials.json`)

## Quickstart Deployment (Docker)

1. Ensure your BigQuery service account credentials are saved at `api/credentials.json`.
2. Start the entire application:
```bash
docker-compose up --build
```
3. The platform will automatically launch:
   - **Frontend UI**: [http://localhost:4200](http://localhost:4200)
   - **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Key API Endpoints

- `GET /prices` - List active products within target verticals.
- `GET /prices/stats` - High-level market metrics.
- `GET /prices/alerts` - Strategic price drops > 10%.
- `GET /prices/regression` - Multivariate OLS model summary.
- `GET /prices/trends` - Price evolution by retailer & category.
- `GET /prices/velocity` - Calculation of price drop speed (MAD/hr).
