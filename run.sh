#!/bin/bash
echo "📊 Starting Dental ROI Intel Pro..."

echo "Starting FastApi Backend..."
# Assuming system python for MVP since it's just pandas/numpy
if [ ! -d "venv" ]; then
    python -m venv venv
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
    pip install -r requirements.txt
else
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi
nohup uvicorn src.api.main:app --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting React Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
nohup npm run dev -- --port 5175 > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ Analytics System is running!"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:5175"
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"
