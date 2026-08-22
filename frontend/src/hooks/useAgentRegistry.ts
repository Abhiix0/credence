import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { AgentRegistryABI } from '../contracts/AgentRegistry';
import { AGENT_REGISTRY_ADDRESS } from '../contracts/config';
import type { Address } from 'viem';

// ─── Read Hooks ──────────────────────────────────────────────────────────────

export function useGetAgent(agentAddress?: Address) {
  return useReadContract({
    address: AGENT_REGISTRY_ADDRESS,
    abi: AgentRegistryABI,
    functionName: 'getAgent',
    args: agentAddress ? [agentAddress] : undefined,
    query: {
      enabled: !!agentAddress && agentAddress !== '0x0000000000000000000000000000000000000000',
    },
  });
}

export function useIsRegisteredAgent(agentAddress?: Address) {
  return useReadContract({
    address: AGENT_REGISTRY_ADDRESS,
    abi: AgentRegistryABI,
    functionName: 'isRegisteredAgent',
    args: agentAddress ? [agentAddress] : undefined,
    query: {
      enabled: !!agentAddress && agentAddress !== '0x0000000000000000000000000000000000000000',
    },
  });
}

export function useGetAllAgents() {
  return useReadContract({
    address: AGENT_REGISTRY_ADDRESS,
    abi: AgentRegistryABI,
    functionName: 'getAllAgents',
  });
}

// ─── Write Hooks ─────────────────────────────────────────────────────────────

export function useRegisterAgent() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const registerAgent = (name: string, capabilities: string[]) => {
    writeContract({
      address: AGENT_REGISTRY_ADDRESS,
      abi: AgentRegistryABI,
      functionName: 'registerAgent',
      args: [name, capabilities],
    });
  };

  return {
    registerAgent,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

export function useUpdateCapabilities() {
  const { data: hash, writeContract, isPending, error } = useWriteContract();
  
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const updateCapabilities = (capabilities: string[]) => {
    writeContract({
      address: AGENT_REGISTRY_ADDRESS,
      abi: AgentRegistryABI,
      functionName: 'updateCapabilities',
      args: [capabilities],
    });
  };

  return {
    updateCapabilities,
    hash,
    isPending,
    isConfirming,
    isSuccess,
    error,
  };
}

// ─── Types ───────────────────────────────────────────────────────────────────

export interface Agent {
  wallet: Address;
  name: string;
  capabilities: string[];
  reputationScore: bigint;
  completedTasks: bigint;
  failedTasks: bigint;
  isRegistered: boolean;
}
