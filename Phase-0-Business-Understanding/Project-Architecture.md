# Project Architecture Diagram
## Swastik Traders — Retail Analytics Ecosystem

**Version:** 1.0
**Date:** July 2026

---

## Full Data Pipeline

```mermaid
flowchart TD
    subgraph Phase1["🗄️ Phase 1 — Synthetic Data Generation (Python)"]
        EXT["External Signals\n(Weather · Fuel Prices · Inflation)"]
        GEN["Data Generator\nPython Notebook\n~22 tables · April 2023–June 2026"]
        CSV["Raw CSV Files\n(one per table)"]
        EXT -->|"drives correlations"| GEN
        GEN --> CSV
    end

    subgraph Phase2["🗃️ Phase 2 — Database Design (MySQL)"]
        DDL["Schema DDL\n(Tables · PK/FK · Constraints)"]
        DB[("MySQL Database\nswastik_traders_db")]
        OBJ["DB Objects\n(Views · Procedures · Triggers · Events)"]
        CSV -->|"SQL INSERT scripts"| DDL
        DDL --> DB
        DB --> OBJ
    end

    subgraph Phase3["🧹 Phase 3 — ETL & Data Cleaning (Python)"]
        CLEAN["Cleaning Pipeline\n(Missing · Dupes · Format · Dates)"]
        FE["Feature Engineering\n(CLV · RFM · Profit% · Flags)"]
        CLEANDB[("Clean MySQL Layer")]
        DB -->|"raw tables"| CLEAN
        CLEAN --> FE
        FE --> CLEANDB
    end

    subgraph Phase4["📊 Phase 4 — SQL Business Analytics"]
        SQL200["200+ SQL Queries\n(organized by category)"]
        SQLRPT["SQL Report\n(40-60 pages PDF)"]
        CLEANDB -->|"queried via"| SQL200
        SQL200 --> SQLRPT
    end

    subgraph Phase5["📈 Phase 5 — Power BI Dashboards"]
        STAR["Star Schema\n(Fact + Dimension Tables)"]
        DAX["DAX Measures\n(KPIs · Time Intelligence)"]
        DASH["12 Dashboards\n(.pbix)"]
        PBI["Power BI Service\n(Published Workspace)"]
        CLEANDB -->|"imported to"| STAR
        STAR --> DAX
        DAX --> DASH
        DASH --> PBI
    end

    subgraph Phase6["🤖 Phase 6 — Machine Learning (Python · scikit-learn)"]
        FEAT["Feature Matrix\n(Phase 3 Engineered Features)"]
        DEEP["3 Deep Models\nProfit Prediction\nPaint Price Prediction\nReturn Prediction"]
        REG["10 Regular Models\nChurn · Segmentation · Basket Analysis\nSentiment NLP · Time Series · etc."]
        MODELS["Saved Model Artifacts\n(.pkl files)"]
        CLEANDB -->|"feature extraction"| FEAT
        FEAT --> DEEP
        FEAT --> REG
        DEEP --> MODELS
        REG --> MODELS
    end

    subgraph Phase7["🚀 Phase 7 — Deployment"]
        STREAM["Streamlit/Gradio Apps\n(3 Deep Model Demos)"]
        HF["HuggingFace Spaces\n(Public URLs)"]
        DOCKER["Docker Container\n(MySQL + Seed Data)"]
        GHPAGES["GitHub Pages\n(Project Landing Site)"]
        MODELS -->|"loaded by"| STREAM
        STREAM --> HF
        DB -->|"containerized"| DOCKER
    end

    subgraph Phase8["📄 Phase 8 — Reports"]
        SQLRPT2["SQL Report PDF"]
        BIRPT["Power BI Report PDF"]
        MLRPT["ML Report PDF"]
        FINALRPT["Final Business Report\n(100-150 pages PDF)"]
        SQL200 --> SQLRPT2
        DASH --> BIRPT
        MODELS --> MLRPT
        SQLRPT2 & BIRPT & MLRPT --> FINALRPT
    end

    subgraph Phase9["🎤 Phase 9 — Presentation"]
        PPT["Executive PPT\n(25-35 slides)"]
        FINALRPT --> PPT
    end

    subgraph Phase10["🐙 Phase 10 — GitHub Structure"]
        REPOS["13 GitHub Repositories"]
        UMBRELLA["13-Project-Documentation\n(Umbrella Repo + GitHub Pages)"]
        REPOS --> UMBRELLA
        HF --> UMBRELLA
        PBI --> UMBRELLA
        FINALRPT --> UMBRELLA
    end

    Phase1 --> Phase2
    Phase2 --> Phase3
    Phase3 --> Phase4
    Phase3 --> Phase5
    Phase3 --> Phase6
    Phase4 --> Phase8
    Phase5 --> Phase8
    Phase6 --> Phase5
    Phase6 --> Phase7
    Phase7 --> Phase10
    Phase8 --> Phase9
    Phase9 --> Phase10
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Data Generation** | Python (Faker, NumPy, Pandas) | Synthetic data generation with realistic correlations |
| **Database** | MySQL 8.x | Core transactional + analytical database |
| **ETL/Cleaning** | Python (Pandas, re, datetime) | Data cleaning + feature engineering pipeline |
| **SQL Analytics** | MySQL (advanced SQL) | 200+ business analytics queries |
| **BI/Dashboards** | Power BI Desktop + Power BI Service | 12 interactive dashboards |
| **Machine Learning** | Python (scikit-learn, XGBoost, LightGBM, NLTK/spaCy) | 13 ML models (3 deep + 10 regular) |
| **ML Deployment** | Streamlit or Gradio | Interactive model demo apps |
| **App Hosting** | HuggingFace Spaces / Render | Free public hosting for ML demos |
| **DB Containerization** | Docker + docker-compose | Reproducible MySQL setup |
| **Documentation Site** | GitHub Pages | Project front door |
| **Version Control** | Git + GitHub | 13 repositories under one org |
| **Reporting** | MS Word / Google Docs → PDF | SQL, BI, ML, Final Business Reports |
| **Presentation** | PowerPoint / Google Slides | Executive deck |

---

## Data Flow Summary

```
External Signals (Weather/Fuel/Inflation)
        ↓ (drives correlations)
[Python Generator] → CSV Files (22 tables)
        ↓ (SQL INSERT scripts)
[MySQL Database] → Schema + Views + Triggers + Procedures
        ↓ (Python ETL)
[Cleaned Data Layer] → Engineered Features (CLV, RFM, Profit%, etc.)
        ↓                        ↓                        ↓
[SQL Analytics]          [Power BI Dashboards]     [ML Models]
200+ queries              12 dashboards              13 models
SQL Report                BI Report                  ML Report
        ↓                        ↓                        ↓
                    [Final Business Report]
                    [Executive Presentation]
                            ↓
                [GitHub Pages — Project Landing]
```

---

## Key Architectural Decisions

1. **Two-layer MySQL architecture:** Raw imported data stays in base tables. Views + the cleaned Python output form the analytics layer. Keeps raw data recoverable without overwriting.

2. **Feature engineering in Python, not SQL:** CLV, RFM segments, flags are computed in the Phase 3 Python notebook and written back to the database as enriched columns/tables — easier to document and version-control than SQL-only transformations.

3. **Star schema in Power BI separate from MySQL 3NF:** MySQL is normalized for transactional integrity; Power BI imports denormalized views for performance. The star schema is built inside Power BI's data model layer.

4. **ML model outputs feed back into Power BI:** Sentiment labels from the NLP model and time series forecasts are exported as CSVs and imported into Power BI for the Review Dashboard and Forecast Dashboard — creating a real ML→BI feedback loop.

5. **Docker for reproducibility:** The MySQL database is containerized so evaluators can spin up the exact same environment with one command, without needing a local MySQL install.
