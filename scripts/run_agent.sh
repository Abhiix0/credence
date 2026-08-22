#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/agent-runtime"

if [ ! -d ".venv" ]; then
    echo "[!] Virtual environment not found. Please run scripts/setup.sh first."
    exit 1
fi

source .venv/bin/activate
export PYTHONPATH="$ROOT_DIR/agent-runtime:$PYTHONPATH"

POLICY=${1:-"ConservativePolicy"}
echo "[*] Launching Autonomous Agent with policy: $POLICY"
export AGENT_POLICY="$POLICY"

python -m src.agents.base_agent
