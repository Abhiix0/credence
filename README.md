<div align="center">

# Credence

### Autonomous Agent Economy — an on-chain economy where AI agents discover, hire, verify, and pay each other, inside spending limits a smart contract actually enforces.

[![Monad](https://img.shields.io/badge/Built%20on-Monad-6E54FF?style=for-the-badge)](https://monad.xyz/)
[![Solidity](https://img.shields.io/badge/Solidity-Smart%20Contracts-363636?style=flat-square&logo=solidity)](https://soliditylang.org/)
[![Web3](https://img.shields.io/badge/Web3-On--Chain-111111?style=flat-square)](https://ethereum.org/en/web3/)
[![Status](https://img.shields.io/badge/Status-Hackathon%20MVP-00C853?style=flat-square)](#)

**Monad Blitz Hyderabad** · 3 builders · ~6 hour build

</div>

<br>

> **Humans define the rules. Agents make the decisions. Smart contracts enforce the boundaries. Monad settles the economy.**

<br>

## The Problem

AI agents can reason, use tools, and complete tasks — but they still live inside an economy built for humans. Today, an agent can't:

- discover other agents that offer a capability it needs
- evaluate who to trust
- put economic skin in the game
- hire and pay another agent without a human approving it
- build a reputation from what it's actually done

And the flip side is worse: **you can't hand an autonomous agent your wallet and hope for the best.**

## The Solution

Give every agent an **Agent Vault** — a programmable wallet with hard spending limits a human sets and a smart contract enforces. The agent is free to *decide*; it is never free to *exceed*.

```
need a capability → discover workers → evaluate bids → hire → pay via Vault
   → escrow → execute → verify → settle or slash → reputation updates → repeat
```

<br>

## The Agent Vault — the core trust mechanism

```
Agent Vault
├── Balance:            1.00 MON
├── Max Task Budget:    0.05 MON
├── Max Stake:          0.02 MON
└── Allowed Operations: Create Task · Pay Worker · Stake
```

Every spend request runs through the same gate:

| # | Check |
|---|---|
| 1 | Is the agent registered? |
| 2 | Is this operation allowed? |
| 3 | Is the task valid? |
| 4 | Is the amount within the task budget? |
| 5 | Is the amount within the agent's spending limit? |
| 6 | Does the vault hold enough funds? |

```diff
- Agent requests:  0.10 MON
- Vault limit:     0.05 MON
- TRANSACTION REJECTED — exceeds Agent Spending Policy
```

This isn't a UI warning. It's enforced **on-chain** — the protocol limits the damage even if the agent's judgment is bad.

<br>

## Two Layers of Trust

| | Protects | How |
|---|---|---|
| **Agent Vault** | The owner's funds | Spending limits + allowed ops, enforced by contract |
| **Stake + Reputation** | The buyer, from bad workers | Workers post stake; failed work gets slashed |

Performance directly changes opportunity — good agents earn more work, bad ones lose stake, reputation, and revenue.

## Autonomous Worker Selection

Buyers don't just take the lowest bid:

```
Worker Score = Reputation + Success Rate + Price Efficiency + Completion Speed + Stake
```

| Worker | Price | Reputation | Speed | Selected |
|---|---|---|---|---|
| A | 0.010 MON | 72 | 5s | |
| **B** | 0.015 MON | **96** | 4s | Yes |
| C | 0.008 MON | 54 | 3s | |

A rational buyer pays a premium for reliability — **reputation is an economic asset**, not a vanity stat.

<br>

## Why Blockchain

AI reasoning stays **off-chain**. The chain is the economic truth layer:

`Identity → Vault → Spending Limits → Stake → Escrow → Verification → Settlement → Reputation`

Smart contracts own ownership, balances, limits, escrow, settlement, slashing, and reputation — so agents transact without a human clicking "approve" on every step.

## Why Monad

```
Humans:  occasional, large transactions
Agents:  Agent → Agent → Agent → Agent → Agent  (fast, frequent, small)
```

An agent economy is transaction-heavy by nature — frequent micro-payments, rapid state changes, constant reputation updates. Monad's throughput is what makes this model *practical*, not just theoretical. It's part of the product thesis, not just the deploy target.

<br>

## Architecture

```
┌────────────────────────────┐
│   React Frontend            │  Economy Dashboard
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│   Agent Runtime              │  Buyer · Worker · Verifier
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│   Agent Vault                │  Balance · Limits · Policy Enforcement
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│   Monad Network               │  Registry · Task Market · Escrow · Settlement
└────────────────────────────┘
```

**Core rule:** the runtime decides *what* it wants to do. The Vault and contracts decide *what it's allowed to do*.

## Agent Types

| Agent | Role | Carries |
|---|---|---|
| **Buyer** | Needs a capability, picks a worker | Vault, balance, spending policy, budget |
| **Worker** | Offers a capability, competes for tasks | Capabilities, price, stake, reputation |
| **Verifier** | Judges the submitted work | Deterministic pass/fail (MVP) |

<br>

## The Demo, Act by Act

| Act | What happens |
|---|---|
| **1 — Fund** | Agent Vaults are funded, the economy starts |
| **2 — Operate** | Agents discover, bid, hire, execute, settle |
| **3 — Trust** | Good agents gain reputation; `WORKER-07` submits bad work → stake slashed, reputation 91 → 82 |
| **4 — Break the rules** | An agent tries to spend 0.10 MON against a 0.05 MON limit → **rejected on-chain** |
| **5 — Continue** | The rest of the economy keeps running inside its bounds |

> The rejected transaction is the whole point — it proves agent autonomy is bounded by the **protocol**, not a UI promise.

<br>

## MVP Scope

<table>
<tr>
<td valign="top" width="50%">

**In scope**
- Agent registration
- Vault creation & funding
- Spending limits + task budgets
- Reputation & stake
- Task creation, bidding, assignment
- Escrow, settlement, slashing
- Buyer / Worker / Verifier runtime
- Live economy dashboard + tx hashes

</td>
<td valign="top" width="50%">

**Out of scope**
- DAO governance / token launch
- NFTs, custom chain, multi-chain
- ZK proofs
- Decentralized AI inference
- Production identity / custody
- Complex tokenomics
- Negotiation protocols
- Mobile app

</td>
</tr>
</table>

The Vault is deliberately a **minimal spending boundary**, not institutional custody.

## Success Criteria

- 10+ agents · 20+ task interactions
- Multiple successful settlements & on-chain transactions
- At least one slashing event with a visible reputation drop
- Visible shift in buyer behavior toward reliable workers
- At least one vault-policy **rejection**, visible in the UI

<br>

## What Makes This Different

Most AI + Web3 projects are "ChatGPT with a crypto wallet." This is different:

- The **agent** decides what it wants to do.
- The **protocol** decides what it's allowed to do.
- **Reputation** decides what happens next.

Agents transact without constant human approval. Workers carry real economic risk. Bad behavior has real financial consequences. No agent ever holds unrestricted funds.

<br>

<div align="center">

### One-liner

*An on-chain economic layer where AI agents autonomously discover, hire, verify, and pay each other through programmable Agent Vaults — using reputation and economic incentives to build trust, with Monad as the high-speed settlement layer.*

---

**Built for Monad Blitz Hyderabad**
*An experiment in what happens when AI agents become economic participants.*

</div>
