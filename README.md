# 👗 FashionPulse AI - Sales Trends, Customer Behavior & Predictive Intelligence

### Sales Intelligence • Product Analytics • Predictive AI • Business Decisions

<p align="center">

**Turning 50,000 fashion products into actionable business intelligence.**

<br>

<a href="#-project-highlights">Highlights</a> • <a href="#-architecture">Architecture</a> • <a href="#-dashboard-story">Dashboard</a> • <a href="#-ai--machine-learning">AI & ML</a> • <a href="#-installation">Installation</a> • <a href="#-future-scope">Future Scope</a>

</p>

---

## 🚀 What is FashionPulse AI?

**FashionPulse AI** is an end-to-end **Business Intelligence and Predictive Analytics platform** built for a women's fashion e-commerce catalog.

It transforms raw product data into a complete decision-support system by combining:

**Data → SQL Analytics → APIs → Interactive Dashboard → Machine Learning → Business Recommendations**

The platform analyzes **50,000 product records** across product attributes, pricing, discounts, sales, ratings, inventory, and returns.

Instead of simply showing charts, FashionPulse AI answers a more important question:

> ### **"What is happening, what might happen next, and what should the business do?"**

---

# ✨ Project Highlights

| Capability                        | What FashionPulse AI Provides                   |
| --------------------------------- | ----------------------------------------------- |
| 📦 **50K Products**               | Analytics across 50,000 fashion catalog records |
| 🗄️ **MySQL Database**            | Structured and queryable product data           |
| 🔎 **SQL Analytics**              | Business-focused analytical endpoints           |
| 🌐 **Flask REST API**             | Connects the data layer with the dashboard      |
| 📊 **Interactive Dashboard**      | Five business intelligence views                |
| 🤖 **Sales Prediction**           | Predicts expected product sales                 |
| 🏆 **Performance Classification** | High / Mid / Low performer identification       |
| ⚠️ **Return Risk**                | Identifies products with elevated return risk   |
| 🧩 **Product Segmentation**       | Groups products using K-Means clustering        |
| 💡 **Business Recommendations**   | Converts analytics into suggested actions       |

---

# 🎯 The Business Problem

Fashion e-commerce businesses generate large amounts of product and sales-related data.

But raw data alone does not answer important business questions.

FashionPulse AI addresses questions such as:

* 📈 Which categories and products perform best?
* 👗 Which styles and subcategories generate stronger sales?
* 💰 What price bands are associated with better performance?
* 🏷️ How do discount levels relate to observed sales?
* 📦 Which products require restocking attention?
* ⚠️ Which products have elevated return risk?
* 🏆 Which products are high performers?
* 🧩 Which products belong to similar business segments?
* 🔮 What sales/performance outcome might a new product receive?
* 💡 What business action should be considered?

The objective is to move from:

> **Raw Data → Information → Insight → Prediction → Action**

---

# 🧠 How the System Thinks

FashionPulse AI follows a four-layer analytical approach.

### 01 — DESCRIPTIVE

### **What is happening?**

KPIs, category performance, product rankings, pricing, inventory and return analysis.

↓

### 02 — DIAGNOSTIC

### **What patterns are associated with performance?**

Price, discounts, categories, styles, seasons, materials, sizes and other product attributes.

↓

### 03 — PREDICTIVE

### **What might happen?**

Machine-learning models estimate sales, classify performance, assess return risk and segment products.

↓

### 04 — PRESCRIPTIVE

### **What should we do?**

The system translates analytical signals into business-oriented recommendations.

---

# 🏗️ Architecture

```text
                    ┌──────────────────────────┐
                    │   women_clothing_50k.csv │
                    │       50,000 Products     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     Data Preparation      │
                    │  Normalize • Validate     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     MySQL Database        │
                    │     FashionPulse_AI       │
                    │         products          │
                    └────────────┬─────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
        ┌──────────────────┐          ┌────────────────────┐
        │  SQL / BI Layer  │          │   ML Training       │
        │                  │          │                    │
        │ KPIs             │          │ Sales Regression   │
        │ Categories       │          │ Performance Class. │
        │ Pricing          │          │ Return Risk        │
        │ Inventory        │          │ K-Means Segments   │
        │ Returns          │          │                    │
        └────────┬─────────┘          └─────────┬──────────┘
                 │                              │
                 ▼                              ▼
        ┌─────────────────────────────────────────────┐
        │                Flask REST API               │
        │       Analytics + Prediction Endpoints      │
        └──────────────────────┬──────────────────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │      Interactive Dashboard     │
              │                                │
              │ Executive Overview             │
              │ Product Performance            │
              │ Pricing Intelligence            │
              │ Inventory & Returns            │
              │ AI Predictions                 │
              └────────────────────────────────┘
```

---

# 📊 Dashboard Story

FashionPulse AI is designed around a **business storytelling journey**, not a collection of disconnected charts.

## 01 — Executive Overview

### **"How is the business performing?"**

Provides the management-level picture.

**Key areas**

* Total products
* Units sold
* Estimated sales value
* Average price
* Average rating
* Average discount
* Inventory
* Return rate
* Category and season performance
* Top products

**Business question:**

> Where should management look first?

---

## 02 — Product Performance

### **"Which products are winning?"**

Moves from overall performance to individual product intelligence.

**Analysis includes**

* Top products
* Bottom products
* Category performance
* Subcategory performance
* Style performance
* Performance classes
* Predicted performance

**Business question:**

> Which products should receive greater attention?

---

## 03 — Pricing Intelligence

### **"How do price and discounts relate to demand?"**

Explores the relationship between pricing decisions and observed sales performance.

**Analysis includes**

* Price distribution
* Price bands
* Discount bands
* Sales by price segment
* Sales by discount segment
* Category × pricing analysis

**Important analytical principle:**

> The dashboard identifies **associations**, not causal effects.

---

## 04 — Inventory & Returns

### **"Where are the operational risks?"**

Connects sales performance with inventory and return behavior.

**Analysis includes**

* Inventory health
* Out-of-stock products
* Restock opportunities
* Overstock situations
* Return rates
* High-return products
* Return analysis by category, material and size

**Business question:**

> Where could the business be losing opportunity through inventory or returns?

---

## 05 — AI Predictions

### **"What should the business do next?"**

The final layer combines machine-learning predictions with business interpretation.

**Includes**

* Sales prediction
* Performance classification
* Return-risk probability
* Product segmentation
* Feature importance
* Business recommendations

**Business question:**

> What action should be considered?

---

# 🤖 AI & Machine Learning

FashionPulse AI contains **four predictive workflows**.

## 📈 1. Sales Prediction

Predicts:

> **`units_sold`**

The target is log-transformed to better handle the highly skewed sales distribution.

Candidate models include:

* Ridge Regression
* Random Forest
* Gradient Boosting
* XGBoost *(optional)*
* LightGBM *(optional)*

Model selection uses holdout performance metrics.

---

## 🏆 2. Performance Classification

Products are classified into:

```text
High Performer
Mid Performer
Low Performer
```

The classes are generated using sales tertiles.

Candidate models include:

* Random Forest
* Gradient Boosting
* XGBoost *(optional)*

Evaluation includes:

* Accuracy
* Precision
* Recall
* F1
* ROC-AUC where applicable

---

## ⚠️ 3. Return-Risk Prediction

Products at or above the **75th percentile of return rate** are identified as high return risk.

The model evaluates product characteristics and pricing information to estimate return-risk probability.

Potential models include:

* Logistic Regression
* Random Forest
* XGBoost *(optional)*

---

## 🧩 4. Product Segmentation

K-Means clustering groups products based on characteristics such as:

* Price
* Discount
* Rating
* Reviews
* Units sold
* Return rate

The configured business segments include:

```text
Premium High Performers
Discount-Driven Products
Low Demand Products
High Return Risk Products
```

The purpose is not merely to create clusters, but to translate those clusters into **business-oriented product groups**.

---

# 🔐 Leakage Control

A major design principle is avoiding obvious post-outcome information when building sales and classification predictors.

The prediction feature set avoids variables such as:

* `review_count`
* `stock_quantity`
* Post-sale outcome information

This keeps the prediction inputs closer to information that could be available before the sales outcome is observed.

---

# 💰 Estimated Sales Value

FashionPulse AI calculates:

```text
Estimated Sales Value
=
price_usd × units_sold
```

### ⚠️ Important

This is an **analytical estimate**, not verified accounting revenue.

It does not account for:

* Refunds
* Taxes
* Shipping
* Cost of goods
* Payment fees
* Currency conversion

Therefore, project dashboards should interpret this metric as **Estimated Sales Value**, not audited revenue.

---

# 🔌 REST API

The Flask application exposes analytical and AI functionality through REST endpoints.

### Operational

```text
GET /api/health
```

### Business Analytics

```text
GET /api/kpis
GET /api/sales-by-category
GET /api/sales-by-season
GET /api/top-products
GET /api/category-performance
GET /api/style-performance
GET /api/price-analysis
GET /api/discount-analysis
GET /api/inventory-matrix
GET /api/return-analysis
```

### AI

```text
POST /api/predict
POST /api/segment
GET  /api/model-performance
GET  /api/feature-importance
```

---

# 🛠️ Technology Stack

### Data & Analytics

* 🐍 Python
* 🐼 Pandas
* 🔢 NumPy
* 📐 SciPy
* 🧮 SQL

### Database

* 🐬 MySQL

### Backend

* 🌐 Flask
* 🔗 Flask-CORS
* SQLAlchemy
* PyMySQL
* MySQL Connector

### Machine Learning

* Scikit-learn
* XGBoost
* LightGBM
* Joblib

### Frontend

* HTML
* CSS
* Vanilla JavaScript
* Chart.js

---

# 📁 Project Structure

```text
FashionPulse AI/
│
├── app.py
├── config.py
├── diagnose.py
├── setup_database.py
├── train_models.py
├── requirements.txt
├── run.bat
├── README.md
│
├── data/
│   └── women_clothing_50k.csv
│
├── models/
│   ├── sales_model.pkl
│   ├── classifier_model.pkl
│   ├── classifier_label_encoder.pkl
│   ├── return_risk_model.pkl
│   ├── segmenter.pkl
│   └── metrics.json
│
├── outputs/
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── main.js
│       ├── dashboard.js
│       ├── products.js
│       ├── pricing.js
│       ├── inventory.js
│       └── ai_predictions.js
│
└── templates/
    └── index.html
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "FashionPulse AI"
```

## 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

Recommended:

```text
Python 3.10+
MySQL Server 8.x
```

---

# 🗄️ Database Setup

Configure your MySQL connection in:

```text
config.py
```

Default configuration:

```text
Host     : localhost
Port     : 3306
User     : root
Database : FashionPulse_AI
Table    : products
Charset  : utf8mb4
```

Place the dataset here:

```text
data/women_clothing_50k.csv
```

Then run:

```bash
python setup_database.py
```

The setup script creates the database/table, normalizes the dataset, converts numeric fields, imports records in batches, and performs verification checks.

---

# 🤖 Train the Models

After the database has been populated:

```bash
python train_models.py
```

The trained artifacts are stored inside:

```text
models/
```

The training process produces:

```text
sales_model.pkl
classifier_model.pkl
classifier_label_encoder.pkl
return_risk_model.pkl
segmenter.pkl
metrics.json
```

---

# 🌐 Run the Dashboard

Start the Flask application:

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

You can also use:

```bash
run.bat
```

on Windows.

---

# 🔍 Health Check

Before using the dashboard, verify:

```text
GET /api/health
```

A healthy system should report database connectivity and model availability.

If models are trained while Flask is already running, restart Flask so the newly generated model artifacts are loaded.

---

# 📦 Dataset

The project uses a **50,000-row women's fashion catalog**.

Main fields include:

```text
product_id
category
subcategory
material
color
size
season
style
price_usd
discount_percent
rating
review_count
stock_quantity
units_sold
return_rate
```

---

# 🧭 Project Workflow

```text
             RAW DATA
                │
                ▼
        Data Understanding
                │
                ▼
       Data Preparation
                │
                ▼
         MySQL Database
                │
                ▼
        SQL Analytics
                │
                ▼
         Flask REST API
                │
        ┌───────┴────────┐
        ▼                ▼
   Dashboard         ML Pipeline
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
            Sales      Risk       Segment
              │          │          │
              └──────────┼──────────┘
                         ▼
                  AI Intelligence
                         │
                         ▼
                 Business Actions
```

---

# 💡 From Analytics to Action

FashionPulse AI is designed to turn analytical signals into practical business actions.

| Signal                                 | Possible Business Response   |
| -------------------------------------- | ---------------------------- |
| 🏆 High performance + Low risk         | **Prioritize / Restock**     |
| 🏆 High performance + High return risk | **Investigate Returns**      |
| 📉 Low performance + Low risk          | **Promote / Optimize**       |
| 📉 Low performance + High return risk  | **Review / Clearance**       |
| 📦 Low stock + strong demand           | **Restock**                  |
| 📦 Excess stock + weak demand          | **Reduce Stock / Promote**   |
| 🏷️ Discount-dependent performance     | **Review Discount Strategy** |

This is where the project moves beyond visualization into **decision support**.

---

# 📊 What Makes This Project Different?

Most analytics projects stop here:

```text
Dataset
   ↓
Charts
   ↓
Insights
```

FashionPulse AI extends the pipeline:

```text
Dataset
   ↓
Data Engineering
   ↓
SQL Analytics
   ↓
Interactive Dashboard
   ↓
Machine Learning
   ↓
Prediction
   ↓
Risk & Opportunity
   ↓
Business Recommendation
```

### The goal is not simply to predict.

### The goal is to support better decisions.

---

# ⚠️ Project Limitations

FashionPulse AI is built on a product-level dataset, so some capabilities are intentionally outside the current scope.

### No true time-series forecasting

The dataset does not contain a date field.

Therefore, the current implementation does not claim genuine monthly/weekly time-series forecasting.

### No direct customer-level modeling

The dataset does not contain customer transaction history or customer IDs.

Customer behavior is therefore represented indirectly through product-level indicators such as ratings, reviews, sales and returns.

### Estimated sales value ≠ accounting revenue

The estimated sales value does not include accounting-level adjustments.

### Local Flask deployment

The included Flask development server is intended for local/project use rather than production deployment.

---

# 🔮 Future Scope

FashionPulse AI provides a foundation for more advanced retail intelligence.

Potential extensions include:

* 📅 Transaction-level time-series forecasting
* 👤 Customer-level segmentation
* 🛍️ Purchase-history analysis
* 📈 Campaign effectiveness analysis
* 🌦️ Richer seasonality features
* 🔄 Automated model retraining
* 📡 Model monitoring
* 🔔 Advanced dashboard alerts
* ☁️ Production deployment
* 🔐 Environment-based secret management
* 🧠 Advanced AI / RAG business knowledge layer

---

# 🎓 Skills Demonstrated

This project demonstrates practical experience across the complete analytics lifecycle:

```text
Data Preparation
      ↓
Database Management
      ↓
SQL Analytics
      ↓
REST API Development
      ↓
Dashboard Development
      ↓
Data Visualization
      ↓
Machine Learning
      ↓
Model Evaluation
      ↓
Model Persistence
      ↓
Application Integration
      ↓
Business Decision Support
```

---

# 👨‍💻 Developer

### **[Satyam Kumar Shrivastav / Username: Satyam K. S. G2 - Data Analytics](https://www.linkedin.com/in/s-k-shrivastav/)**

**[Official Mail](mailto:satyamg2dataanalytics@gmail.com)**

**Batch: G2 Data Analytics**

**Duration: 6 Months (April 2026 - September 2026)**

**[SURE Trust / Sure ProEd](https://www.suretrustforruralyouth.com/)**

Project Period:

**July 2026 – September 2026**

Mentor:

**[Keerthana V.](https://www.linkedin.com/in/keerthana-v-294a311b9/)**

Senior Executive — Business Analyst, EXL Service, Chennai

---

# 📌 Project Statement

> **FashionPulse AI transforms raw fashion e-commerce data into actionable business intelligence.**

---

# ⭐ If You Find This Project Interesting

If this project demonstrates something useful to you:

⭐ **Star the repository**

🍴 **Fork the project**

💬 **Share your feedback**

---

<p align="center">

### 👗 FashionPulse AI

**From Data → Insight → Prediction → Action**

<br>

**Built with Python • MySQL • Flask • Machine Learning • JavaScript**

</p>
