# Economy Runner Guide

## Overview

The `run_economy.py` script provides a single command to spin up a complete autonomous agent economy with buyers, workers, bad workers, and verifiers all running concurrently.

## Quick Start

```bash
# 1. Configure your agents in .env file (see .env.example)
cp .env.example .env
# Edit .env with your private keys and contract addresses

# 2. Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Start the economy
python run_economy.py

# Or with custom polling interval:
python run_economy.py --interval 20  # Poll every 20 seconds
```

## Architecture

The economy runner:
1. **Loads configurations** from environment variables (`AGENT_1_*`, `AGENT_2_*`, etc.)
2. **Instantiates agents** based on their role (buyer/worker/bad_worker/verifier)
3. **Runs each agent** in its own thread with independent step() cycles
4. **Handles errors** gracefully with automatic retry and error counting
5. **Provides clean shutdown** on Ctrl+C

## Configuration Format

Each agent is configured through numbered environment variables:

```bash
# Worker Agent Example
AGENT_1_NAME="WorkerBot-CodeSpecialist"
AGENT_1_PRIVATE_KEY="0x..."
AGENT_1_ROLE="worker"
AGENT_1_POLICY="ConservativePolicy"
AGENT_1_CAPABILITIES="coding,testing,code-review"
AGENT_1_RISK_TOLERANCE="0.3"

# Buyer Agent Example
AGENT_2_NAME="BuyerBot"
AGENT_2_PRIVATE_KEY="0x..."
AGENT_2_ROLE="buyer"
AGENT_2_POLICY="ConservativePolicy"
AGENT_2_RISK_TOLERANCE="0.6"  # For buyers: 0-1 scale

# Bad Worker Example (for testing verification)
AGENT_3_NAME="BadWorker-Fraudster"
AGENT_3_PRIVATE_KEY="0x..."
AGENT_3_ROLE="bad_worker"
AGENT_3_CAPABILITIES="sentiment-analysis"
AGENT_FAILURE_RATE="0.4"  # 40% of tasks will be fraudulent

# Verifier Agent Example
AGENT_4_NAME="VerifierBot"
AGENT_4_PRIVATE_KEY="0x..."  # Must be contract owner or task creator
AGENT_4_ROLE="verifier"
VERIFIER_MODE="owner"  # or "buyer"
```

### Required Fields

| Field | Description | Roles |
|-------|-------------|-------|
| `AGENT_N_NAME` | Display name | All |
| `AGENT_N_PRIVATE_KEY` | Ethereum private key | All |
| `AGENT_N_ROLE` | Agent role | All |
| `AGENT_N_POLICY` | Decision policy | All except verifier |
| `AGENT_N_CAPABILITIES` | Comma-separated skills | worker, bad_worker |
| `AGENT_N_RISK_TOLERANCE` | Risk threshold 0-1 | All |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `AGENT_N_MAX_BID_WEI` | Maximum bid amount | None |
| `AGENT_N_MIN_BALANCE_WEI` | Minimum wallet balance | 0 |
| `AGENT_FAILURE_RATE` | Bad worker failure rate | 0.4 |
| `AGENT_FAILURE_SEED` | RNG seed for bad worker | Random |
| `VERIFIER_MODE` | Verifier authorization mode | "owner" |

## Agent Roles

### Worker (`role=worker`)
- Discovers open tasks matching capabilities
- Evaluates tasks using policy
- Places bids on attractive tasks
- Executes assigned tasks
- Submits results to blockchain
- Tracks reputation changes

**Policies:**
- `ConservativePolicy`: Risk-averse, selective bidding
- `AggressivePolicy`: Price-focused, frequent bidding
- `BalancedPolicy`: Even consideration of factors
- `ReputationPolicy`: Reputation-focused selection

### Buyer (`role=buyer`)
- Creates tasks (manual or automated)
- Discovers bids on their tasks
- Evaluates bids using policy
- Selects best worker based on reputation/price/speed
- Verifies submitted results
- Handles settlements

**Risk Tolerance:** 
- For buyers, this is converted to 0-100 scale
- Higher = more selective (only high-scoring bids)
- Lower = less selective (wider acceptance range)

### Bad Worker (`role=bad_worker`)
- Same as worker but intentionally produces wrong results
- Used to test verification system
- Failure rate controlled by `AGENT_FAILURE_RATE`
- Always bids aggressively (50% of reward)

**Important:** Bad workers demonstrate that verification catches fraud!

### Verifier (`role=verifier`)
- Discovers submitted tasks
- Re-executes tasks deterministically
- Compares computed vs submitted results
- Submits verification (pass/fail) to contract

**Authorization:** Must use contract owner or task creator key!

## Standardized Logging

All agents use standardized block-format logging via `logging_utils.py`:

### Worker Bid Decision
```
======================================================================
[WorkerBot-CodeSpecialist]
Event: Bid Decision
======================================================================
Found Task: Task #42
Capability: code-review
Reward: 0.100000 ETH (100000000000000000 wei)
Policy: ConservativePolicy
Decision: BID
Proposed Price: 0.080000 ETH (80.0% of reward)
Estimated Duration: 3600 seconds
Reason: Policy accepted task based on capability match and reward threshold
======================================================================
```

### Buyer Worker Selection
```
======================================================================
[BuyerBot]
Event: Worker Selection
======================================================================
Found Task: Task #42
Capability: code-review
Reward: 0.100000 ETH (100000000000000000 wei)
Candidates:
  • 👑 Bid #1 | Worker: 0x1234567... | Score: 87.50 | Rep: 92 | Price: 0.080000 ETH (80.0%) | Duration: 3600s
  • #2 Bid #2 | Worker: 0xabcdef0... | Score: 72.30 | Rep: 68 | Price: 0.050000 ETH (50.0%) | Duration: 1800s
Policy: ConservativePolicy
Risk Tolerance: 60.0 (minimum acceptable score)
Decision: Selected Worker 0x1234567... (Bid #1)
Selection Score: 87.50/100
Reason: Selected for strong reputation (92/100) meeting conservative risk threshold
======================================================================
```

### Verifier Verification Result
```
======================================================================
[VerifierBot-QA]
Event: Verification Result
======================================================================
Task Id: Task #42
Worker: 0x1234567...
Result: ✅ PASS
Hash Comparison: ✓ Match
Submitted Hash: 8f2a7b...
Computed Hash: 8f2a7b...
Reason: Hash matches and URI format is valid
======================================================================
```

### Reputation Change
```
======================================================================
[WorkerBot-CodeSpecialist]
Event: Reputation Change
======================================================================
Worker: 0x1234567...
Task Id: Task #42
Change Type: Task Pass
Reputation Score: 90 ↑ 92 (Δ+2)
Completed Tasks: 15 → 16
Failed Tasks: 1 → 1
Reason: Task completed successfully and verified
======================================================================
```

## Running a Demo Economy

Example setup for a full economy demo:

```bash
# 1 Buyer
AGENT_1_ROLE=buyer
AGENT_1_NAME="BuyerBot"

# 2 Honest Workers (different policies)
AGENT_2_ROLE=worker
AGENT_2_NAME="Worker-Conservative"
AGENT_2_POLICY=ConservativePolicy

AGENT_3_ROLE=worker
AGENT_3_NAME="Worker-Aggressive"
AGENT_3_POLICY=AggressivePolicy

# 1 Bad Worker (for testing verification)
AGENT_4_ROLE=bad_worker
AGENT_4_NAME="BadWorker-Fraudster"
AGENT_FAILURE_RATE=0.4

# 1 Verifier
AGENT_5_ROLE=verifier
AGENT_5_NAME="VerifierBot"
VERIFIER_MODE=owner
```

This creates a complete economy:
1. Buyer posts tasks
2. Workers compete with bids
3. Bad worker also bids (sometimes fraudulent)
4. Buyer selects best worker
5. Workers execute tasks
6. Verifier catches fraud from bad worker
7. Reputation updates accordingly

## Monitoring

The economy runner provides:
- **Startup summary** showing all agents and their roles
- **Real-time logs** from all agents in unified format
- **Error tracking** with automatic retry (up to 10 errors per agent)
- **Clean shutdown** on Ctrl+C

Watch for these key events:
- `[Bid Decision]` - Worker decides to bid or skip
- `[Worker Selection]` - Buyer chooses winning worker
- `[Verification Result]` - Verifier validates results
- `[Reputation Change]` - Reputation updates after settlement

## Troubleshooting

### No agents starting
- Check `.env` file has `AGENT_1_*` variables configured
- Verify `AGENT_N_ROLE` is one of: buyer, worker, bad_worker, verifier
- Ensure `AGENT_N_PRIVATE_KEY` is set

### Verifier authorization errors
- Verifier must use contract owner or task creator key
- Set `VERIFIER_MODE=owner` and use deployer key
- Or set `VERIFIER_MODE=buyer` and use buyer's key

### Agents not finding tasks
- Verify contract addresses in `.env`
- Check Monad RPC connection
- Ensure agents have gas for transactions

### Too many logs
- Increase `--interval` to reduce polling frequency
- Adjust `logging.basicConfig` level in code
- Filter by agent name in logs

## Advanced Usage

### Custom Interval
```bash
# Poll every 30 seconds instead of default 15
python run_economy.py --interval 30
```

### Running Specific Agents
Comment out unwanted agents in `.env` or remove their configurations.

### Adding More Agents
Just increment the number and add new config:
```bash
AGENT_7_NAME="NewWorker"
AGENT_7_PRIVATE_KEY="0x..."
# ... etc
```

### Reproducible Bad Worker Behavior
```bash
AGENT_FAILURE_SEED="42"  # Same seed = same fraud pattern
```

## Integration with Tests

The economy runner complements the test suite:
- **Unit tests** (`tests/test_*.py`) - Test individual components
- **Economy runner** (`run_economy.py`) - Integration testing of full system
- **Frontend** - Visual monitoring and manual task creation

Use all three together for comprehensive testing!
