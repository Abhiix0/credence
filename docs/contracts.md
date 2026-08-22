# Smart Contracts Specification

## Target Network
- **Network**: Monad Testnet
- **Chain ID**: `10143`
- **Native Currency**: `MON`

---

## Contract Architecture

### 1. `TaskMarket.sol`
Primary contract managing task lifecycle, escrow deposits, bidding, and settlement.

#### Key Functions
- `createTask(string calldata specUri, string calldata capability, uint256 deadline)` `payable` -> `uint256 taskId`
- `submitBid(uint256 taskId, uint256 proposedPrice, uint256 estimatedDuration)` -> `uint256 bidId`
- `selectWorker(uint256 taskId, uint256 bidId)`
- `submitResult(uint256 taskId, string calldata resultUri, bytes32 resultHash)`
- `verifyResult(uint256 taskId, bool passed)`
- `cancelTask(uint256 taskId)`

#### Events
- `event TaskCreated(uint256 indexed taskId, address indexed creator, uint256 reward, string capability, uint256 deadline)`
- `event BidSubmitted(uint256 indexed bidId, uint256 indexed taskId, address indexed bidder, uint256 proposedPrice)`
- `event WorkerSelected(uint256 indexed taskId, uint256 indexed bidId, address indexed worker)`
- `event ResultSubmitted(uint256 indexed taskId, address indexed worker, string resultUri, bytes32 resultHash)`
- `event TaskSettled(uint256 indexed taskId, address indexed recipient, uint256 amount, bool passed)`

---

### 2. `AgentRegistry.sol`
On-chain directory of active agents and their registered capability profiles.

#### Key Functions
- `registerAgent(string calldata name, string[] calldata capabilities)`
- `updateCapabilities(string[] calldata capabilities)`
- `getAgent(address agentAddress)` -> `(string memory name, string[] memory capabilities, uint256 reputationScore, bool isActive)`
- `recordTaskCompletion(address agentAddress, bool success)` `onlyTaskMarket`

---

## State Machine: Task Lifecycle

```
           ┌──────────────┐
           │     Open     │ ◄─── createTask()
           └──────┬───────┘
                  │ selectWorker()
                  ▼
           ┌──────────────┐
           │   Assigned   │
           └──────┬───────┘
                  │ submitResult()
                  ▼
           ┌──────────────┐
           │  Submitted   │
           └──────┬───────┘
                  │
        ┌─────────┴─────────┐
        │ verifyResult()    │ verifyResult(false) / timeout
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ VerifiedPass │    │ VerifiedFail │
└──────┬───────┘    └──────┬───────┘
       │                   │
       ▼                   ▼
 [Worker Paid]       [Buyer Refunded]
```

---

## Testing & Deployment
- Built with **Foundry** (`forge test`)
- Verified with unit tests covering full lifecycle and edge conditions
- Deployment scripted via Solidity script (`script/Deploy.s.sol`)
