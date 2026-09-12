"""
FashionPulse AI - Diagnostic Script
Checks: Python, packages, MySQL connectivity
"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print(f"Python: {sys.version}\n")

# -- Package checks -------------------------------------------
packages = [
    ("flask",                  "Flask"),
    ("flask_cors",             "Flask-CORS"),
    ("pandas",                 "pandas"),
    ("numpy",                  "numpy"),
    ("sklearn",                "scikit-learn"),
    ("joblib",                 "joblib"),
    ("sqlalchemy",             "SQLAlchemy"),
    ("pymysql",                "PyMySQL"),
]


print("Checking Core Packages:")
all_ok = True
for mod, name in packages:
    try:
        m = __import__(mod)
        ver = getattr(m, "__version__", getattr(m, "VERSION", "ok"))
        print(f"  [OK] {name:25s} {ver}")
    except ImportError:
        print(f"  [MISSING] {name:25s}")
        all_ok = False

# Optional
for mod, name in [("xgboost","XGBoost"),("lightgbm","LightGBM")]:
    try:
        m = __import__(mod)
        ver = getattr(m, "__version__", "ok")
        print(f"  [OK] {name:25s} {ver}")
    except ImportError:
        print(f"  [WARN] {name:25s} not installed (optional)")

print()

# -- MySQL connectivity ---------------------------------------
sys.path.insert(0, ".")
from config import DB_CONFIG, DB_NAME, get_db_connection

print(f"MySQL host  : {DB_CONFIG['host']}")

print(f"MySQL user  : {DB_CONFIG['user']}")
print(f"MySQL DB    : {DB_NAME}")
print()

try:
    conn = get_db_connection(with_db=False)
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    row = cursor.fetchone()
    ver = row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]
    print(f"  [OK] MySQL server: {ver}")

    # Check database
    cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
    exists = cursor.fetchone()
    if exists:
        conn_db = get_db_connection(with_db=True)
        cursor_db = conn_db.cursor()
        cursor_db.execute("SELECT COUNT(*) FROM products")
        r = cursor_db.fetchone()
        count = r[0] if isinstance(r, (tuple, list)) else list(r.values())[0]
        print(f"  [OK] Database '{DB_NAME}' exists")
        print(f"  [OK] products table: {count:,} rows")
        cursor_db.close()
        conn_db.close()
    else:
        print(f"  [WARN] Database '{DB_NAME}' does NOT exist yet -> run setup_database.py")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"  [FAIL] MySQL error: {e}")
    all_ok = False


print()
print("=" * 50)
if all_ok:
    print("STATUS: Ready to run setup / server!")
else:
    print("STATUS: Missing required dependencies or MySQL connection issue")
print("=" * 50)
