import { useState, useEffect, useCallback } from 'react';
import { publicClient } from '../lib/viemClient';
import { TASK_MARKET_ABI, TASK_MARKET_ADDRESS } from '../lib/contracts';
import { Task, TaskStatus } from '../lib/types';
import { formatEther } from 'viem';

const STATUS_MAP: Record<number, TaskStatus> = {
  0: 'Open',
  1: 'Assigned',
  2: 'Submitted',
  3: 'VerifiedPass',
  4: 'VerifiedFail',
  5: 'Cancelled',
};

export function useTaskMarket() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    if (!TASK_MARKET_ADDRESS || TASK_MARKET_ADDRESS === '0x0000000000000000000000000000000000000000') {
      // Return empty if contract address not configured yet
      setTasks([]);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const total = (await publicClient.readContract({
        address: TASK_MARKET_ADDRESS,
        abi: TASK_MARKET_ABI,
        functionName: 'totalTasks',
      })) as bigint;

      const items: Task[] = [];
      for (let i = 1; i <= Number(total); i++) {
        const raw = (await publicClient.readContract({
          address: TASK_MARKET_ADDRESS,
          abi: TASK_MARKET_ABI,
          functionName: 'getTask',
          args: [BigInt(i)],
        })) as any;

        items.push({
          id: Number(raw.id),
          creator: raw.creator,
          specificationUri: raw.specificationUri,
          requiredCapability: raw.requiredCapability,
          rewardWei: raw.reward,
          rewardFormatted: `${formatEther(raw.reward)} MON`,
          deadline: Number(raw.deadline),
          status: STATUS_MAP[raw.status] || 'Open',
          selectedWorker: raw.selectedWorker,
          acceptedBidId: Number(raw.acceptedBidId),
          resultUri: raw.resultUri,
          resultHash: raw.resultHash,
        });
      }

      setTasks(items);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch tasks from Monad');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return { tasks, isLoading, error, refetch: fetchTasks };
}
