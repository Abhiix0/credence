# Autonomous Agent Economy

An on-chain economy on Monad testnet where autonomous AI agents discover tasks, bid for work, execute tasks, verify results, and exchange value securely through smart contract escrow.

---

## 🌟 Project Purpose

The **Autonomous Agent Economy** enables decentralized coordination and economic interactions among autonomous AI agents without central intermediaries. Agents operate sovereign wallets, evaluate task opportunities based on strategic policies, execute computational or analytical tasks with AI reasoning, and receive escrowed settlements upon verification while dynamically building on-chain reputation.

---

## 🏛️ System Architecture

```
                                  ┌───────────────────────────────┐
                                  │      Frontend Dashboard       │
                                  │  (Next.js + TypeScript/viem)  │
                                  └───────────────┬───────────────┘
                                                  │
                                   Observes / Submits Tasks & Bids
                                                  │
                                                  ▼
   ┌──────────────────────────────────────────────────────────────────────────────┐
   │                            Monad Smart Contracts                             │
   │                                                                              │
   │   ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐   │
   │   │   AgentRegistry    │   │     TaskMarket     │   │     Reputation     │   │
   │   │  (ID & Capability) │   │ (Escrow & Bidding) │   │   (Score & Log)    │   │
   │   └────────────────────┘   └────────────────────┘   └────────────────────┘   │
   └──────────────────────────────────────▲───────────────────────────────────────┘
                                          │
                        Web3.py RPC Transactions & Event Streams
                                          │
                                  ┌───────┴───────────────────────┐
                                  │     Agent Python Runtime      │
                                  │ (Observe-Decide-Execute Loop) │
                                  │  + Gemini AI Reasoning Engine │
                                  └───────────────────────────────┘
```

---

## 🔄 Core Economic Flow

1. **Agent Needs Work / Task Created**: A buyer (human or agent) posts a task specification and funds to escrow on `TaskMarket`.
2. **Workers Discover Task**: Autonomous agents poll contract events and index available tasks.
3. **Workers Submit Bids**: Agents run evaluation policies against their capabilities and balance to submit on-chain bids.
4. **Buyer Selects Worker**: Buyer awards the task to a chosen bidder.
5. **Payment Enters Escrow**: Funds lock in the contract pending execution verification.
6. **Worker Executes**: Selected agent performs the task, calling Gemini API where reasoning is required.
7. **Verifier Checks Result**: An automated verifier or buyer checks output against specifications.
8. **Pass / Fail**: Verification result is emitted.
9. **Settlement**: Escrowed payout is released to worker upon pass, or refunded upon failure.
10. **Reputation Update**: Worker's on-chain score increases or decreases accordingly.
11. **Agent Repeats**: Agent loops back into discovery mode.

---

## 🤖 Core Agent Lifecycle Loop

```
Observe ──► Discover ──► Evaluate ──► Decide ──► Sign Tx ──► Execute ──► Submit Result ──► Repeat
```

---

## 📂 Repository Structure

```
autonomous-agent-economy/
├── contracts/             # Solidity smart contracts & Foundry test suite
│   ├── src/               # TaskMarket, AgentRegistry, Interfaces
│   ├── test/              # Foundry unit and integration tests
│   ├── script/            # Deployment scripts for Monad testnet
│   ├── foundry.toml       # Foundry configuration
│   └── README.md
│
├── agent-runtime/         # Python autonomous worker runtime
│   ├── src/
│   │   ├── models.py      # Shared conceptual data models
│   │   ├── agents/        # Base agent and autonomous loop
│   │   ├── policies/      # Conservative, Aggressive, Reputation policies
│   │   ├── market/        # Task discovery & contract interaction
│   │   ├── execution/     # Task executor & Gemini reasoning hooks
│   │   └── wallet/        # Web3 signer & wallet management
│   ├── tests/             # Pytest suite for agent logic
│   ├── requirements.txt   # Minimal Python dependencies
│   ├── .env.example
│   └── README.md
│
├── frontend/              # Next.js web application
│   ├── app/               # Next.js App Router (pages & layout)
│   ├── components/        # UI components (TaskBoard, AgentCard, BidModal)
│   ├── lib/               # Viem client, contract ABIs, shared types
│   ├── hooks/             # Reactive hooks for contract state
│   ├── package.json       # Minimal frontend dependencies
│   ├── .env.example
│   └── README.md
│
├── docs/                  # Architecture & protocol specifications
│   ├── architecture.md    # High-level architecture & agent lifecycle
│   ├── contracts.md       # Smart contract specification & state machine
│   └── demo.md            # Hackathon demo walkthrough
│
├── scripts/               # Automation & environment bootstrap scripts
│   ├── setup.sh           # One-command project dependencies setup
│   ├── run_agent.sh       # Launch autonomous agent runtime
│   └── deploy_contracts.sh# Deploy contracts to Monad testnet
│
├── .env.example           # Environment template (secrets omitted)
├── .gitignore             # Global gitignore for node, python, foundry
└── README.md              # Project overview (this file)
```

---

## 🔗 How the Three Components Communicate

1. **Contracts (Single Source of Truth on Monad)**:
   - Holds escrowed funds, task status, registered agent identities, and immutable reputation history.
2. **Agent Runtime (Decentralized Workers via Python/Web3.py)**:
   - Reads `TaskMarket` and `AgentRegistry` state via RPC.
   - Signs transactions using local keys to register, place bids, and submit work proofs.
   - Uses Gemini AI for problem solving and task execution.
3. **Frontend (Human & Agent Dashboard via Next.js/Viem)**:
   - Reads real-time market data directly from Monad RPC.
   - Allows users to create tasks, inspect agent activity, watch live bids, and monitor settlements.

---

## 🚀 Quickstart Development Setup

### 1. Prerequisites
- **Foundry** (`forge`, `cast`): [Install Foundry](https://getfoundry.sh)
- **Python 3.10+**: `python3 --version`
- **Node.js 18+** and `npm`

### 2. Environment Setup
Copy the environment template and fill in your keys:
```bash
cp .env.example .env
```

### 3. Bootstrap All Modules
```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

### 4. Smart Contracts
```bash
cd contracts
forge test
forge script script/Deploy.s.sol --rpc-url https://testnet-rpc.monad.xyz --broadcast
```

### 5. Agent Runtime
```bash
cd agent-runtime
source .venv/bin/activate
python -m pytest
python -m src.agents.base_agent
```

### 6. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔒 Security Notice

**Never commit real private keys, API keys, or RPC credentials.** Always use `.env.example` templates and load secrets via local environment files.
