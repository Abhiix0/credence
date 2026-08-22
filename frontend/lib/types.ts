export type TaskStatus =
  | 'Open'
  | 'Assigned'
  | 'Submitted'
  | 'VerifiedPass'
  | 'VerifiedFail'
  | 'Cancelled';

export interface Reputation {
  agentAddress: `0x${string}` | string;
  score: number;
  completedTasks: number;
  failedTasks: number;
  lastUpdated?: number;
}

export interface Agent {
  walletAddress: `0x${string}` | string;
  name: string;
  capabilities: string[];
  reputation: Reputation;
  policyName?: string;
  isActive: boolean;
}

export interface Task {
  id: number;
  creator: `0x${string}` | string;
  specificationUri: string;
  requiredCapability: string;
  rewardWei: bigint;
  rewardFormatted: string;
  deadline: number;
  status: TaskStatus;
  selectedWorker?: `0x${string}` | string | null;
  acceptedBidId?: number | null;
  resultUri?: string | null;
  resultHash?: string | null;
}

export interface Bid {
  id: number;
  taskId: number;
  bidder: `0x${string}` | string;
  proposedPriceWei: bigint;
  proposedPriceFormatted: string;
  estimatedDurationSec: number;
  timestamp: number;
  isAccepted: boolean;
}

export interface Settlement {
  settlementId: string;
  taskId: number;
  recipient: `0x${string}` | string;
  amountWei: bigint;
  amountFormatted: string;
  timestamp: number;
  resultProof: string;
  passed: boolean;
}

export interface ActivityEvent {
  id: string;
  timestamp: number;
  message: string;
  kind:
    | 'task_created'
    | 'bid_submitted'
    | 'worker_selected'
    | 'escrow_locked'
    | 'result_submitted'
    | 'verification_pass'
    | 'verification_fail'
    | 'settlement'
    | 'reputation_change';
}

export interface EconomyStats {
  agentsOnline: number;
  activeTasks: number;
  totalTransactions: number;
  volumeFormatted: string;
  successRatePct: number;
}
