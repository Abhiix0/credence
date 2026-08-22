import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { TaskMarketABI, TaskStatus } from '../contracts/TaskMarket';
import { TASK_MARKET_ADDRESS } from '../contracts/config';
import type { Address } from 'viem';
import { parseEther } from 'viem';

// ─── Read Hooks ──────────────────────────────────────────────────────────────

export function useGetTask(taskId?: bigint | number) {
  const taskIdBigInt = typeof taskId === 'number' ? BigInt(taskId) : taskId;
  
  return useReadContract({
    address: TASK_MARKET_ADDRESS,
    abi: TaskMarketABI,
    functionName: 'getTask',
    args: taskIdBigInt !== undefined ? [taskIdBigInt] : undefined,
    query: {
      enabled: taskIdBigInt !== undefined && taskIdBigInt > 0n,
    },
  });
}

export function useGetBid(bidId?: bigint | number) {
  const bidIdBigInt = typeof bidId === 'number' ? BigInt(bidId) : bidId;
  
  return useReadContract({
    address: TASK_MARKET_ADDRESS,
    abi: TaskMarketABI,
    functionName: 'getBid',
    args: bidIdBigInt !== undefined ? [bidIdBigInt] : undefined,
    query: {
      enabled: bidIdBigInt !== undefined && bidIdBigInt > 0n,
    },
  });
}

export function useGetTaskBids(taskId?: bigint | number) {
  const taskIdBigInt = typeof taskId === 'number' ? BigInt(taskId) : taskId;
  
  return useReadContract({
    address: TASK_MARKET_ADDRESS,
    abi: TaskMarketABI,
    functionName: 'getTaskBids',
    args: taskIdBigInt !== undefined ? [taskIdBigInt] : undefined,
    query: {
      enabled: taskIdBigInt !== undefined && taskIdBigInt > 0n,
    },
  });
}

export function useTotalTasks() {
  return useReadContract({
    address: TASK_MARKET_ADDRESS,
    abi: TaskMarketABI,
    functionName: 'totalTasks',
  });
}

// ─── Write Hooks ─────────────────────────────────────────────────────────────

export function useCreateTask() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const createTask = (
    specificationUri: string,
    requiredCapability: string,
    deadline: bigint,
    rewardEther: string
  ) => {
    writeContract({
      address: TASK_MARKET_ADDRESS,
      abi: TaskMarketABI,
      functionName: 'createTask',
      args: [specificationUri, requiredCapability, deadline],
      value: parseEther(rewardEther),
    });
  };

  return {
    createTask,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

export function useSubmitBid() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const submitBid = (
    taskId: bigint,
    proposedPriceEther: string,
    estimatedDuration: bigint,
    stakeEther: string
  ) => {
    writeContract({
      address: TASK_MARKET_ADDRESS,
      abi: TaskMarketABI,
      functionName: 'submitBid',
      args: [taskId, parseEther(proposedPriceEther), estimatedDuration],
      value: parseEther(stakeEther),
    });
  };

  return {
    submitBid,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

export function useSelectWorker() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const selectWorker = (taskId: bigint, bidId: bigint) => {
    writeContract({
      address: TASK_MARKET_ADDRESS,
      abi: TaskMarketABI,
      functionName: 'selectWorker',
      args: [taskId, bidId],
    });
  };

  return {
    selectWorker,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

export function useSubmitResult() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const submitResult = (
    taskId: bigint,
    resultUri: string,
    resultHash: `0x${string}`
  ) => {
    writeContract({
      address: TASK_MARKET_ADDRESS,
      abi: TaskMarketABI,
      functionName: 'submitResult',
      args: [taskId, resultUri, resultHash],
    });
  };

  return {
    submitResult,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

export function useVerifyResult() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const verifyResult = (taskId: bigint, passed: boolean) => {
    writeContract({
      address: TASK_MARKET_ADDRESS,
      abi: TaskMarketABI,
      functionName: 'verifyResult',
      args: [taskId, passed],
    });
  };

  return {
    verifyResult,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

export function useCancelTask() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const cancelTask = (taskId: bigint) => {
    writeContract({
      address: TASK_MARKET_ADDRESS,
      abi: TaskMarketABI,
      functionName: 'cancelTask',
      args: [taskId],
    });
  };

  return {
    cancelTask,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

export function useExpireTask() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const expireTask = (taskId: bigint) => {
    writeContract({
      address: TASK_MARKET_ADDRESS,
      abi: TaskMarketABI,
      functionName: 'expireTask',
      args: [taskId],
    });
  };

  return {
    expireTask,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

// ─── Types ───────────────────────────────────────────────────────────────────

export interface Task {
  id: bigint;
  creator: Address;
  specificationUri: string;
  requiredCapability: string;
  reward: bigint;
  deadline: bigint;
  status: TaskStatus;
  selectedWorker: Address;
  acceptedBidId: bigint;
  resultUri: string;
  resultHash: `0x${string}`;
}

export interface Bid {
  id: bigint;
  taskId: bigint;
  bidder: Address;
  proposedPrice: bigint;
  estimatedDuration: bigint;
  timestamp: bigint;
  isAccepted: boolean;
  stake: bigint;
}

export { TaskStatus };
