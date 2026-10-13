#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "❌ Python is required but was not found in PATH."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "❌ npm is required but was not found in PATH."
    exit 1
fi

echo "📊 Starting Dental ROI Intel Pro..."

echo "Starting FastApi Backend..."
if [ ! -d "venv" ]; then
    "$PYTHON_BIN" -m venv venv
fi

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Could not find a virtual environment activation script in ./venv."
    exit 1
fi

if ! python -c "import fastapi, uvicorn" >/dev/null 2>&1; then
    pip install -r requirements.txt
fi

nohup uvicorn src.api.main:app --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting React Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
fi
nohup npm run dev -- --port 5175 > frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$ROOT_DIR"

echo "✅ Analytics System is running!"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:5175"
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"
