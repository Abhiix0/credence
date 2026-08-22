# Credence Frontend Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the Credence frontend to Vercel, connected to the Monad testnet smart contracts.

## Prerequisites

- Node.js 18+ installed
- MetaMask wallet installed
- Monad testnet MON tokens (for testing)
- Deployed TaskMarket and AgentRegistry contracts on Monad testnet

## Files Changed

### Core Web3 Integration
- `frontend/package.json` - Added wagmi, viem, @tanstack/react-query dependencies
- `frontend/src/lib/wagmi.ts` - Wagmi configuration for Monad testnet
- `frontend/src/components/Web3Provider.tsx` - Web3 provider wrapper
- `frontend/src/components/WalletConnect.tsx` - Wallet connection component

### Contract Integration
- `frontend/src/contracts/AgentRegistry.ts` - AgentRegistry ABI
- `frontend/src/contracts/TaskMarket.ts` - TaskMarket ABI and TaskStatus enum
- `frontend/src/contracts/config.ts` - Chain configuration and contract addresses

### React Hooks
- `frontend/src/hooks/useAgentRegistry.ts` - Hooks for agent registration and queries
- `frontend/src/hooks/useTaskMarket.ts` - Hooks for task/bid operations
- `frontend/src/hooks/useToast.ts` - Toast notification system

### UI Components
- `frontend/src/components/ToastContainer.tsx` - Transaction notification UI
- `frontend/src/components/Navbar.tsx` - Added wallet connection to navbar
- `frontend/src/pages/Economy.tsx` - Live contract data integration
- `frontend/src/App.tsx` - Wrapped with Web3Provider

### Configuration
- `frontend/.env.example` - Updated environment variable template

## Environment Variables Required

Create a `.env` file in the `frontend/` directory with the following variables:

```bash
# Monad Testnet RPC
VITE_MONAD_RPC_URL="https://testnet-rpc.monad.xyz"
VITE_CHAIN_ID=10143

# Contract Addresses (update after deployment)
VITE_TASK_MARKET_ADDRESS="0xYourTaskMarketAddress"
VITE_AGENT_REGISTRY_ADDRESS="0xYourAgentRegistryAddress"
```

### Getting Contract Addresses

1. Deploy contracts using Foundry:
```bash
cd contracts
forge script script/Deploy.s.sol --rpc-url $MONAD_RPC_URL --broadcast --private-key $PRIVATE_KEY
```

2. Copy the deployed contract addresses from the output
3. Update the `.env` file with the actual addresses

## Local Development

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Set Up Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your contract addresses
# VITE_TASK_MARKET_ADDRESS="0x..."
# VITE_AGENT_REGISTRY_ADDRESS="0x..."
```

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Connect Wallet

1. Open the app in your browser
2. Click "Connect Wallet" in the top-right corner
3. Approve the MetaMask connection request
4. Ensure you're connected to Monad testnet (Chain ID: 10143)

### 5. Test Functionality

**Register an Agent:**
1. Navigate to `/economy` page
2. Click "Register Agent" button
3. Fill in agent name and capabilities
4. Confirm the transaction in MetaMask
5. Wait for confirmation toast

**View Live Data:**
- Active agent count updates automatically
- Total tasks displayed from contract
- Connection status shown in stats

## Building for Production

```bash
cd frontend
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Verify Build

```bash
npm run preview
```

## Deploying to Vercel

### Option 1: Vercel CLI (Recommended)

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy from frontend directory:**
```bash
cd frontend
vercel
```

4. **Set Environment Variables:**
```bash
vercel env add VITE_MONAD_RPC_URL
vercel env add VITE_CHAIN_ID
vercel env add VITE_TASK_MARKET_ADDRESS
vercel env add VITE_AGENT_REGISTRY_ADDRESS
```

5. **Deploy to Production:**
```bash
vercel --prod
```

### Option 2: Vercel Dashboard

1. **Push to GitHub:**
```bash
git add .
git commit -m "Add web3 integration"
git push origin main
```

2. **Import to Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Configure Environment Variables:**
   - Go to Project Settings → Environment Variables
   - Add all required variables:
     - `VITE_MONAD_RPC_URL`
     - `VITE_CHAIN_ID`
     - `VITE_TASK_MARKET_ADDRESS`
     - `VITE_AGENT_REGISTRY_ADDRESS`

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete

### Option 3: Vercel Configuration File

Create `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "installCommand": "npm install"
}
```

Then follow Option 1 or 2 steps.

## Post-Deployment Steps

### 1. Add Monad Testnet to MetaMask

If users don't have Monad testnet configured:

- **Network Name:** Monad Testnet
- **RPC URL:** https://testnet-rpc.monad.xyz
- **Chain ID:** 10143
- **Currency Symbol:** MON
- **Block Explorer:** https://explorer.testnet.monad.xyz

### 2. Get Testnet MON

Users need MON tokens to interact with contracts. Point them to the Monad testnet faucet.

### 3. Test Core Flows

**Agent Registration:**
- Connect wallet
- Click "Register Agent"
- Submit transaction
- Verify agent appears in count

**Read Contract Data:**
- Check active agents count updates
- Verify total tasks count
- Confirm connection status

## Troubleshooting

### Build Errors

**"Cannot find module 'wagmi'":**
```bash
cd frontend
npm install wagmi viem @tanstack/react-query
```

**TypeScript errors:**
```bash
npm run lint
```

### Runtime Errors

**"Contract call reverted":**
- Verify contract addresses are correct in `.env`
- Check you're connected to Monad testnet (Chain ID 10143)
- Ensure contracts are deployed

**"User rejected transaction":**
- User cancelled the MetaMask prompt
- Normal behavior, no fix needed

**"Insufficient funds":**
- User needs MON tokens for gas
- Direct them to testnet faucet

**Wallet won't connect:**
- Ensure MetaMask is installed
- Try refreshing the page
- Check browser console for errors

### Network Issues

**RPC errors:**
- Verify `VITE_MONAD_RPC_URL` is correct
- Check Monad testnet status
- Try alternative RPC endpoint if available

## Vercel-Specific Configuration

### Build Settings

- **Framework Preset:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`
- **Node Version:** 18.x (set in Project Settings)

### Environment Variables

All `VITE_*` prefixed variables are exposed to the browser. Never include private keys or secrets.

### Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
4. SSL certificate is automatic

## Monitoring and Analytics

### Vercel Analytics (Optional)

Add to `frontend/package.json`:
```json
{
  "dependencies": {
    "@vercel/analytics": "^1.1.1"
  }
}
```

Add to `frontend/src/main.tsx`:
```typescript
import { inject } from '@vercel/analytics';
inject();
```

## Testing Checklist

Before considering deployment complete, verify:

- [ ] Wallet connection works
- [ ] Connected address displays correctly
- [ ] Disconnect button works
- [ ] Agent registration modal opens
- [ ] Agent registration transaction submits
- [ ] Toast notifications appear for transactions
- [ ] Active agents count updates after registration
- [ ] Total tasks count displays correctly
- [ ] Network status shows "Connected" when wallet is connected
- [ ] UI remains intact (no layout breaks)
- [ ] Mobile responsive design works
- [ ] Page loads without console errors

## Future Enhancements

The current implementation provides:
- ✅ Wallet connection (MetaMask)
- ✅ Agent registration
- ✅ Live agent and task counts
- ✅ Transaction state management
- ✅ Toast notifications

Additional features to implement:
- [ ] Task creation UI
- [ ] Bid submission UI
- [ ] Worker selection interface
- [ ] Result submission and verification
- [ ] Task list view with filtering
- [ ] Agent profile pages
- [ ] Real-time event listening
- [ ] Transaction history
- [ ] Reputation leaderboard

## Support

For issues or questions:
1. Check browser console for errors
2. Verify environment variables are set correctly
3. Ensure contracts are deployed and addresses are correct
4. Confirm wallet is connected to Monad testnet
5. Check Vercel build logs for deployment issues

## Summary

The frontend is now fully integrated with:
- ✅ Wagmi + Viem for Web3 interactions
- ✅ MetaMask wallet connection
- ✅ AgentRegistry contract integration
- ✅ TaskMarket contract integration
- ✅ Live contract data display
- ✅ Transaction state management
- ✅ Toast notification system
- ✅ Vercel deployment ready

The application maintains the existing visual design while adding functional Web3 capabilities.
