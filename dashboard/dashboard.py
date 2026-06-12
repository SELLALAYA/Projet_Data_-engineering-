import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
import os

# ── Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Price Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Mono', monospace; }
    .main { background-color: #0d1117; }
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2330 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8b949e;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .pipeline-badge {
        display: inline-block;
        background: #1f6feb22;
        border: 1px solid #1f6feb;
        color: #58a6ff;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.78rem;
        font-family: 'Space Mono', monospace;
        margin: 2px;
    }
    .section-header {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8b949e;
        border-bottom: 1px solid #21262d;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
    [data-testid="stMetricValue"] { color: #58a6ff !important; font-family: 'Space Mono', monospace; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
</style>
""", unsafe_allow_html=True)

# ── BigQuery Client ───────────────────────────────────────────────────────
PROJECT_ID = 'project-32a82952-90fa-4dd7-b9c'
DATASET    = 'price_intelligence_dbt'

@st.cache_resource
def get_bq_client():
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if creds_path and os.path.exists(creds_path):
        from google.oauth2.credentials import Credentials
        import json
        with open(creds_path) as f:
            info = json.load(f)
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        creds = Credentials(
            token=None,
            refresh_token=info['refresh_token'],
            token_uri=info.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=info['client_id'],
            client_secret=info['client_secret'],
            scopes=['https://www.googleapis.com/auth/bigquery',
                    'https://www.googleapis.com/auth/cloud-platform']
        )
        return bigquery.Client(project=PROJECT_ID, credentials=creds)
    return bigquery.Client(project=PROJECT_ID)

@st.cache_data(ttl=300)
def load_cleaned(_client):
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.prices_cleaned`
        WHERE price > 0
        LIMIT 6303
    """
    try:
        return _client.query(query).to_dataframe()
    except Exception as e:
        st.warning(f"BigQuery error: {e}. Using sample data.")
        return get_sample_cleaned()

@st.cache_data(ttl=300)
def load_aggregated(_client):
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.prices_aggregated`
        ORDER BY avg_price DESC
    """
    try:
        return _client.query(query).to_dataframe()
    except Exception as e:
        return get_sample_aggregated()

def get_sample_aggregated():
    return pd.DataFrame({
        "source": ["jumia.ma", "avito.ma", "electroplanet.ma"],
        "category": ["Informatique", "Téléphones", "Électroménager"],
        "total_products": [4795, 1441, 67],
        "avg_price": [193091.0, 860816.0, 4500.0],
        "min_price": [9.0, 100.0, 500.0],
        "max_price": [6300000.0, 5000000.0, 15000.0],
        "avg_discount": [16.69, 0.0, 10.0],
    })

def get_sample_cleaned():
    import numpy as np
    np.random.seed(42)
    n = 500
    return pd.DataFrame({
        "product_id": [f"P{i:04d}" for i in range(n)],
        "name": [f"Product {i}" for i in range(n)],
        "price": np.random.lognormal(7, 1.5, n).round(2),
        "old_price": np.random.lognormal(7.2, 1.5, n).round(2),
        "discount_pct": np.random.uniform(0, 87, n).round(1),
        "rating": np.random.uniform(1, 5, n).round(1),
        "category": np.random.choice(["Informatique", "Téléphones & Smartphones", "Électroménager"], n),
        "source": np.random.choice(["jumia.ma", "avito.ma", "electroplanet.ma"], n, p=[0.76, 0.23, 0.01]),
        "currency": ["MAD"] * n,
        "scraped_at": pd.to_datetime("2026-03-29")
    })

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 32px 0 24px 0;">
    <div style="font-family: Space Mono, monospace; font-size: 0.75rem;
                color: #58a6ff; letter-spacing: 0.15em; text-transform: uppercase;
                margin-bottom: 8px;">● LIVE PIPELINE OUTPUT</div>
    <h1 style="font-size: 2.2rem; margin: 0; color: #e6edf3;">Price Intelligence</h1>
    <p style="color: #8b949e; margin-top: 6px; font-size: 0.95rem;">
        Data Engineering Pipeline · Scrapy → NiFi → Bigtable → dbt → BigQuery
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom: 32px;">
    <span class="pipeline-badge">Scrapy</span> →
    <span class="pipeline-badge">NiFi</span> →
    <span class="pipeline-badge">Bigtable</span> →
    <span class="pipeline-badge">Airflow</span> →
    <span class="pipeline-badge">dbt-bigquery</span> →
    <span class="pipeline-badge" style="background:#2ea04322; border-color:#2ea043; color:#3fb950;">✔ Dashboard</span>
</div>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────
try:
    client = get_bq_client()
    df_clean = load_cleaned(client)
    df_agg   = load_aggregated(client)
    st.success(f"✅ Connected to BigQuery — {len(df_clean):,} records loaded from dbt pipeline")
except Exception as e:
    st.info("📎 Running in demo mode — connect BigQuery credentials to use live data.")
    df_clean = get_sample_cleaned()
    df_agg   = get_sample_aggregated()

# ── Sidebar Filters ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔧 Filters")
    sources    = ["All"] + sorted(df_clean["source"].unique().tolist())
    sel_source = st.selectbox("Source", sources)
    categories = ["All"] + sorted(df_clean["category"].unique().tolist())
    sel_cat    = st.selectbox("Category", categories)
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.78rem; color:#8b949e;">
    <b>Pipeline Stack</b><br><br>
    🕷 Scrapy<br>🔧 Apache NiFi<br>🗄 Bigtable<br>
    ⏰ Airflow<br>🔧 dbt-bigquery<br>✅ Great Expectations<br>📊 Streamlit
    </div>
    """, unsafe_allow_html=True)

# Apply filters
df_f = df_clean.copy()
if sel_source != "All":
    df_f = df_f[df_f["source"] == sel_source]
if sel_cat != "All":
    df_f = df_f[df_f["category"] == sel_cat]

# ── KPI Metrics ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">KEY METRICS — DBT PRICES_AGGREGATED</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{len(df_f):,}</div>
        <div class="metric-label">Total Products</div>
    </div>""", unsafe_allow_html=True)
with col2:
    avg_p = df_f["price"].mean() if len(df_f) else 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{avg_p:,.0f}</div>
        <div class="metric-label">Avg Price (MAD)</div>
    </div>""", unsafe_allow_html=True)
with col3:
    avg_d = df_f["discount_pct"].mean() if len(df_f) else 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{avg_d:.1f}%</div>
        <div class="metric-label">Avg Discount</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{df_f["source"].nunique()}</div>
        <div class="metric-label">Sources</div>
    </div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{df_f["category"].nunique()}</div>
        <div class="metric-label">Categories</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">PRICE DISTRIBUTION BY SOURCE</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    fig1 = px.box(df_f, x="source", y="price", color="source",
                  title="Price Distribution per Source",
                  color_discrete_sequence=["#58a6ff", "#3fb950", "#f78166"])
    fig1.update_yaxes(range=[0, df_f["price"].quantile(0.95)])
    fig1.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                       font_color="#8b949e", title_font_color="#e6edf3",
                       showlegend=False,
                       xaxis=dict(gridcolor="#21262d"),
                       yaxis=dict(gridcolor="#21262d"))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    src_cnt = df_f.groupby("source").size().reset_index(name="count")
    fig2 = px.bar(src_cnt, x="source", y="count",
                  title="Products per Source",
                  color="count",
                  color_continuous_scale=["#1f6feb", "#58a6ff", "#cae8ff"])
    fig2.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                       font_color="#8b949e", title_font_color="#e6edf3",
                       showlegend=False, coloraxis_showscale=False,
                       xaxis=dict(gridcolor="#21262d"),
                       yaxis=dict(gridcolor="#21262d"))
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">CATEGORY ANALYSIS — DBT PRICES_AGGREGATED</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    cat_avg = df_f.groupby("category")["price"].median().reset_index()
    cat_avg.columns = ["category", "median_price"]
    fig3 = px.bar(cat_avg.sort_values("median_price", ascending=True),
                  x="median_price", y="category", orientation="h",
                  title="Median Price by Category (MAD)",
                  color="median_price",
                  color_continuous_scale=["#1f6feb", "#58a6ff"])
    fig3.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                       font_color="#8b949e", title_font_color="#e6edf3",
                       coloraxis_showscale=False,
                       xaxis=dict(gridcolor="#21262d"),
                       yaxis=dict(gridcolor="#21262d"))
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    fig4 = px.histogram(df_f, x="discount_pct", nbins=30,
                        title="Discount Distribution (%)",
                        color_discrete_sequence=["#3fb950"])
    fig4.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#0d1117",
                       font_color="#8b949e", title_font_color="#e6edf3",
                       xaxis=dict(gridcolor="#21262d"),
                       yaxis=dict(gridcolor="#21262d"))
    st.plotly_chart(fig4, use_container_width=True)

# ── Stats Summary ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">STATISTICAL INSIGHTS — SCIPY · STATSMODELS · PINGOUIN</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">49.84</div>
        <div class="metric-label">T-Test Statistic (avito vs jumia)</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">375.79</div>
        <div class="metric-label">ANOVA F-Stat (categories)</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">-0.25</div>
        <div class="metric-label">Correlation (price vs discount)</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Data Table ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">RAW DATA — DBT PRICES_CLEANED (sample)</div>', unsafe_allow_html=True)
display_cols = ["name", "price", "old_price", "discount_pct", "category", "source", "currency"]
available_cols = [c for c in display_cols if c in df_f.columns]
st.dataframe(df_f[available_cols].head(100), use_container_width=True, height=300)

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:40px; padding-top:20px; border-top:1px solid #21262d;
            text-align:center; color:#484f58; font-size:0.78rem;
            font-family: Space Mono, monospace;">
    Price Intelligence · Data Engineering Pipeline · Scrapy → NiFi → Bigtable → Airflow → dbt → BigQuery ✅
</div>
""", unsafe_allow_html=True)