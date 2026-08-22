import { Agent, Task, Bid, ActivityEvent, EconomyStats } from '../types';

const now = Math.floor(Date.now() / 1000);

// Mock agent addresses for consistency
const AGENT_ADDRESSES = {
  sentinel: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1',
  vortex: '0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199',
  oracle: '0xdD2FD4581271e230360230F9337D5c0430Bf44C0',
  nexus: '0xbDA5747bFD65F08deb54cb465eB87D40e51B197E',
  phantom: '0x2546BcD3c84621e976D8185a91A922aE77ECEc30',
  cipher: '0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC',
  glitch: '0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9', // Low reputation, foreshadowing bad actor
  rift: '0x28C6c06298d514Db089934071355E5743bf21d60',
} as const;

export const mockAgents: Agent[] = [
  {
    walletAddress: AGENT_ADDRESSES.sentinel,
    name: 'Sentinel-01',
    capabilities: ['data_analysis', 'verification'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.sentinel,
      score: 94,
      completedTasks: 127,
      failedTasks: 3,
      lastUpdated: now - 3600,
    },
    policyName: 'balanced',
    isActive: true,
    role: 'worker',
    balanceFormatted: '47.3 MON',
  },
  {
    walletAddress: AGENT_ADDRESSES.vortex,
    name: 'Vortex-Alpha',
    capabilities: ['computation', 'simulation'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.vortex,
      score: 88,
      completedTasks: 94,
      failedTasks: 7,
      lastUpdated: now - 7200,
    },
    policyName: 'aggressive',
    isActive: true,
    role: 'worker',
    balanceFormatted: '32.1 MON',
  },
  {
    walletAddress: AGENT_ADDRESSES.oracle,
    name: 'Oracle-Prime',
    capabilities: ['prediction', 'data_analysis'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.oracle,
      score: 91,
      completedTasks: 156,
      failedTasks: 12,
      lastUpdated: now - 1800,
    },
    policyName: 'reputation',
    isActive: true,
    role: 'buyer',
    balanceFormatted: '128.7 MON',
  },
  {
    walletAddress: AGENT_ADDRESSES.nexus,
    name: 'Nexus-7',
    capabilities: ['verification', 'auditing'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.nexus,
      score: 96,
      completedTasks: 203,
      failedTasks: 4,
      lastUpdated: now - 900,
    },
    policyName: 'conservative',
    isActive: true,
    role: 'verifier',
    balanceFormatted: '89.5 MON',
  },
  {
    walletAddress: AGENT_ADDRESSES.phantom,
    name: 'Phantom-X',
    capabilities: ['computation', 'verification'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.phantom,
      score: 85,
      completedTasks: 67,
      failedTasks: 9,
      lastUpdated: now - 5400,
    },
    policyName: 'balanced',
    isActive: true,
    role: 'worker',
    balanceFormatted: '21.4 MON',
  },
  {
    walletAddress: AGENT_ADDRESSES.cipher,
    name: 'Cipher-9',
    capabilities: ['data_analysis', 'computation'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.cipher,
      score: 89,
      completedTasks: 112,
      failedTasks: 8,
      lastUpdated: now - 2700,
    },
    policyName: 'balanced',
    isActive: true,
    role: 'worker',
    balanceFormatted: '38.9 MON',
  },
  {
    walletAddress: AGENT_ADDRESSES.glitch,
    name: 'Glitch-Worker',
    capabilities: ['computation', 'simulation'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.glitch,
      score: 62,
      completedTasks: 34,
      failedTasks: 18,
      lastUpdated: now - 10800,
    },
    policyName: 'aggressive',
    isActive: true,
    role: 'worker',
    balanceFormatted: '12.3 MON',
  },
  {
    walletAddress: AGENT_ADDRESSES.rift,
    name: 'Rift-Beta',
    capabilities: ['verification', 'prediction'],
    reputation: {
      agentAddress: AGENT_ADDRESSES.rift,
      score: 92,
      completedTasks: 145,
      failedTasks: 6,
      lastUpdated: now - 4500,
    },
    policyName: 'reputation',
    isActive: true,
    role: 'verifier',
    balanceFormatted: '67.2 MON',
  },
];

export const mockCurrentTask: Task = {
  id: 42,
  creator: '0x1234567890123456789012345678901234567890',
  specificationUri: 'ipfs://QmX7Y8Z9...',
  requiredCapability: 'data_analysis',
  rewardWei: BigInt('3200000000000000000'), // 3.2 MON
  rewardFormatted: '3.2 MON',
  deadline: now + 3600, // 1 hour from now
  status: 'Assigned',
  selectedWorker: AGENT_ADDRESSES.sentinel,
  acceptedBidId: 2,
  resultUri: null,
  resultHash: null,
};

export const mockBidsForCurrentTask: Bid[] = [
  {
    id: 1,
    taskId: 42,
    bidder: AGENT_ADDRESSES.oracle,
    proposedPriceWei: BigInt('2800000000000000000'), // 2.8 MON
    proposedPriceFormatted: '2.8 MON',
    estimatedDurationSec: 2400,
    timestamp: now - 600,
    isAccepted: false,
  },
  {
    id: 2,
    taskId: 42,
    bidder: AGENT_ADDRESSES.sentinel,
    proposedPriceWei: BigInt('3000000000000000000'), // 3.0 MON (winning bid)
    proposedPriceFormatted: '3.0 MON',
    estimatedDurationSec: 1800,
    timestamp: now - 540,
    isAccepted: true,
  },
  {
    id: 3,
    taskId: 42,
    bidder: AGENT_ADDRESSES.cipher,
    proposedPriceFormatted: '3.1 MON',
    proposedPriceWei: BigInt('3100000000000000000'), // 3.1 MON
    estimatedDurationSec: 2100,
    timestamp: now - 480,
    isAccepted: false,
  },
  {
    id: 4,
    taskId: 42,
    bidder: AGENT_ADDRESSES.glitch,
    proposedPriceWei: BigInt('2500000000000000000'), // 2.5 MON (low price, low reputation)
    proposedPriceFormatted: '2.5 MON',
    estimatedDurationSec: 3000,
    timestamp: now - 420,
    isAccepted: false,
  },
];

export const mockActivityFeed: ActivityEvent[] = [
  {
    id: 'evt_001',
    timestamp: now - 660,
    message: 'Task #42 created: data_analysis job posted with 3.2 MON reward',
    kind: 'task_created',
  },
  {
    id: 'evt_002',
    timestamp: now - 600,
    message: 'Oracle-Prime submitted bid: 2.8 MON, 40min ETA',
    kind: 'bid_submitted',
  },
  {
    id: 'evt_003',
    timestamp: now - 540,
    message: 'Sentinel-01 submitted bid: 3.0 MON, 30min ETA',
    kind: 'bid_submitted',
  },
  {
    id: 'evt_004',
    timestamp: now - 480,
    message: 'Cipher-9 submitted bid: 3.1 MON, 35min ETA',
    kind: 'bid_submitted',
  },
  {
    id: 'evt_005',
    timestamp: now - 420,
    message: 'Glitch-Worker submitted bid: 2.5 MON, 50min ETA',
    kind: 'bid_submitted',
  },
  {
    id: 'evt_006',
    timestamp: now - 360,
    message: 'Buyer selected Sentinel-01 (reputation: 94, price: 3.0 MON)',
    kind: 'worker_selected',
  },
  {
    id: 'evt_007',
    timestamp: now - 355,
    message: 'Escrow locked: 3.0 MON transferred to TaskMarket contract',
    kind: 'escrow_locked',
  },
  {
    id: 'evt_008',
    timestamp: now - 180,
    message: 'Task #41 completed: Nexus-7 verification passed',
    kind: 'verification_pass',
  },
  {
    id: 'evt_009',
    timestamp: now - 175,
    message: 'Settlement: 2.7 MON released to Vortex-Alpha',
    kind: 'settlement',
  },
  {
    id: 'evt_010',
    timestamp: now - 170,
    message: 'Reputation updated: Vortex-Alpha +2 (now 88)',
    kind: 'reputation_change',
  },
  {
    id: 'evt_011',
    timestamp: now - 120,
    message: 'Task #40 verification failed: Glitch-Worker result rejected',
    kind: 'verification_fail',
  },
  {
    id: 'evt_012',
    timestamp: now - 115,
    message: 'Reputation updated: Glitch-Worker -5 (now 62)',
    kind: 'reputation_change',
  },
];

export const mockEconomyStats: EconomyStats = {
  agentsOnline: 8,
  activeTasks: 3,
  totalTransactions: 487,
  volumeFormatted: '1,247.3 MON',
  successRatePct: 91.2,
};
