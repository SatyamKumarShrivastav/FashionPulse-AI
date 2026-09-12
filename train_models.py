"""
╔══════════════════════════════════════════════════════════════╗
║        FASHIONPULSE AI — ML Model Training Script           ║
╚══════════════════════════════════════════════════════════════╝

Trains 4 models:
  1. Sales Predictor        (regression   → units_sold)
  2. Performance Classifier (multiclass   → High/Med/Low)
  3. Return Risk Predictor  (binary class → high_risk)
  4. Product Segmenter      (K-Means clustering)

Usage:
    python train_models.py

Outputs saved to /models/
"""

import os
import sys
import json
import warnings
import numpy  as np
import pandas as pd
import joblib
import mysql.connector

from sklearn.model_selection   import train_test_split, cross_val_score
from sklearn.preprocessing     import LabelEncoder, StandardScaler
from sklearn.compose           import ColumnTransformer
from sklearn.pipeline          import Pipeline
from sklearn.preprocessing     import OneHotEncoder
from sklearn.impute            import SimpleImputer

from sklearn.linear_model      import Ridge, LogisticRegression
from sklearn.ensemble          import (
    RandomForestRegressor, GradientBoostingRegressor,
    RandomForestClassifier, GradientBoostingClassifier,
)
from sklearn.cluster           import KMeans
from sklearn.metrics           import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, f1_score, silhouette_score,
)

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    DB_CONFIG, TABLE_NAME, MODEL_DIR, RANDOM_STATE,
    TEST_SIZE, CV_FOLDS, N_CLUSTERS, RETURN_RISK_PERCENTILE,
)

# ── Optional advanced models ────────────────────────────────
try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_OK = True
except ImportError:
    XGBOOST_OK = False

try:
    from lightgbm import LGBMRegressor, LGBMClassifier
    LIGHTGBM_OK = True
except ImportError:
    LIGHTGBM_OK = False


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def banner(msg: str) -> None:
    print("\n" + "=" * 62)
    print(f"  {msg}")
    print("=" * 62)


os.makedirs(MODEL_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    banner("Loading data from MySQL …")
    try:
        from urllib.parse import quote_plus
        from sqlalchemy import create_engine
        cfg = DB_CONFIG
        user = quote_plus(str(cfg['user']))
        password = quote_plus(str(cfg['password']))
        host = cfg['host']
        port = cfg.get('port', 3306)
        database = cfg['database']
        charset = cfg.get('charset', 'utf8mb4')
        url = (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            f"?charset={quote_plus(charset)}"
        )
        engine = create_engine(url)
        df = pd.read_sql(f"SELECT * FROM `{TABLE_NAME}`", engine)
        engine.dispose()
    except ImportError:
        # Fallback: direct mysql.connector (pandas < 2.0 compatible)
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{TABLE_NAME}`")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        cursor.close()
        conn.close()
    print(f"  ✅ {len(df):,} rows loaded")
    return df


# ─────────────────────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────

CAT_FEATURES = [
    "category", "subcategory", "material",
    "color", "size", "season", "style",
]
NUM_FEATURES = ["price_usd", "discount_percent"]
ALL_FEATURES = CAT_FEATURES + NUM_FEATURES


def build_preprocessor() -> ColumnTransformer:
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("ohe",     OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])
    return ColumnTransformer([
        ("cat", cat_pipe, CAT_FEATURES),
        ("num", num_pipe, NUM_FEATURES),
    ], remainder="drop")


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["gross_sales_value"]    = df["price_usd"] * df["units_sold"]
    df["discounted_price"]     = df["price_usd"] * (1 - df["discount_percent"] / 100)
    df["inv_sales_ratio"]      = df["stock_quantity"] / (df["units_sold"] + 1)
    df["est_returned_units"]   = df["units_sold"] * df["return_rate"] / 100
    return df


# ─────────────────────────────────────────────────────────────
# MODEL 1 — SALES PREDICTION (REGRESSION)
# ─────────────────────────────────────────────────────────────

def train_sales_model(df: pd.DataFrame) -> dict:
    banner("MODEL 1 — Sales Predictor (Regression)")

    X = df[ALL_FEATURES]
    y = np.log1p(df["units_sold"])          # log-transform skewed target

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    pre = build_preprocessor()

    candidates = {
        "Ridge": Ridge(alpha=10),
        "RandomForest": RandomForestRegressor(
            n_estimators=200, max_depth=12,
            min_samples_leaf=5, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200, max_depth=5, learning_rate=0.05,
            subsample=0.8, random_state=RANDOM_STATE
        ),
    }
    if XGBOOST_OK:
        candidates["XGBoost"] = XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, n_jobs=-1, verbosity=0
        )
    if LIGHTGBM_OK:
        candidates["LightGBM"] = LGBMRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, n_jobs=-1, verbose=-1
        )

    results = {}
    best_name, best_pipe, best_r2 = None, None, -np.inf

    for name, model in candidates.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)

        # back-transform
        y_pred_orig = np.expm1(y_pred)
        y_te_orig   = np.expm1(y_te)

        mae  = mean_absolute_error(y_te_orig, y_pred_orig)
        rmse = np.sqrt(mean_squared_error(y_te_orig, y_pred_orig))
        r2   = r2_score(y_te_orig, y_pred_orig)

        results[name] = {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "R2": round(r2, 4)}
        print(f"  {name:20s}  MAE={mae:7.2f}  RMSE={rmse:8.2f}  R²={r2:.4f}")

        if r2 > best_r2:
            best_r2, best_name, best_pipe = r2, name, pipe

    print(f"\n  🏆 Best model: {best_name}  (R²={best_r2:.4f})")

    # Feature importance
    feat_names = list(
        best_pipe.named_steps["pre"]
        .get_feature_names_out()
    )
    try:
        raw_model = best_pipe.named_steps["model"]
        if hasattr(raw_model, "feature_importances_"):
            imp = raw_model.feature_importances_
        elif hasattr(raw_model, "coef_"):
            imp = np.abs(raw_model.coef_)
        else:
            imp = np.zeros(len(feat_names))

        top_n = 20
        top_idx = np.argsort(imp)[-top_n:][::-1]
        feat_imp = [
            {"feature": feat_names[i], "importance": round(float(imp[i]), 6)}
            for i in top_idx
        ]
    except Exception:
        feat_imp = []

    joblib.dump(best_pipe, os.path.join(MODEL_DIR, "sales_model.pkl"))
    print(f"  💾 Saved: models/sales_model.pkl")

    return {
        "model_results": results,
        "best_model": best_name,
        "best_r2": best_r2,
        "feature_importance": feat_imp,
    }


# ─────────────────────────────────────────────────────────────
# MODEL 2 — PERFORMANCE CLASSIFIER
# ─────────────────────────────────────────────────────────────

def train_classifier(df: pd.DataFrame) -> dict:
    banner("MODEL 2 — Performance Classifier (High / Mid / Low)")

    q33 = df["units_sold"].quantile(0.33)
    q66 = df["units_sold"].quantile(0.66)

    def label(v):
        if v >= q66:
            return "High Performer"
        elif v >= q33:
            return "Mid Performer"
        else:
            return "Low Performer"

    df = df.copy()
    df["perf_class"] = df["units_sold"].apply(label)

    X = df[ALL_FEATURES]
    y = df["perf_class"]

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y_enc, test_size=TEST_SIZE,
        stratify=y_enc, random_state=RANDOM_STATE
    )

    pre = build_preprocessor()

    candidates = {
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.05,
            random_state=RANDOM_STATE
        ),
    }
    if XGBOOST_OK:
        candidates["XGBoost"] = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            random_state=RANDOM_STATE, n_jobs=-1, verbosity=0,
            eval_metric="mlogloss"
        )

    results = {}
    best_name, best_pipe, best_f1 = None, None, -np.inf

    for name, model in candidates.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)
        acc = accuracy_score(y_te, y_pred)
        f1  = f1_score(y_te, y_pred, average="weighted")
        results[name] = {"Accuracy": round(acc, 4), "F1": round(f1, 4)}
        print(f"  {name:20s}  Acc={acc:.4f}  F1={f1:.4f}")
        if f1 > best_f1:
            best_f1, best_name, best_pipe = f1, name, pipe

    print(f"\n  🏆 Best model: {best_name}  (F1={best_f1:.4f})")

    joblib.dump(best_pipe,  os.path.join(MODEL_DIR, "classifier_model.pkl"))
    joblib.dump(le,         os.path.join(MODEL_DIR, "classifier_label_encoder.pkl"))
    print("  💾 Saved: models/classifier_model.pkl")

    return {
        "model_results": results,
        "best_model": best_name,
        "best_f1": best_f1,
        "thresholds": {"q33": round(q33, 2), "q66": round(q66, 2)},
        "classes": list(le.classes_),
    }


# ─────────────────────────────────────────────────────────────
# MODEL 3 — RETURN RISK CLASSIFIER
# ─────────────────────────────────────────────────────────────

def train_return_risk(df: pd.DataFrame) -> dict:
    banner("MODEL 3 — Return Risk Predictor (Binary)")

    threshold = df["return_rate"].quantile(RETURN_RISK_PERCENTILE / 100)
    df = df.copy()
    df["high_return_risk"] = (df["return_rate"] >= threshold).astype(int)

    X = df[ALL_FEATURES]
    y = df["high_return_risk"]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=TEST_SIZE,
        stratify=y, random_state=RANDOM_STATE
    )

    pre = build_preprocessor()

    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=500, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=RANDOM_STATE, n_jobs=-1
        ),
    }
    if XGBOOST_OK:
        candidates["XGBoost"] = XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.05,
            random_state=RANDOM_STATE, verbosity=0,
            eval_metric="logloss"
        )

    results = {}
    best_name, best_pipe, best_f1 = None, None, -np.inf

    for name, model in candidates.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)
        acc = accuracy_score(y_te, y_pred)
        f1  = f1_score(y_te, y_pred)
        results[name] = {"Accuracy": round(acc, 4), "F1": round(f1, 4)}
        print(f"  {name:20s}  Acc={acc:.4f}  F1={f1:.4f}")
        if f1 > best_f1:
            best_f1, best_name, best_pipe = f1, name, pipe

    print(f"\n  🏆 Best model: {best_name}  (F1={best_f1:.4f})")

    joblib.dump(best_pipe, os.path.join(MODEL_DIR, "return_risk_model.pkl"))
    print("  💾 Saved: models/return_risk_model.pkl")

    return {
        "model_results": results,
        "best_model": best_name,
        "best_f1": best_f1,
        "risk_threshold": round(float(threshold), 2),
    }


# ─────────────────────────────────────────────────────────────
# MODEL 4 — PRODUCT SEGMENTATION (K-MEANS)
# ─────────────────────────────────────────────────────────────

CLUSTER_FEATURES = [
    "price_usd", "discount_percent", "rating",
    "review_count", "units_sold", "return_rate",
]

CLUSTER_NAMES = {
    0: "Premium High Performers",
    1: "Discount-Driven Products",
    2: "Low Demand Products",
    3: "High Return Risk Products",
}


def train_segmenter(df: pd.DataFrame) -> dict:
    banner("MODEL 4 — Product Segmenter (K-Means)")

    X = df[CLUSTER_FEATURES].fillna(df[CLUSTER_FEATURES].median())
    scaler = StandardScaler()
    Xs     = scaler.fit_transform(X)

    kmeans = KMeans(
        n_clusters=N_CLUSTERS, random_state=RANDOM_STATE,
        n_init=10, max_iter=300
    )
    labels = kmeans.fit_predict(Xs)
    sil    = silhouette_score(Xs, labels, sample_size=5000, random_state=RANDOM_STATE)

    df = df.copy()
    df["cluster"] = labels

    # Profile each cluster
    profiles = {}
    for c in range(N_CLUSTERS):
        sub = df[df["cluster"] == c]
        profiles[c] = {
            "count":        int(len(sub)),
            "avg_price":    round(float(sub["price_usd"].mean()), 2),
            "avg_discount": round(float(sub["discount_percent"].mean()), 2),
            "avg_rating":   round(float(sub["rating"].mean()), 2),
            "avg_sales":    round(float(sub["units_sold"].mean()), 2),
            "avg_return":   round(float(sub["return_rate"].mean()), 2),
            "name":         CLUSTER_NAMES.get(c, f"Segment {c}"),
        }

    print(f"  Silhouette score: {sil:.4f}")
    for c, p in profiles.items():
        print(f"  Cluster {c} ({p['name']}): {p['count']:,} products")

    joblib.dump({"kmeans": kmeans, "scaler": scaler}, os.path.join(MODEL_DIR, "segmenter.pkl"))
    print("  💾 Saved: models/segmenter.pkl")

    return {
        "silhouette": round(float(sil), 4),
        "profiles":   profiles,
        "cluster_features": CLUSTER_FEATURES,
        "n_clusters": N_CLUSTERS,
    }


# ─────────────────────────────────────────────────────────────
# SAVE METRICS MANIFEST
# ─────────────────────────────────────────────────────────────

def save_manifest(metrics: dict) -> None:
    path = os.path.join(MODEL_DIR, "metrics.json")
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  💾 Metrics saved: {path}")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    banner("🚀 FASHIONPULSE AI — Model Training")
    print(f"  XGBoost  : {'✅' if XGBOOST_OK  else '❌ not installed'}")
    print(f"  LightGBM : {'✅' if LIGHTGBM_OK else '❌ not installed'}")

    df = load_data()
    df = engineer(df)

    metrics = {}

    metrics["sales"]       = train_sales_model(df)
    metrics["classifier"]  = train_classifier(df)
    metrics["return_risk"] = train_return_risk(df)
    metrics["segmenter"]   = train_segmenter(df)

    save_manifest(metrics)

    banner("🎉 ALL MODELS TRAINED AND SAVED")
    print("  You can now run:  python app.py")
    print("  Then open:        http://localhost:5000\n")
