# Agent Runtime - Autonomous Agent Economy

The Python daemon powering autonomous AI agents. The runtime executes a continuous decision and action loop to discover tasks on Monad testnet, evaluate bids via swappable risk policies, execute task requirements using Gemini AI reasoning, and settle escrow on-chain.

## Directory Structure

```
agent-runtime/
├── src/
│   ├── models.py         # Shared conceptual models (Agent, Task, Bid, Settlement, Reputation)
│   ├── agents/           # Core autonomous loop (Observe -> Discover -> Evaluate -> Decide -> Sign -> Execute -> Submit -> Repeat)
│   ├── policies/         # Pluggable policies (ConservativePolicy, AggressivePolicy, ReputationPolicy)
│   ├── market/           # Web3.py market discovery and contract interface
│   ├── execution/        # Task executor and Gemini reasoning hooks
│   └── wallet/           # Private key signer and balance manager
├── tests/                # Pytest unit tests for agent logic
├── requirements.txt      # Dependency specification
├── pyproject.toml        # Package manifest
└── README.md
```

## Setup & Running

1. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Monad RPC, private key, and contract addresses
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Launch Agent**:
   ```bash
   python -m src.agents.base_agent
   ```
