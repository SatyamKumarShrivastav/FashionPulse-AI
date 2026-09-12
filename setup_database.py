"""
╔══════════════════════════════════════════════════════════════╗
║         FASHIONPULSE AI — Database Setup Script              ║
║         Loads women_clothing_50k.csv → MySQL                 ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python setup_database.py

Steps:
    1. Creates the FashionPulse_AI database
    2. Creates the products table
    3. Loads the CSV file into MySQL (batch insert)
    4. Verifies row count
"""

import os
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass



# ── Adjust path to pick up config ─────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG, DB_NAME, CSV_FILE, TABLE_NAME, get_db_connection, get_dict_cursor


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def banner(msg: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {msg}")
    print("=" * 60)


def connect(with_db: bool = True):
    return get_db_connection(with_db=with_db)



# ─────────────────────────────────────────────────────────────
# STEP 1 — CREATE DATABASE
# ─────────────────────────────────────────────────────────────

def create_database() -> None:
    banner("STEP 1 — Create Database")
    try:
        conn = connect(with_db=False)
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        conn.commit()
        print(f"  ✅ Database `{DB_NAME}` is ready.")
    except Exception as e:
        print(f"  ❌ Error creating database: {e}")
        sys.exit(1)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
# STEP 2 — CREATE TABLE
# ─────────────────────────────────────────────────────────────

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    product_id       VARCHAR(50)     NOT NULL,
    category         VARCHAR(100),
    subcategory      VARCHAR(100),
    material         VARCHAR(100),
    color            VARCHAR(50),
    size             VARCHAR(20),
    season           VARCHAR(30),
    style            VARCHAR(100),
    price_usd        DECIMAL(10, 2),
    discount_percent DECIMAL(5,  2),
    rating           DECIMAL(3,  2),
    review_count     INT,
    stock_quantity   INT,
    units_sold       INT,
    return_rate      DECIMAL(6,  2),
    INDEX idx_category   (category),
    INDEX idx_season     (season),
    INDEX idx_style      (style),
    INDEX idx_units_sold (units_sold),
    INDEX idx_return_rate(return_rate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def create_table() -> None:
    banner("STEP 2 — Create Table")
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        print(f"  ✅ Table `{TABLE_NAME}` is ready.")
    except Exception as e:
        print(f"  ❌ Error creating table: {e}")
        sys.exit(1)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
# STEP 3 — LOAD CSV
# ─────────────────────────────────────────────────────────────

INSERT_SQL = f"""
    INSERT INTO `{TABLE_NAME}`
        (product_id, category, subcategory, material, color,
         size, season, style, price_usd, discount_percent,
         rating, review_count, stock_quantity, units_sold, return_rate)
    VALUES
        (%s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s)
"""

def load_csv() -> None:
    banner("STEP 3 — Load CSV Data")
    import csv

    if not os.path.exists(CSV_FILE):
        print(f"\n  ❌ CSV not found at:\n     {CSV_FILE}")
        print("\n  Please copy women_clothing_50k.csv into the /data folder.")
        sys.exit(1)

    print(f"  📂 Reading: {CSV_FILE}")
    rows_to_insert = []
    with open(CSV_FILE, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Normalise column headers
        field_map = {
            col: col.strip().lower().replace(" ", "_").replace("-", "_")
            for col in (reader.fieldnames or [])
        }
        for row in reader:
            norm_row = {field_map[k]: v for k, v in row.items() if k in field_map}
            
            def parse_float(v):
                try: return float(v) if v is not None and v != "" else None
                except Exception: return None
                
            def parse_int(v):
                try: return int(float(v)) if v is not None and v != "" else None
                except Exception: return None

            rows_to_insert.append((
                norm_row.get("product_id", "").strip(),
                norm_row.get("category", "").strip(),
                norm_row.get("subcategory", "").strip(),
                norm_row.get("material", "").strip(),
                norm_row.get("color", "").strip(),
                norm_row.get("size", "").strip(),
                norm_row.get("season", "").strip(),
                norm_row.get("style", "").strip(),
                parse_float(norm_row.get("price_usd")),
                parse_float(norm_row.get("discount_percent")),
                parse_float(norm_row.get("rating")),
                parse_int(norm_row.get("review_count")),
                parse_int(norm_row.get("stock_quantity")),
                parse_int(norm_row.get("units_sold")),
                parse_float(norm_row.get("return_rate"))
            ))

    print(f"  📊 Parsed: {len(rows_to_insert):,} rows")

    # ── Check for existing data ─────────────────────────────
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM `{TABLE_NAME}`")
    row = cursor.fetchone()
    existing = list(row.values())[0] if isinstance(row, dict) else row[0]

    if existing > 0:
        print(f"\n  ⚠️  Table already has {existing:,} rows. Truncating for fresh import...")
        cursor.execute(f"TRUNCATE TABLE `{TABLE_NAME}`")
        conn.commit()
        print("  🗑️  Table truncated.")

    # ── Batch insert ────────────────────────────────────────
    BATCH_SIZE = 5000
    print(f"\n  ⬆️  Inserting {len(rows_to_insert):,} rows in batches of {BATCH_SIZE:,}…")

    start = time.time()
    inserted = 0
    for i in range(0, len(rows_to_insert), BATCH_SIZE):
        batch = rows_to_insert[i : i + BATCH_SIZE]
        cursor.executemany(INSERT_SQL, batch)
        conn.commit()
        inserted += len(batch)
        pct = inserted / len(rows_to_insert) * 100
        print(f"  Processed {inserted:,}/{len(rows_to_insert):,} rows ({pct:.1f}%)")

    elapsed = time.time() - start
    print(f"\n  ✅ Inserted {inserted:,} rows in {elapsed:.1f}s")

    cursor.close()
    conn.close()


# ─────────────────────────────────────────────────────────────
# STEP 4 — VERIFY
# ─────────────────────────────────────────────────────────────

def verify() -> None:
    banner("STEP 4 — Verification")
    conn = connect()
    cursor = get_dict_cursor(conn)

    cursor.execute(f"SELECT COUNT(*) AS total FROM `{TABLE_NAME}`")
    row = cursor.fetchone()
    total = row["total"] if isinstance(row, dict) else row[0]

    cursor.execute(f"""
        SELECT
            AVG(price_usd)        AS avg_price,
            AVG(units_sold)       AS avg_sales,
            AVG(rating)           AS avg_rating,
            AVG(return_rate)      AS avg_return,
            MIN(units_sold)       AS min_sales,
            MAX(units_sold)       AS max_sales,
            COUNT(DISTINCT category) AS categories
        FROM `{TABLE_NAME}`
    """)
    stats = cursor.fetchone()

    print(f"\n  Total rows    : {total:,}")
    print(f"  Avg price (USD): {float(stats['avg_price']):.2f}")
    print(f"  Avg sales      : {float(stats['avg_sales']):.1f}")
    print(f"  Avg rating     : {float(stats['avg_rating']):.2f}")
    print(f"  Avg return %   : {float(stats['avg_return']):.2f}")
    print(f"  Sales range    : {stats['min_sales']} – {stats['max_sales']}")
    print(f"  Categories     : {stats['categories']}")
    print("\n  ✅ Database setup complete!")

    cursor.close()
    conn.close()



# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    banner("🚀 FASHIONPULSE AI — Database Setup")
    print(f"  Host  : {DB_CONFIG['host']}")
    print(f"  User  : {DB_CONFIG['user']}")
    print(f"  DB    : {DB_NAME}")

    create_database()
    create_table()
    load_csv()
    verify()

    banner("🎉 SETUP COMPLETE")
    print("  You can now run:  python train_models.py")
