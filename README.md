# Dental Market Intelligence (ROI Intel Pro)

Dental market analysis app with:
- **Backend**: FastAPI service in `src/api/main.py`
- **Frontend**: React + Vite app in `frontend/`

## Prerequisites

- Python 3
- Node.js + npm

## Quick start (fresh clone)

From the repository root:

```bash
chmod +x run.sh
./run.sh
```

The startup script will:
- create `./venv` if needed
- install Python dependencies from `requirements.txt` if missing
- install frontend dependencies from `frontend/package-lock.json` on first run
- start backend and frontend development servers

## Local URLs

- Frontend: `http://localhost:5175`
- Backend: `http://localhost:8000`
- Health check: `http://localhost:8000/health`
