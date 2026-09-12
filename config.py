# ============================================================
# FASHIONPULSE AI — Configuration
# ============================================================

import os

# ── MySQL Database ──────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "Kri&Satya$19@sql",
    "database": "FashionPulse_AI",
    "port":     3306,
    "charset":  "utf8mb4",
    "autocommit": True,
}

# Database name (used during creation)
DB_NAME = "FashionPulse_AI"

def get_db_connection(with_db: bool = True):
    """Returns a MySQL connection using mysql.connector or pymysql as fallback."""
    cfg = dict(DB_CONFIG)
    if not with_db:
        cfg.pop("database", None)
    
    # Remove autocommit if present in dict for pymysql compatibility handling
    autocommit = cfg.pop("autocommit", True)

    try:
        import mysql.connector
        conn = mysql.connector.connect(**cfg)
        conn.autocommit = autocommit
        return conn
    except ImportError:
        import pymysql
        # Map charset to charset parameter
        conn = pymysql.connect(
            host=cfg.get("host", "localhost"),
            user=cfg.get("user", "root"),
            password=cfg.get("password", ""),
            database=cfg.get("database") if with_db else None,
            port=cfg.get("port", 3306),
            charset=cfg.get("charset", "utf8mb4"),
            autocommit=autocommit,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn


def get_dict_cursor(conn):
    """Returns a dictionary cursor compatible with both mysql-connector and pymysql."""
    try:
        return conn.cursor(dictionary=True)
    except Exception:
        return conn.cursor()


# ── File Paths ──────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

CSV_FILE  = os.path.join(DATA_DIR, "women_clothing_50k.csv")

# ── Table name ──────────────────────────────────────────────
TABLE_NAME = "products"

# ── ML Settings ─────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE    = 0.2
CV_FOLDS     = 5

# Tertile thresholds for performance classification
# Set dynamically during training — stored here after
SALES_LOW_THRESHOLD  = None
SALES_HIGH_THRESHOLD = None

# Return-rate binary threshold (percentile)
RETURN_RISK_PERCENTILE = 75

# K-Means clusters
N_CLUSTERS = 4

# ── Flask ────────────────────────────────────────────────────
FLASK_HOST  = "0.0.0.0"
FLASK_PORT  = 5000
FLASK_DEBUG = False

# ── Colour palette (used in chart configs) ───────────────────
CHART_COLORS = [
    "#7C3AED", "#06B6D4", "#10B981", "#F59E0B",
    "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6",
    "#F97316", "#6366F1",
]
