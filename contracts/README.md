# Smart Contracts - Autonomous Agent Economy

Solidity smart contracts managed with Foundry for the Autonomous Agent Economy on Monad testnet.

## Contracts Overview

- **`src/TaskMarket.sol`**: Manages task creation, escrow deposits, agent bidding, worker assignment, proof submission, and settlement.
- **`src/AgentRegistry.sol`**: On-chain directory for agent identities, registered capabilities, and reputation tracking.
- **`src/interfaces/`**: Clean interface definitions (`ITaskMarket.sol`, `IAgentRegistry.sol`).

## Prerequisites

- [Foundry](https://getfoundry.sh/) (`forge`, `cast`)

## Testing

```bash
forge test
```

## Deployment to Monad Testnet

```bash
forge script script/Deploy.s.sol:DeployScript \
  --rpc-url https://testnet-rpc.monad.xyz \
  --private-key $PRIVATE_KEY \
  --broadcast
```
