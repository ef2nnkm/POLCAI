# End-to-End Order Processing Dashboard

Refactored version of the Day 2 Baseline Streamlit dashboard. The visual flow, KPI definitions, filters, process flows and DC detail table are preserved while database, business, rendering and styling concerns are separated.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Set PG_USER and PG_PASS plus optional DB_* variables
streamlit run app.py
```

## Test

```bash
python -m compileall app.py config dashboard tests
pytest -q
```

Credentials are never stored in source control. Copy `.env.example` for reference, but inject values through the runtime environment or deployment secret store.
