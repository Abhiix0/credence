#!/usr/bin/env bash
set -e

echo "========================================="
echo "Autonomous Agent Economy - Monorepo Setup"
echo "========================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 1. Check Root Environment
if [ ! -f "$ROOT_DIR/.env" ]; then
    echo "[*] Creating .env from .env.example..."
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

# 2. Setup Agent Runtime (Python)
echo "[*] Setting up Agent Runtime..."
cd "$ROOT_DIR/agent-runtime"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
deactivate

# 3. Setup Frontend (Next.js)
echo "[*] Setting up Frontend..."
cd "$ROOT_DIR/frontend"
npm install
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
fi

# 4. Check Foundry
echo "[*] Checking Foundry setup..."
if command -v forge &> /dev/null; then
    cd "$ROOT_DIR/contracts"
    forge --version
else
    echo "[!] Foundry not installed. Please install from https://getfoundry.sh"
fi

echo "========================================="
echo "Setup complete! Read README.md for next steps."
echo "========================================="
