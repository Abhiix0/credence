import { defineChain } from 'viem';

export const monadTestnet = defineChain({
  id: 10143,
  name: 'Monad Testnet',
  network: 'monad-testnet',
  nativeCurrency: {
    decimals: 18,
    name: 'Monad',
    symbol: 'MON',
  },
  rpcUrls: {
    default: {
      http: [import.meta.env.VITE_MONAD_RPC_URL || 'https://testnet-rpc.monad.xyz'],
    },
    public: {
      http: [import.meta.env.VITE_MONAD_RPC_URL || 'https://testnet-rpc.monad.xyz'],
    },
  },
  blockExplorers: {
    default: { name: 'Explorer', url: 'https://explorer.testnet.monad.xyz' },
  },
  testnet: true,
});

export const TASK_MARKET_ADDRESS = (import.meta.env.VITE_TASK_MARKET_ADDRESS || '0x0000000000000000000000000000000000000000') as `0x${string}`;
export const AGENT_REGISTRY_ADDRESS = (import.meta.env.VITE_AGENT_REGISTRY_ADDRESS || '0x0000000000000000000000000000000000000000') as `0x${string}`;
