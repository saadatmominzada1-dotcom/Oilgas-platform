#!/bin/bash

echo ""
echo "🛢️  Starting OilGas Intelligence Platform..."
echo ""

# Use absolute path so cd commands are always reliable
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start backend using explicit venv python (avoids activate path confusion)
echo "▶ Starting backend on http://localhost:8000"
"$SCRIPT_DIR/backend/venv/bin/python" "$SCRIPT_DIR/backend/main.py" &
BACKEND_PID=$!

# Wait for backend
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend
echo "▶ Starting frontend on http://localhost:3000"
cd "$SCRIPT_DIR/frontend" && npm start &
FRONTEND_PID=$!

echo ""
echo "=============================================="
echo "  ✅ Platform running!"
echo "  🌐 Open: http://localhost:3000"
echo "  Press Ctrl+C to stop both servers"
echo "=============================================="
echo ""

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

wait
