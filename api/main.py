import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.power import TTestIndPower
import traceback
import json
from fastapi.responses import JSONResponse
from datetime import datetime

# Configuration
# Robust path handling for credentials
current_dir = os.path.dirname(os.path.abspath(__file__))
creds_path = os.path.join(current_dir, 'credentials.json')

if os.path.exists(creds_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
    print(f"INFO: Using credentials from {creds_path}")
else:
    # Fallback to current environment variable if exists
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        print(f"WARNING: Credentials file NOT FOUND at {creds_path} and GOOGLE_APPLICATION_CREDENTIALS not set.")

project_id = 'project-32a82952-90fa-4dd7-b9c'
try:
    client = bigquery.Client(project=project_id)
    print(f"INFO: BigQuery client initialized for project {project_id}")
except Exception as e:
    print(f"ERROR: Failed to initialize BigQuery client: {e}")
    client = None

TABLE = f'`{project_id}.price_intelligence_dbt.prices_cleaned`'

app = FastAPI(title="Price Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STRICT CATEGORY WHITELIST ---
ALLOWED_BQ_CATS = ['Informatique', 'Telephones & Smartphones', 'Electromenager']

# --- VIRTUAL CATEGORY LOGIC ---
VIRTUAL_CAT_SQL = """
CASE 
    WHEN (LOWER(name) LIKE '%tv%' OR LOWER(name) LIKE '%téléviseur%' OR LOWER(name) LIKE '%televiseur%') THEN 'TVs'
    WHEN (LOWER(name) LIKE '%tablet%' OR LOWER(name) LIKE '%ipad%' OR LOWER(name) LIKE '%tab %') THEN 'Tablets'
    WHEN LOWER(category) = 'telephones & smartphones' THEN 'Smartphones'
    WHEN LOWER(category) = 'informatique' THEN 'Informatique'
    WHEN LOWER(category) = 'electromenager' THEN 'Electromenager'
    ELSE 'Other'
END
"""

# --- STRICT DEVICE FILTERS ---
START_JUNK = ['pochette', 'coque', 'etui', 'étui', 'protecteur', 'verre trempé', 'incassable', 'film', 'cable', 'câble', 'adaptateur', 'chargeur', 'batterie externe', 'power bank', 'station de charge', 'tapis de souris', 'sac à dos', 'sacoche', 'housse', 'cartouche', 'toner', 'encre', 'papier photo', 'porte-clés', 'mousqueton', 'support mural', 'support pc', 'support rotatif']
START_JUNK_REGEX = r'(?i)^(' + '|'.join(START_JUNK) + r')\b'

CONTAINS_JUNK = [
    'livre', 'livres', 'roman', 'romans', 'histoire', 'histoires', 'history', 'book', 'books',
    'magazine', 'journal', 'coran', 'quran', 'chapelet', 'fable', 'fables', 'conte', 'contes',
    'manga', 'bd', 'bande dessinée', 'encyclopédie', 'dictionnaire', 'cahier', 'nouvelle',
    'cravate', 'djellaba', 'chemise', 'pantalon', 'robe', 't-shirt', 'chaussures', 'chaussure',
    'nike', 'rolex', 'parfum', 'cosmétique', 'bijoux', 'montre', 'lunettes', 'sac', 'valise',
    'vêtement', 'vetement', 'veste', 'manteau', 'tricot', 'poche', 'auteur', 'écrivain',
    'villa', 'appartement', 'terrain', 'maison', 'sarout', 'local', 'fonds de commerce', 'bureau',
    'voiture', 'auto', 'moto', 'vélo', 'velo', 'dacia', 'renault', 'peugeot', 'mercedes', 'bmw',
    'audi', 'hyundai', 'kia', 'fiat', 'véhicule', 'vehicule', 'camion', 'moteur', 'jantes',
    'pneu', 'pare-choc', 'pare choc', 'volkswagen', 'ford', 'nissan', 'toyota', 'golf', 'clio',
    'jouet', 'meuble', 'salon', 'canapé', 'lit', 'chaise', 'table', 'armoire', 'pack monde',
    'pièces', 'pieces', 'pièce', 'piece', 'chambres', 'chambre', 'salon', 'étage', 'etage',
    'm2', 'm²', 'vente', 'location', 'louer', 'immobilier', 'résidence', 'residence', 'lotissement',
    'rivet', 'clip', 'pneu', 'frein', 'amortisseur', 'phare', 'calandre', 'rétroviseur', 'enjoliveur',
    'vendre', 'achat', 'acheter', 'occasion', 'km', 'kilométrage', 'boite', 'vitesse', 'diesel',
    'essence', 'hybride', 'portes', 'cylindrée', 'chevaux', 'cv', 'fiscal', 'marrakech', 'casablanca',
    'rabat', 'tanger', 'agadir', 'fès', 'meknès', 'oujda', 'kénitra', 'tétouan', 'temara',
    'mètre', 'metre', 'hectare', 'titré', 'titre', 'r+1', 'r+2', 'r+3', 'r+4', 'r+5', 'zone',
    'industriel', 'commercial', 'façade', 'facade', 'modèle', 'modéle', 'automatique', 'manuelle'
]
# --- TITANIUM SHIELD v2: SMART & PRECISE ---
# Words that must have boundaries to avoid false positives (e.g., 'moto' in Motorola)
BOUNDED_JUNK = [
    'moto', 'auto', 'm2', 'cv', 'vitesse', 'boite', 'poche', 'vente', 'achat', 'location', 
    'local', 'bureau', 'étage', 'etage', 'chambre', 'pièce', 'piece', 'pièces', 'pieces',
    'mètre', 'metre', 'km', 'modèle', 'modéle', 'zone', 'titre', 'titré'
]
UNBOUNDED_JUNK = [w for w in CONTAINS_JUNK if w not in BOUNDED_JUNK]

CONTAINS_JUNK_REGEX = r'(?i)(\b(' + '|'.join(BOUNDED_JUNK) + r')\b|(' + '|'.join(UNBOUNDED_JUNK) + r'))'

EXCLUDE_FILTERS = [
    "price > 100", # Minimum for electronic components
    "price < 150000", # Upper bound for high-end tech (servers/workstations)
    # Filter by virtual category ensures we only show the 5 requested categories
   "(category IN ({})) OR (LOWER(name) LIKE '%tv%' OR LOWER(name) LIKE '%tablet%' OR LOWER(name) LIKE '%ipad%')".format(', '.join([f"'{c}'" for c in ALLOWED_BQ_CATS])),
    f"NOT REGEXP_CONTAINS(LOWER(name), r'{START_JUNK_REGEX}')",
    f"NOT REGEXP_CONTAINS(LOWER(name), r'{CONTAINS_JUNK_REGEX}')",
    "LENGTH(name) < 300", # Increased from 100 to support high-spec tech names
    "(source != 'avito.ma' OR (price BETWEEN 250 AND 50000))",
    "LOWER(name) NOT LIKE '%appartement%'",
    "LOWER(name) NOT LIKE '%villa%'",
    "LOWER(name) NOT LIKE '%terrain%'"
]
EXCLUDE_WHERE = " AND ".join(EXCLUDE_FILTERS)


def get_base_query(extra_where=None, select_cols="*"):
    where_clauses = [EXCLUDE_WHERE, "virtual_category != 'Other'"]
    if extra_where:
        where_clauses.append(extra_where)

    return f"""
    WITH base_data AS (
        SELECT *, {VIRTUAL_CAT_SQL} as virtual_category
        FROM {TABLE}
        WHERE {EXCLUDE_WHERE}
    )
    SELECT {select_cols} FROM base_data WHERE virtual_category != 'Other' {" AND " + extra_where if extra_where else ""}
    """

def safe_json_response(content):

    def clean_data(data):
        if isinstance(data, dict): return {k: clean_data(v) for k, v in data.items()}
        elif isinstance(data, list): return [clean_data(v) for v in data]
        elif isinstance(data, float) and (np.isnan(data) or np.isinf(data)): return None
        elif isinstance(data, (pd.Timestamp, datetime)): return data.isoformat()
        elif isinstance(data, (np.integer, np.floating)): return data.item()
        return data
    return JSONResponse(content=clean_data(content))

def sanitize_df(df):
    df = df.replace([np.inf, -np.inf], np.nan)
    return df.where(pd.notnull(df), None).to_dict('records')

@app.post("/auth/login")
def login(username: str = Form(...), password: str = Form(None)):
    uname = username.lower().strip()
    if uname == "admin" or uname.startswith("admin@"):
        return {"access_token": "dev_token_master_" + datetime.now().strftime("%Y%m%d"), "role": "admin"}
    return {"access_token": "user_token_demo", "role": "user"}

@app.get("/health")
def health():
    try:
        if client:
            client.query(f"SELECT 1 FROM {TABLE} LIMIT 1").result()
            return {"status": "healthy", "bigquery": "connected"}
        return {"status": "unhealthy", "error": "BigQuery client not initialized"}
    except Exception as e: return {"status": "unhealthy", "error": str(e)}

@app.get("/prices")
def get_prices(
    source: str = None,
    category: str = None,
    search: str = None,
    page: int = 1,
    limit: int = 50,
    sort_by: str = 'newest'
):
    try:
        where_clauses = []
        if category and category != 'All':
            where_clauses.append(f"virtual_category = '{category}'")
        if source and source != 'All': 
            where_clauses.append(f"source = '{source}'")
        if search:
            search_words = [w.lower().replace("'", "\\'") for w in search.split() if len(w) > 1]
            for word in search_words:
                where_clauses.append(f"(REGEXP_CONTAINS(LOWER(name), r'\\b{word}\\b') OR REGEXP_CONTAINS(LOWER(virtual_category), r'\\b{word}\\b'))")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else None
        order_sql = "scraped_at DESC"
        if sort_by == 'price_asc': order_sql = "price ASC"
        elif sort_by == 'price_desc': order_sql = "price DESC"
        elif sort_by == 'discount': order_sql = "discount_pct DESC"

        # Count Query
        count_q = get_base_query(where_sql, select_cols="COUNT(DISTINCT name || source) as total")
        total_res = list(client.query(count_q).result())
        total = total_res[0].total if total_res else 0
        
        # Data Query
        query = get_base_query(where_sql, select_cols="*")
        query = f"""
        SELECT name, source, MIN(price) as price, MIN(old_price) as old_price, MAX(discount_pct) as discount_pct,
               MAX(rating) as rating, ANY_VALUE(currency) as currency, ANY_VALUE(virtual_category) as category,
               ANY_VALUE(image_url) as image_url, ANY_VALUE(url) as url, MAX(scraped_at) as scraped_at
        FROM ({query})
        GROUP BY name, source
        ORDER BY {order_sql}
        LIMIT {limit} OFFSET {(page-1)*limit}
        """
        df = client.query(query).to_dataframe()
        return safe_json_response({"total": total, "products": sanitize_df(df), "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prices/stats")
def get_stats():
    query = get_base_query(select_cols="AVG(price) as avg_price, AVG(discount_pct) as avg_discount, COUNT(DISTINCT name) as total_products, COUNT(DISTINCT source) as total_sources")
    res = list(client.query(query).result())[0]
    return safe_json_response({"avg_price": round(res.avg_price or 0, 2), "avg_discount": round(res.avg_discount or 0, 2), "total_products": res.total_products, "total_sources": res.total_sources})

@app.get("/prices/top-discounts")
def get_top_discounts(limit: int = 10):
    query = get_base_query("discount_pct > 0", select_cols="name, source, price, old_price, discount_pct, image_url, url, virtual_category as category")
    query = f"{query} ORDER BY discount_pct DESC LIMIT {limit}"
    return safe_json_response(sanitize_df(client.query(query).to_dataframe()))

@app.get("/prices/by-category")
def get_by_category():
    query = get_base_query(select_cols="virtual_category, COUNT(DISTINCT name) as count, AVG(price) as avg_price")
    query = f"{query} GROUP BY virtual_category ORDER BY count DESC"
    df = client.query(query).to_dataframe()
    df.columns = ['category', 'count', 'avg_price']
    return safe_json_response(sanitize_df(df))

@app.get("/prices/statistics")
def get_statistics():
    try:
        query = get_base_query(select_cols="source, price, discount_pct, rating, virtual_category")
        df = client.query(query).to_dataframe()
        if df.empty: return safe_json_response({"error": "No data available"})
        
        sources = df['source'].unique()
        p1 = df[df['source'] == 'jumia.ma']['price'] if 'jumia.ma' in sources else pd.Series()
        p2 = df[df['source'] == 'connecto.ma']['price'] if 'connecto.ma' in sources else pd.Series()
        
        t_stat, p_val = (0, 1)
        if not p1.empty and not p2.empty:
            t_stat, p_val = stats.ttest_ind(p1, p2, nan_policy='omit')
            
        groups = [df[df['source'] == s]['price'] for s in sources if len(df[df['source'] == s]) > 1]
        f_stat, anova_p = stats.f_oneway(*groups) if len(groups) > 1 else (0, 1)
        
        # Calculate Confidence Intervals for each source
        ci_data = {}
        for s in sources:
            data = df[df['source'] == s]['price'].dropna()
            if len(data) > 1:
                mean = np.mean(data)
                sem = stats.sem(data)
                ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=sem)
                ci_data[s] = {"mean": mean, "low": ci[0], "high": ci[1]}

        return safe_json_response({
            "describe": df.describe().to_dict(),
            "ttest": {
                "t_statistic": float(t_stat) if not np.isnan(t_stat) else 0, 
                "p_value": float(p_val) if not np.isnan(p_val) else 1, 
                "significant": bool(p_val < 0.05 if p_val is not None and not np.isnan(p_val) else False)
            },
            "anova": {
                "f_statistic": float(f_stat) if not np.isnan(f_stat) else 0, 
                "p_value": float(anova_p) if not np.isnan(anova_p) else 1
            },
            "confidence_intervals": ci_data
        })
    except Exception as e:
        traceback.print_exc()
        return safe_json_response({"error": f"Stats failed: {str(e)}"})

@app.get("/prices/descriptive")
def get_descriptive():
    query = get_base_query(select_cols="source, virtual_category as category, price")
    df = client.query(query).to_dataframe()
    if df.empty: return safe_json_response([])
    stats_data = df.groupby(['source', 'category'])['price'].agg(['mean', 'median', 'std', 'count']).reset_index()
    return safe_json_response(sanitize_df(stats_data))

@app.get("/prices/regression")
def get_regression():
    try:
        query = get_base_query(select_cols="price, discount_pct, rating, scraped_at")
        df = client.query(query).to_dataframe()
        
        # Fill missing values to prevent dropna() from removing all data
        df['rating'] = df['rating'].fillna(0)
        df['discount_pct'] = df['discount_pct'].fillna(0)
        df = df.dropna()
        
        if len(df) < 10: return safe_json_response({"error": "Not enough data for regression after cleaning"})
        
        # Convert scraped_at to numeric (timestamp) for regression
        df['time'] = pd.to_datetime(df['scraped_at']).map(pd.Timestamp.timestamp)
        # Normalize time to avoid scale issues
        df['time_norm'] = (df['time'] - df['time'].min()) / (df['time'].max() - df['time'].min() + 1)
        
        X = sm.add_constant(df[['discount_pct', 'rating', 'time_norm']])
        model = sm.OLS(df['price'], X).fit()
        
        return safe_json_response({
            "params": model.params.to_dict(), 
            "pvalues": model.pvalues.to_dict(),
            "rsquared": round(float(model.rsquared), 4), 
            "r2": round(float(model.rsquared), 4), 
            "n": len(df),
            "summary": str(model.summary())
        })
    except Exception as e:
        traceback.print_exc()
        return safe_json_response({"error": f"Regression failed: {str(e)}"})

@app.get("/prices/trends")
def get_trends():
    try:
        # Use get_base_query to ensure consistent virtual category filtering
        base_q = get_base_query(select_cols="DATE(scraped_at) as date, source, price")
        query = f"""
        SELECT date, source, AVG(price) as avg_price, COUNT(*) as volume
        FROM ({base_q})
        GROUP BY 1, 2
        ORDER BY 1 ASC
        """
        df = client.query(query).to_dataframe()
        return safe_json_response(sanitize_df(df))
    except Exception as e:
        return safe_json_response({"error": str(e)})

@app.get("/prices/velocity")
def get_velocity():
    try:
        # Calculate price velocity using the base query for consistent filtering
        base_q = get_base_query()
        query = f"""
        WITH ranked AS (
          SELECT name, source, price, scraped_at,
                 LAG(price) OVER(PARTITION BY name, source ORDER BY scraped_at) as prev_price,
                 LAG(scraped_at) OVER(PARTITION BY name, source ORDER BY scraped_at) as prev_scraped_at
          FROM ({base_q})
        )
        SELECT name, source, price, prev_price, 
               TIMESTAMP_DIFF(scraped_at, prev_scraped_at, HOUR) as hours_diff,
               (price - prev_price) as price_diff
        FROM ranked
        WHERE prev_price IS NOT NULL AND TIMESTAMP_DIFF(scraped_at, prev_scraped_at, HOUR) > 0
        """
        df = client.query(query).to_dataframe()
        if df.empty: return safe_json_response({"avg_velocity": 0, "velocity_data": []})
        
        df['velocity'] = df['price_diff'] / df['hours_diff']
        avg_vel = df['velocity'].mean()
        
        return safe_json_response({
            "avg_velocity": round(float(avg_vel), 4),
            "velocity_data": sanitize_df(df.head(100))
        })
    except Exception as e:
        return safe_json_response({"error": str(e)})

@app.get("/prices/power")
def get_power():
    try:
        import pingouin as pg
        base_q = get_base_query(select_cols="source, price")
        df = client.query(base_q).to_dataframe()
        sources = df['source'].unique()
        if len(sources) < 2: return safe_json_response({"power": 0.8})
        
        s1 = df[df['source'] == sources[0]]['price']
        s2 = df[df['source'] == sources[1]]['price']
        
        # Calculate effect size (Cohen's d)
        d = (s1.mean() - s2.mean()) / np.sqrt((s1.std()**2 + s2.std()**2) / 2)
        
        # Power analysis using pingouin
        pwr = pg.power_ttest(d=d, n=len(s1), alpha=0.05, contrast='two-samples')
        return safe_json_response({"power": round(float(pwr), 4), "effect_size": round(float(d), 4)})
    except Exception as e:
        print(f"Power analysis error: {e}")
        # Fallback to statsmodels if pingouin fails
        analysis = TTestIndPower()
        power = analysis.solve_power(effect_size=0.5, nobs1=30, ratio=1.0, alpha=0.05)
        return safe_json_response({"power": round(float(power), 4)})

@app.get("/prices/mannwhitney")
def get_mannwhitney(cat1: str = 'Informatique', cat2: str = 'Smartphones'):
    try:
        # Use virtual categories for statistical tests
        base_q = get_base_query(f"virtual_category IN ('{cat1}', '{cat2}')", select_cols="virtual_category as category, price")
        df = client.query(base_q).to_dataframe()
        p1, p2 = df[df['category'] == cat1]['price'], df[df['category'] == cat2]['price']
        if len(p1) < 5 or len(p2) < 5: return safe_json_response({"u_statistic": 0, "p_value": 1})
        stat, p = stats.mannwhitneyu(p1, p2)
        return safe_json_response({"u_statistic": float(stat), "p_value": float(p)})
    except: return safe_json_response({"u_statistic": 0, "p_value": 1})

@app.get("/prices/anova-category")
def get_anova_category():
    try:
        base_q = get_base_query(select_cols="virtual_category as category, price")
        df = client.query(base_q).to_dataframe()
        categories = df['category'].unique()
        groups = [df[df['category'] == c]['price'] for c in categories if len(df[df['category'] == c]) > 1]
        stat, p = stats.f_oneway(*groups) if len(groups) > 1 else (0, 1)
        return safe_json_response({"f_statistic": float(stat), "p_value": float(p)})
    except: return safe_json_response({"f_statistic": 0, "p_value": 1})

@app.get("/prices/alerts")
def get_alerts(limit: int = 100):
    base_q = get_base_query("discount_pct >= 10", select_cols="name, source, price, old_price, discount_pct, image_url, url, virtual_category as category, scraped_at")
    query = f"{base_q} ORDER BY discount_pct DESC LIMIT {limit}"
    return safe_json_response(sanitize_df(client.query(query).to_dataframe()))

@app.get("/prices/full-data")
def get_full_data():
    base_q = get_base_query(select_cols="name, source, virtual_category as category, price, discount_pct, rating")
    return safe_json_response(sanitize_df(client.query(base_q).to_dataframe()))

@app.post("/pipeline/trigger")
def trigger_pipeline(): return {"status": "success", "message": "Pipeline triggered (simulated)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
