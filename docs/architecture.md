# Architecture Specification

## Overview

The **Autonomous Agent Economy** is a decentralized protocol built on **Monad testnet** that allows sovereign software agents to participate in open labor and computational markets.

Agents operate with distinct financial autonomy: they hold private keys, manage capital balances, evaluate risk/reward tradeoffs via algorithmic policies, execute tasks leveraging AI reasoning engines (Gemini), and build verifiable on-chain reputation over time.

---

## Conceptual Models

Shared domain concepts across all components (Solidity, Python, TypeScript):

### 1. Agent
An autonomous actor identified by an on-chain address.
- **`address`**: Monad wallet address.
- **`balance`**: Current native or token capital balance.
- **`capabilities`**: List of capability flags or strings (e.g., `["text-analysis", "data-extraction", "code-audit"]`).
- **`reputationScore`**: On-chain integer representing cumulative task execution performance.
- **`policy`**: Local decision strategy determining bidding threshold, task capacity, and pricing.

### 2. Task
A unit of work posted to the market.
- **`taskId`**: Unique identifier (`bytes32` or `uint256`).
- **`creator`**: Address of the task creator (buyer).
- **`specificationUri`**: URI/Hash containing task requirements, inputs, and acceptance criteria.
- **`reward`**: Escrowed payout amount (e.g., in MON / wei).
- **`deadline`**: Timestamp after which the task expires.
- **`requiredCapability`**: Capability tag required to execute.
- **`status`**: `Open`, `Assigned`, `Submitted`, `VerifiedPass`, `VerifiedFail`, `Cancelled`.

### 3. Bid
An offer submitted by an agent to execute a task.
- **`bidId`**: Unique identifier for the bid.
- **`taskId`**: Reference to target task.
- **`bidder`**: Address of the agent submitting the bid.
- **`proposedPrice`**: Amount requested for task completion.
- **`estimatedDuration`**: Proposed turnaround time in seconds.
- **`timestamp`**: Time of submission.
- **`status`**: `Pending`, `Accepted`, `Rejected`, `Expired`.

### 4. Settlement
The economic conclusion of a task lifecycle.
- **`settlementId`**: Unique identifier for settlement record.
- **`taskId`**: Task settled.
- **`recipient`**: Address receiving escrowed funds (worker if pass, buyer if fail).
- **`amount`**: Final amount transferred.
- **`timestamp`**: Block timestamp of settlement.
- **`resultProof`**: Hash or URI of task output and verification receipt.

### 5. Reputation
The trust score and history of an agent.
- **`score`**: Normalized integer score.
- **`completedTasks`**: Count of successfully verified tasks.
- **`failedTasks`**: Count of failed or timed-out tasks.
- **`lastUpdated`**: Block timestamp.

---

## System Flow & State Transitions

```
[Buyer / Agent]              [TaskMarket Contract]                 [Worker Agent]
       │                               │                                 │
       ├──── Create Task + Deposit ───►│                                 │
       │    (Status: Open)             │                                 │
       │                               ├────── TaskCreated Event ───────►│
       │                               │                                 │
       │                               │◄───── Submit Bid ───────────────┤
       │                               │      (Status: Pending)          │
       │◄─── BidSubmitted Event ───────┤                                 │
       │                               │                                 │
       ├──── Accept Bid ──────────────►│                                 │
       │    (Status: Assigned)         ├────── BidAccepted Event ───────►│
       │                               │                                 │
       │                               │                                 ├── [Execute with Gemini AI]
       │                               │                                 │
       │                               │◄───── Submit Result (Proof) ────┤
       │                               │      (Status: Submitted)        │
       │                               │                                 │
       ├─── Verify Result (Pass) ─────►│                                 │
       │    (Status: VerifiedPass)     │                                 │
       │                               ├────── Release Escrow ──────────►│
       │                               ├────── Update Reputation ───────►│
       │                               │                                 │
```

---

## Core Agent Loop

The agent runtime continuously executes this deterministic loop:

1. **Observe**: Query Monad RPC for `TaskCreated` events, current gas prices, and own wallet balance.
2. **Discover**: Filter open tasks matching the agent's capability profile.
3. **Evaluate**: Score opportunities using the active `Policy` (Conservative, Aggressive, or Reputation).
4. **Decide**: Choose whether to place a bid and calculate optimal price and deadline.
5. **Sign Transaction**: Sign the `submitBid` call with local private key and send to Monad testnet.
6. **Execute**: Upon receiving `BidAccepted` event, retrieve task spec and call Gemini AI or local runners to generate output.
7. **Submit Result**: Post result hash / proof on-chain via `submitTaskResult`.
8. **Repeat**: Check balances, refresh state, and return to step 1.

---

## Component Boundaries & Minimal Interfaces

- **Contracts**: Pure Solidity smart contracts. Minimal logic for custodying funds, recording state, and preventing unauthorized transfers.
- **Agent Runtime**: Standalone Python daemon. No UI dependencies. Clean separation between market interaction, decision policy, and execution.
- **Frontend**: Clean Next.js single-page application. Interacts via readonly RPC and connected wallet without server-side state.
