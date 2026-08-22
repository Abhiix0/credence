#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/contracts"

if ! command -v forge &> /dev/null; then
    echo "[!] Foundry (forge) not found in PATH. Install from https://getfoundry.sh"
    exit 1
fi

RPC_URL=${MONAD_RPC_URL:-"https://testnet-rpc.monad.xyz"}

echo "[*] Compiling contracts..."
forge build

if [ -z "$PRIVATE_KEY" ]; then
    echo "[!] PRIVATE_KEY not set. Running dry-run simulation..."
    forge script script/Deploy.s.sol:DeployScript --rpc-url "$RPC_URL"
else
    echo "[*] Deploying to Monad Testnet..."
    forge script script/Deploy.s.sol:DeployScript \
        --rpc-url "$RPC_URL" \
        --private-key "$PRIVATE_KEY" \
        --broadcast
fi
