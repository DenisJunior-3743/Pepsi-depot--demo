# Pepsi Depo Management ERP — Backend

FastAPI backend for the Pepsi Cola Depo Management ERP (production → distribution → depot sales, restock alerts). Deployed on Render with a PostgreSQL database.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # then fill in DATABASE_URL
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` once running.
