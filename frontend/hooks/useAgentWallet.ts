import { useState, useEffect, useCallback } from 'react';
import { publicClient } from '../lib/viemClient';
import { formatEther } from 'viem';

export function useAgentWallet(address?: `0x${string}`) {
  const [balance, setBalance] = useState<string>('0');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchBalance = useCallback(async () => {
    if (!address || address === '0x0000000000000000000000000000000000000000') {
      setBalance('0');
      return;
    }

    try {
      setIsLoading(true);
      const rawBalance = await publicClient.getBalance({ address });
      setBalance(formatEther(rawBalance));
    } catch {
      setBalance('0');
    } finally {
      setIsLoading(false);
    }
  }, [address]);

  useEffect(() => {
    fetchBalance();
  }, [fetchBalance]);

  return { balance, isLoading, refetch: fetchBalance };
}
