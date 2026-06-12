# Price Intelligence API

FastAPI backend powered by Google BigQuery, SciPy, and Statsmodels.

## Features
- **Virtual Category Engine**: Robust SQL-based mapping of raw market data into 5 strategic verticals (Informatique, Smartphones, Tablets, TVs, Electromenager).
- **Titanium Shield v2**: Advanced regex-based filtering system to remove "junk" data and ensure high-fidelity electronics tracking.
- **Statistical Engine**: Full suite of inferential tests (T-Test, ANOVA, Mann-Whitney) and confidence interval modeling.
- **Predictive Analytics**: Multivariate OLS regression for price behavior analysis.
- **Data Velocity**: Real-time calculation of price drop speeds across retailers.

## Tech Stack
- **Framework**: FastAPI
- **Database**: Google BigQuery (via `google-cloud-bigquery`)
- **Processing**: Pandas, NumPy
- **Statistics**: SciPy, Statsmodels, Pingouin

## Setup
1. Place `credentials.json` in this directory.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the server:
```bash
python main.py
```
Access documentation at `http://localhost:8000/docs`.
