# Hackathon Demo Walkthrough

This guide demonstrates an end-to-end execution of the **Autonomous Agent Economy** on Monad testnet.

---

## 📋 Demo Scenario

1. **Buyer creates a Task**: "Analyze market data trends and output JSON summary".
2. **Worker Agents discover Task**:
   - `Agent 1` (ConservativePolicy): Bids 0.05 MON with strict margin.
   - `Agent 2` (AggressivePolicy): Bids 0.04 MON for immediate execution.
3. **Buyer selects Agent 2**: Escrow of 0.04 MON is assigned to the task.
4. **Agent 2 executes with Gemini AI**: Processes input prompt and computes summary payload.
5. **Agent 2 submits result**: Transaction with result proof is confirmed on Monad.
6. **Buyer / Verifier approves**: Task is verified as `VerifiedPass`.
7. **Settlement**: 0.04 MON is transferred to Agent 2's wallet; Agent 2 reputation increments on-chain.

---

## 🛠️ Step-by-Step Execution

### Step 1: Deploy Contracts to Monad Testnet
```bash
cd contracts
forge script script/Deploy.s.sol --rpc-url https://testnet-rpc.monad.xyz --broadcast
```
Note the deployed addresses:
- `TaskMarket`: `0x...`
- `AgentRegistry`: `0x...`

Update your `.env` with the deployed addresses.

### Step 2: Start the Agent Runtime
In a terminal, start worker agent running with `ConservativePolicy`:
```bash
cd agent-runtime
source .venv/bin/activate
export AGENT_POLICY=ConservativePolicy
python -m src.agents.base_agent
```

In a second terminal (optional), start a competitor agent with `AggressivePolicy`:
```bash
cd agent-runtime
source .venv/bin/activate
export AGENT_POLICY=AggressivePolicy
python -m src.agents.base_agent
```

### Step 3: Launch Frontend Dashboard
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000` to inspect live tasks, watch incoming bids from the agents, assign work, and trigger verifications.
