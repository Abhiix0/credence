'use client';

import { useState, useEffect } from 'react';
import {
  mockAgents,
  mockCurrentTask,
  mockActivityFeed,
  mockEconomyStats,
} from './mockEconomy';
import { Agent, Task, ActivityEvent, EconomyStats } from '../types';

// TODO(real-data): replace mock read with a chain-backed hook, keep this exact return shape.
export function useAgents() {
  const [data, setData] = useState<Agent[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate async loading
    const timer = setTimeout(() => {
      setData(mockAgents);
      setIsLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  return { data, isLoading, error };
}

// TODO(real-data): replace mock read with a chain-backed hook, keep this exact return shape.
export function useCurrentTask() {
  const [data, setData] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate async loading
    const timer = setTimeout(() => {
      setData(mockCurrentTask);
      setIsLoading(false);
    }, 250);

    return () => clearTimeout(timer);
  }, []);

  return { data, isLoading, error };
}

// TODO(real-data): replace mock read with a chain-backed hook, keep this exact return shape.
export function useActivityFeed() {
  const [data, setData] = useState<ActivityEvent[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate async loading
    const timer = setTimeout(() => {
      setData(mockActivityFeed);
      setIsLoading(false);
    }, 200);

    return () => clearTimeout(timer);
  }, []);

  return { data, isLoading, error };
}

// TODO(real-data): replace mock read with a chain-backed hook, keep this exact return shape.
export function useEconomyStats() {
  const [data, setData] = useState<EconomyStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate async loading
    const timer = setTimeout(() => {
      setData(mockEconomyStats);
      setIsLoading(false);
    }, 150);

    return () => clearTimeout(timer);
  }, []);

  return { data, isLoading, error };
}
