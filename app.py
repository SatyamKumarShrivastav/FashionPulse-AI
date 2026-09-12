"""
╔══════════════════════════════════════════════════════════════╗
║           FASHIONPULSE AI — Flask REST API                   ║
║           13 endpoints  •  4 ML models  •  MySQL            ║
╚══════════════════════════════════════════════════════════════╝

Run:
    python app.py
    → http://localhost:5000
"""

from __future__ import annotations
import os, sys, json, warnings
from decimal import Decimal
import numpy  as np
import pandas as pd
import joblib
import mysql.connector
from mysql.connector import Error as MySQLError
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG, TABLE_NAME, MODEL_DIR, FLASK_HOST, FLASK_PORT, FLASK_DEBUG, get_db_connection, get_dict_cursor

# ─────────────────────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)


# ─────────────────────────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────────────────────────

def get_conn():
    return get_db_connection(with_db=True)


def query_df(sql: str, params=None) -> pd.DataFrame:
    """Run SQL and return a DataFrame using cursor (pandas 2.x safe)."""
    conn = get_conn()
    cursor = get_dict_cursor(conn)
    try:
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        df = pd.DataFrame(rows) if rows else pd.DataFrame()
    finally:
        cursor.close()
        conn.close()
    return df


def query_one(sql: str, params=None) -> dict:
    conn = get_conn()
    cursor = get_dict_cursor(conn)
    try:
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    return row or {}


def query_all(sql: str, params=None) -> list:
    conn = get_conn()
    cursor = get_dict_cursor(conn)
    try:
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return rows or []


# ─────────────────────────────────────────────────────────────
# JSON SERIALISER (handles numpy types)
# ─────────────────────────────────────────────────────────────

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal): return float(obj)
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)): return None
        return super().default(obj)


def jsend(data, status: int = 200):
    return app.response_class(
        response=json.dumps(data, cls=NpEncoder),
        status=status,
        mimetype="application/json",
    )


# ─────────────────────────────────────────────────────────────
# ML MODELS — LAZY LOAD
# ─────────────────────────────────────────────────────────────

MODELS: dict = {}


def load_models() -> None:
    files = {
        "sales":       "sales_model.pkl",
        "classifier":  "classifier_model.pkl",
        "clf_le":      "classifier_label_encoder.pkl",
        "return_risk": "return_risk_model.pkl",
        "segmenter":   "segmenter.pkl",
    }
    for key, fname in files.items():
        path = os.path.join(MODEL_DIR, fname)
        if os.path.exists(path):
            MODELS[key] = joblib.load(path)

    metrics_path = os.path.join(MODEL_DIR, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            MODELS["metrics"] = json.load(f)


def models_ready() -> bool:
    return "sales" in MODELS


# Load models at startup (works with Flask reloader too)
load_models()


# ─────────────────────────────────────────────────────────────
# STATIC ROUTE
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────────────────────
# API 1 — EXECUTIVE KPIs
# ─────────────────────────────────────────────────────────────

@app.route("/api/kpis")
def api_kpis():
    sql = f"""
        SELECT
            COUNT(*)                           AS total_products,
            SUM(units_sold)                    AS total_units_sold,
            ROUND(SUM(price_usd * units_sold)) AS est_sales_value,
            ROUND(AVG(price_usd), 2)           AS avg_price,
            ROUND(AVG(rating), 2)              AS avg_rating,
            ROUND(AVG(discount_percent), 1)    AS avg_discount,
            SUM(stock_quantity)                AS total_inventory,
            ROUND(AVG(return_rate), 2)         AS avg_return_rate,
            COUNT(DISTINCT category)           AS total_categories,
            ROUND(MIN(price_usd), 2)           AS min_price,
            ROUND(MAX(price_usd), 2)           AS max_price,
            MAX(units_sold)                    AS max_units_sold
        FROM `{TABLE_NAME}`
    """
    row = query_one(sql)
    return jsend(row)


# ─────────────────────────────────────────────────────────────
# API 2 — SALES BY CATEGORY
# ─────────────────────────────────────────────────────────────

@app.route("/api/sales-by-category")
def api_sales_category():
    sql = f"""
        SELECT
            category,
            SUM(units_sold)                       AS total_sales,
            COUNT(*)                              AS product_count,
            ROUND(AVG(units_sold), 1)             AS avg_sales,
            ROUND(SUM(price_usd * units_sold), 0) AS est_revenue,
            ROUND(AVG(rating), 2)                 AS avg_rating,
            ROUND(AVG(return_rate), 2)            AS avg_return_rate
        FROM `{TABLE_NAME}`
        GROUP BY category
        ORDER BY total_sales DESC
    """
    rows = query_all(sql)
    return jsend(rows)


# ─────────────────────────────────────────────────────────────
# API 3 — SALES BY SEASON
# ─────────────────────────────────────────────────────────────

@app.route("/api/sales-by-season")
def api_sales_season():
    sql = f"""
        SELECT
            season,
            SUM(units_sold)            AS total_sales,
            COUNT(*)                   AS product_count,
            ROUND(AVG(units_sold), 1)  AS avg_sales,
            ROUND(AVG(rating), 2)      AS avg_rating,
            ROUND(AVG(return_rate), 2) AS avg_return_rate
        FROM `{TABLE_NAME}`
        GROUP BY season
        ORDER BY total_sales DESC
    """
    rows = query_all(sql)
    return jsend(rows)


# ─────────────────────────────────────────────────────────────
# API 4 — TOP & BOTTOM PRODUCTS
# ─────────────────────────────────────────────────────────────

@app.route("/api/top-products")
def api_top_products():
    n = request.args.get("n", 10, type=int)
    n = min(n, 50)

    top_sql = f"""
        SELECT product_id, category, subcategory, style, season,
               price_usd, discount_percent, rating, review_count,
               stock_quantity, units_sold, return_rate,
               ROUND(price_usd * units_sold, 0) AS est_revenue
        FROM `{TABLE_NAME}`
        ORDER BY units_sold DESC
        LIMIT {n}
    """
    bot_sql = f"""
        SELECT product_id, category, subcategory, style, season,
               price_usd, discount_percent, rating, review_count,
               stock_quantity, units_sold, return_rate,
               ROUND(price_usd * units_sold, 0) AS est_revenue
        FROM `{TABLE_NAME}`
        WHERE units_sold > 0
        ORDER BY units_sold ASC
        LIMIT {n}
    """
    return jsend({
        "top":    query_all(top_sql),
        "bottom": query_all(bot_sql),
    })


# ─────────────────────────────────────────────────────────────
# API 5 — CATEGORY PERFORMANCE
# ─────────────────────────────────────────────────────────────

@app.route("/api/category-performance")
def api_category_performance():
    sql = f"""
        SELECT
            category,
            subcategory,
            COUNT(*)                              AS products,
            ROUND(AVG(price_usd), 2)              AS avg_price,
            ROUND(AVG(discount_percent), 1)       AS avg_discount,
            ROUND(AVG(rating), 2)                 AS avg_rating,
            ROUND(AVG(review_count), 0)           AS avg_reviews,
            SUM(units_sold)                       AS total_sales,
            ROUND(AVG(units_sold), 1)             AS avg_sales,
            SUM(stock_quantity)                   AS total_stock,
            ROUND(AVG(return_rate), 2)            AS avg_return_rate,
            ROUND(SUM(price_usd * units_sold), 0) AS est_revenue
        FROM `{TABLE_NAME}`
        GROUP BY category, subcategory
        ORDER BY total_sales DESC
    """
    rows = query_all(sql)
    return jsend(rows)


# ─────────────────────────────────────────────────────────────
# API 6 — PRICE ANALYSIS
# ─────────────────────────────────────────────────────────────

@app.route("/api/price-analysis")
def api_price_analysis():
    # Price bands
    bands_sql = f"""
        SELECT
            CASE
                WHEN price_usd < 25  THEN 'Budget (<$25)'
                WHEN price_usd < 50  THEN 'Mid ($25–50)'
                WHEN price_usd < 100 THEN 'Premium ($50–100)'
                ELSE                      'Luxury (>$100)'
            END                                AS price_band,
            COUNT(*)                           AS products,
            ROUND(AVG(units_sold), 1)          AS avg_sales,
            ROUND(AVG(rating), 2)              AS avg_rating,
            ROUND(AVG(return_rate), 2)         AS avg_return,
            ROUND(AVG(discount_percent), 1)    AS avg_discount
        FROM `{TABLE_NAME}`
        GROUP BY price_band
        ORDER BY MIN(price_usd)
    """

    # Price vs sales scatter (sample 500)
    scatter_sql = f"""
        SELECT price_usd, units_sold, rating, category
        FROM `{TABLE_NAME}`
        ORDER BY RAND()
        LIMIT 500
    """

    # Price distribution (histogram buckets)
    dist_sql = f"""
        SELECT
            ROUND(price_usd / 10) * 10        AS bucket,
            COUNT(*)                           AS count
        FROM `{TABLE_NAME}`
        GROUP BY bucket
        ORDER BY bucket
    """

    return jsend({
        "bands":   query_all(bands_sql),
        "scatter": query_all(scatter_sql),
        "distribution": query_all(dist_sql),
    })


# ─────────────────────────────────────────────────────────────
# API 7 — DISCOUNT ANALYSIS
# ─────────────────────────────────────────────────────────────

@app.route("/api/discount-analysis")
def api_discount_analysis():
    sql = f"""
        SELECT
            CASE
                WHEN discount_percent = 0        THEN '0% (No Discount)'
                WHEN discount_percent <= 10      THEN '1–10%'
                WHEN discount_percent <= 20      THEN '11–20%'
                WHEN discount_percent <= 30      THEN '21–30%'
                WHEN discount_percent <= 40      THEN '31–40%'
                ELSE                                  '41%+'
            END                                 AS discount_band,
            COUNT(*)                            AS products,
            ROUND(AVG(units_sold), 1)           AS avg_sales,
            ROUND(AVG(rating), 2)               AS avg_rating,
            ROUND(AVG(return_rate), 2)          AS avg_return,
            ROUND(AVG(price_usd), 2)            AS avg_price,
            SUM(units_sold)                     AS total_sales
        FROM `{TABLE_NAME}`
        GROUP BY discount_band
        ORDER BY MIN(discount_percent)
    """
    rows = query_all(sql)
    return jsend(rows)


# ─────────────────────────────────────────────────────────────
# API 8 — INVENTORY MATRIX
# ─────────────────────────────────────────────────────────────

@app.route("/api/inventory-matrix")
def api_inventory_matrix():
    # Calculate medians
    medians = query_one(f"""
        SELECT
            AVG(units_sold)    AS med_sales,
            AVG(stock_quantity) AS med_stock
        FROM `{TABLE_NAME}`
    """)
    ms, mk = medians["med_sales"], medians["med_stock"]

    matrix_sql = f"""
        SELECT
            CASE
                WHEN units_sold >= {ms} AND stock_quantity <  {mk} THEN 'Restock Now'
                WHEN units_sold >= {ms} AND stock_quantity >= {mk} THEN 'Healthy'
                WHEN units_sold <  {ms} AND stock_quantity >= {mk} THEN 'Overstock'
                ELSE                                                     'Low Priority'
            END             AS quadrant,
            COUNT(*)        AS count,
            SUM(units_sold) AS total_sales,
            SUM(stock_quantity) AS total_stock
        FROM `{TABLE_NAME}`
        GROUP BY quadrant
    """
    matrix = query_all(matrix_sql)

    # Low-stock alerts
    alerts_sql = f"""
        SELECT product_id, category, subcategory, style,
               units_sold, stock_quantity, return_rate, price_usd
        FROM `{TABLE_NAME}`
        WHERE units_sold >= {ms} AND stock_quantity < {mk}
        ORDER BY units_sold DESC
        LIMIT 20
    """
    alerts = query_all(alerts_sql)

    # Return by category
    ret_sql = f"""
        SELECT category,
               ROUND(AVG(return_rate), 2)  AS avg_return_rate,
               COUNT(*)                    AS products,
               SUM(units_sold)             AS total_sales
        FROM `{TABLE_NAME}`
        GROUP BY category
        ORDER BY avg_return_rate DESC
    """
    returns = query_all(ret_sql)

    return jsend({
        "matrix":  matrix,
        "alerts":  alerts,
        "returns": returns,
        "medians": {"sales": round(float(ms), 1), "stock": round(float(mk), 1)},
    })


# ─────────────────────────────────────────────────────────────
# API 9 — RETURN ANALYSIS (detailed)
# ─────────────────────────────────────────────────────────────

@app.route("/api/return-analysis")
def api_return_analysis():
    by_material = query_all(f"""
        SELECT material,
               ROUND(AVG(return_rate), 2) AS avg_return,
               COUNT(*) AS products
        FROM `{TABLE_NAME}`
        GROUP BY material
        ORDER BY avg_return DESC
        LIMIT 15
    """)

    by_size = query_all(f"""
        SELECT size,
               ROUND(AVG(return_rate), 2) AS avg_return,
               COUNT(*) AS products
        FROM `{TABLE_NAME}`
        GROUP BY size
        ORDER BY avg_return DESC
    """)

    by_style = query_all(f"""
        SELECT style,
               ROUND(AVG(return_rate), 2) AS avg_return,
               COUNT(*) AS products
        FROM `{TABLE_NAME}`
        GROUP BY style
        ORDER BY avg_return DESC
        LIMIT 15
    """)

    by_season = query_all(f"""
        SELECT season,
               ROUND(AVG(return_rate), 2) AS avg_return,
               COUNT(*) AS products
        FROM `{TABLE_NAME}`
        GROUP BY season
        ORDER BY avg_return DESC
    """)

    return jsend({
        "by_material": by_material,
        "by_size":     by_size,
        "by_style":    by_style,
        "by_season":   by_season,
    })


# ─────────────────────────────────────────────────────────────
# API 10 — ML PREDICT
# ─────────────────────────────────────────────────────────────

PREDICT_FEATURES = [
    "category", "subcategory", "material", "color",
    "size", "season", "style", "price_usd", "discount_percent",
]


@app.route("/api/predict", methods=["POST"])
def api_predict():
    if not models_ready():
        return jsend({"error": "ML models not loaded. Run train_models.py first."}, 503)

    data = request.json or {}
    missing = [f for f in PREDICT_FEATURES if f not in data]
    if missing:
        return jsend({"error": f"Missing fields: {missing}"}, 400)

    df = pd.DataFrame([data])[PREDICT_FEATURES]

    # ── Sales prediction ────────────────────────────────────
    sales_pred_log = MODELS["sales"].predict(df)[0]
    sales_pred     = max(0, round(float(np.expm1(sales_pred_log))))

    # ── Performance class ───────────────────────────────────
    clf_enc = MODELS["classifier"].predict(df)[0]
    le      = MODELS.get("clf_le")
    perf    = le.inverse_transform([clf_enc])[0] if le else str(clf_enc)

    # ── Return risk ─────────────────────────────────────────
    rr_proba = MODELS["return_risk"].predict_proba(df)[0]
    rr_label = MODELS["return_risk"].predict(df)[0]
    rr_score = round(float(rr_proba[1]) * 100, 1)

    # ── Segment ─────────────────────────────────────────────
    seg_data = MODELS.get("segmenter")
    segment  = "N/A"
    if seg_data:
        seg_feat = ["price_usd", "discount_percent"]
        seg_input = np.zeros((1, 6))
        seg_input[0, 0] = float(data.get("price_usd", 0))
        seg_input[0, 1] = float(data.get("discount_percent", 0))
        seg_scaled = seg_data["scaler"].transform(seg_input)
        cluster_id = int(seg_data["kmeans"].predict(seg_scaled)[0])
        cluster_names = {
            0: "Premium High Performers",
            1: "Discount-Driven Products",
            2: "Low Demand Products",
            3: "High Return Risk Products",
        }
        segment = cluster_names.get(cluster_id, f"Segment {cluster_id}")

    # ── Business recommendation ─────────────────────────────
    rec = _generate_recommendation(perf, rr_score, segment)

    return jsend({
        "predicted_units_sold": sales_pred,
        "performance_class":    perf,
        "return_risk_score":    rr_score,
        "return_risk_label":    "High Risk" if rr_label == 1 else "Normal",
        "segment":              segment,
        "recommendation":       rec,
    })


def _generate_recommendation(perf: str, rr_score: float, segment: str) -> str:
    if perf == "High Performer" and rr_score < 40:
        return "🟢 High-Potential Product — Ensure adequate stock levels and highlight in promotions."
    elif perf == "High Performer" and rr_score >= 60:
        return "🟡 Strong Sales but High Return Risk — Investigate sizing/quality; monitor returns closely."
    elif perf == "Low Performer" and rr_score >= 60:
        return "🔴 Low Sales + High Returns — Consider discontinuing or significant redesign."
    elif perf == "Low Performer":
        return "🟠 Low Performer — Review pricing strategy or introduce discounts to stimulate demand."
    elif "High Return" in segment:
        return "⚠️ Return Risk Segment — Audit product descriptions, sizing charts, and material quality."
    else:
        return "🔵 Mid Performer — Monitor performance; consider targeted discount campaigns."


# ─────────────────────────────────────────────────────────────
# API 11 — SEGMENT (POST)
# ─────────────────────────────────────────────────────────────

@app.route("/api/segment", methods=["POST"])
def api_segment():
    if not models_ready():
        return jsend({"error": "Models not ready."}, 503)

    data = request.json or {}
    seg_data = MODELS.get("segmenter")
    if not seg_data:
        return jsend({"error": "Segmenter not loaded."}, 503)

    feat_vals = [
        float(data.get("price_usd", 50)),
        float(data.get("discount_percent", 10)),
        float(data.get("rating", 3.5)),
        float(data.get("review_count", 50)),
        float(data.get("units_sold", 100)),
        float(data.get("return_rate", 15)),
    ]
    X = np.array(feat_vals).reshape(1, -1)
    Xs = seg_data["scaler"].transform(X)
    cluster = int(seg_data["kmeans"].predict(Xs)[0])
    names = {
        0: "Premium High Performers",
        1: "Discount-Driven Products",
        2: "Low Demand Products",
        3: "High Return Risk Products",
    }
    return jsend({"cluster": cluster, "segment": names.get(cluster, f"Segment {cluster}")})


# ─────────────────────────────────────────────────────────────
# API 12 — MODEL PERFORMANCE METRICS
# ─────────────────────────────────────────────────────────────

@app.route("/api/model-performance")
def api_model_performance():
    metrics = MODELS.get("metrics", {})
    if not metrics:
        return jsend({"error": "metrics.json not found. Run train_models.py first."}, 503)
    return jsend(metrics)


# ─────────────────────────────────────────────────────────────
# API 13 — FEATURE IMPORTANCE
# ─────────────────────────────────────────────────────────────

@app.route("/api/feature-importance")
def api_feature_importance():
    metrics = MODELS.get("metrics", {})
    fi = metrics.get("sales", {}).get("feature_importance", [])
    # Return top 15
    return jsend(fi[:15])


# ─────────────────────────────────────────────────────────────
# API 14 — STYLE PERFORMANCE
# ─────────────────────────────────────────────────────────────

@app.route("/api/style-performance")
def api_style_performance():
    sql = f"""
        SELECT style,
               COUNT(*)                              AS products,
               SUM(units_sold)                       AS total_sales,
               ROUND(AVG(units_sold), 1)             AS avg_sales,
               ROUND(AVG(rating), 2)                 AS avg_rating,
               ROUND(AVG(return_rate), 2)            AS avg_return_rate,
               ROUND(SUM(price_usd * units_sold), 0) AS est_revenue
        FROM `{TABLE_NAME}`
        GROUP BY style
        ORDER BY total_sales DESC
        LIMIT 15
    """
    return jsend(query_all(sql))


# ─────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    db_ok = False
    try:
        query_one(f"SELECT 1 AS ok FROM `{TABLE_NAME}` LIMIT 1")
        db_ok = True
    except Exception:
        pass
    return jsend({
        "status":       "ok" if db_ok else "degraded",
        "db":           "connected" if db_ok else "error",
        "models_ready": models_ready(),
        "models_loaded": list(MODELS.keys()),
    })


# ─────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e): return jsend({"error": "Not found"}, 404)

@app.errorhandler(500)
def server_error(e): return jsend({"error": str(e)}, 500)

@app.errorhandler(MySQLError)
def db_error(e): return jsend({"error": f"Database error: {e}"}, 503)


# ─────────────────────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🚀 FASHIONPULSE AI — Starting Server")
    print("=" * 60)
    load_models()
    if models_ready():
        print("  ✅ ML models loaded")
    else:
        print("  ⚠️  No ML models found — run train_models.py first")
    print(f"  📡 http://localhost:{FLASK_PORT}")
    print("=" * 60 + "\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
