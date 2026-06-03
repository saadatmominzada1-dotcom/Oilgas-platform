#!/bin/bash
set -e

echo ""
echo "=============================================="
echo "  OilGas Intelligence Platform - Setup"
echo "=============================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+ from https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION found"

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install Node.js 18+ from https://nodejs.org"
    exit 1
fi
echo "✅ Node.js $(node --version) found"

# Backend setup
echo ""
echo "📦 Setting up backend..."
cd "$SCRIPT_DIR/backend"

# Create virtual environment
python3 -m venv venv

# Use the venv's own python to upgrade pip — avoids global pip permission issues
echo "   Upgrading pip..."
venv/bin/python -m pip install --upgrade pip -q

# Install all dependencies via the venv pip directly
echo "   Installing dependencies (this may take a few minutes)..."
venv/bin/pip install -r requirements.txt -q

echo "✅ Backend dependencies installed"

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created backend/.env (add optional API keys here)"
fi

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd "$SCRIPT_DIR/frontend"
npm install --legacy-peer-deps --silent
echo "✅ Frontend dependencies installed"

echo ""
echo "=============================================="
echo "  ✅ Setup complete!"
echo "=============================================="
echo ""
echo "To start: ./start.sh"
echo ""
echo "Optional — edit backend/.env to add:"
echo "  ANTHROPIC_API_KEY  → AI-powered digest summaries"
echo "  TELEGRAM_BOT_TOKEN → Telegram digest delivery"
echo "  GNEWS_API_KEY      → Extra news sources"
echo ""
