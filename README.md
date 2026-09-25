# Zepto Data & AI Platform

This single repository contains the three capstone modules: a Books to Scrape data-engineering pipeline, a Titanic analytics/modeling pipeline, and a grounded Zepto policy assistant.

## Setup

Each module owns its dependencies. From the repository root, install them with:

```powershell
python -m pip install -r data_pipeline/requirements.txt
python -m pip install -r analytics/requirements.txt
python -m pip install -r support_assistant/requirements.txt
```

SQLite is provided by Python. The analytics pipeline needs network access only on its first Seaborn Titanic load; `analytics/titanic.csv` is the committed offline fallback. The support assistant defaults to `MOCK_LLM=1`, requiring no API key or LLM network call.

## Run End to End

```powershell
python -m data_pipeline.main
python analytics/src/titanic_pipeline.py
uvicorn support_assistant.src.assistant:app --reload
```

Then call the assistant:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/ask -Method Post -ContentType 'application/json' -Body '{"query":"What is the delivery fee?"}'
```

Run tests:

```powershell
python -m pytest data_pipeline/tests analytics/tests support_assistant/tests -q
```

## Design Decisions

- **Data pipeline:** `requests` and `BeautifulSoup` scrape five Books to Scrape catalogue pages and detail-page categories. Typed cleaning produces `price_gbp`, `price_inr`, integer `rating`, and boolean `in_stock`; SQLite normalizes categories and books with a foreign key. Required SQL output plus equivalent `pd.read_sql`/`pd.merge` output are written by `data_pipeline.main`.
- **Analytics:** `analytics/src/titanic_pipeline.py` loads Titanic once, immediately saves the CSV fallback, applies the missingness threshold rule, creates the required EDA charts and interpretations, and uses train-only `ColumnTransformer` preprocessing for all classifiers. It also performs SMOTE-on-training-only, Random Forest GridSearchCV with OOB scoring, fare regression, and saves a complete joblib pipeline.
- **Support assistant:** `support_assistant/src/assistant.py` ingests eight exact policy documents, embeds them locally, stores vectors in ChromaDB, routes through LangGraph, and returns deterministic Pydantic JSON in mock mode. The optional real mode is gated only by `MOCK_LLM=0`.

See each module README for detailed decisions, metrics, outputs, and Docker instructions. The required Git workflow is a feature branch with at least two commits merged back into `main`; inspect it with `git log --graph --oneline --decorate --all`.
