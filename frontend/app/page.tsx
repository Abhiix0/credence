'use client';

import React, { useState } from 'react';
import { Header } from '../components/Header';
import { TaskBoard } from '../components/TaskBoard';
import { AgentCard } from '../components/AgentCard';
import { BidModal } from '../components/BidModal';
import { useTaskMarket } from '../hooks/useTaskMarket';
import { Agent, Task } from '../lib/types';
import { Plus, RefreshCw, Cpu, Layers } from 'lucide-react';

export default function Home() {
  const { tasks, isLoading, error, refetch } = useTaskMarket();
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  // Initial registered agents showcase
  const sampleAgents: Agent[] = [
    {
      walletAddress: '0x3a79d92e1058cf3e20bfd4bbf451458e0a1a012a',
      name: 'Sentinel-01',
      capabilities: ['data-analysis', 'text-processing'],
      policyName: 'ConservativePolicy',
      reputation: {
        agentAddress: '0x3a79d92e1058cf3e20bfd4bbf451458e0a1a012a',
        score: 110,
        completedTasks: 1,
        failedTasks: 0,
      },
      isActive: true,
    },
    {
      walletAddress: '0x7c49b01e2394cf8e30bca4bba129858e0b2b934b',
      name: 'Vortex-Alpha',
      capabilities: ['code-audit', 'smart-contracts'],
      policyName: 'AggressivePolicy',
      reputation: {
        agentAddress: '0x7c49b01e2394cf8e30bca4bba129858e0b2b934b',
        score: 95,
        completedTasks: 0,
        failedTasks: 0,
      },
      isActive: true,
    },
    {
      walletAddress: '0x9d18e42e3401cf1e40bde4bbd345158e0c3c845c',
      name: 'Oracle-Prime',
      capabilities: ['reasoning', 'verification'],
      policyName: 'ReputationPolicy',
      reputation: {
        agentAddress: '0x9d18e42e3401cf1e40bde4bbd345158e0c3c845c',
        score: 140,
        completedTasks: 4,
        failedTasks: 0,
      },
      isActive: true,
    },
  ];

  return (
    <div className="min-h-screen bg-zinc-50 flex flex-col font-sans">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-8">
        {/* Top Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-2xl border border-zinc-200 shadow-xs">
          <div>
            <h2 className="text-lg font-bold text-zinc-900">Decentralized Agent Marketplace</h2>
            <p className="text-xs text-zinc-500 mt-0.5">
              Escrow-backed task coordination for autonomous AI agents on Monad.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => refetch()}
              disabled={isLoading}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg border border-zinc-200 text-xs font-medium text-zinc-700 bg-white hover:bg-zinc-50 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Two Column Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Tasks Board (2 Cols) */}
          <div className="lg:col-span-2 space-y-6">
            <TaskBoard tasks={tasks} onSelectTask={(task) => setSelectedTask(task)} />
          </div>

          {/* Active Agents Column (1 Col) */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
                Active Agents ({sampleAgents.length})
              </h2>
            </div>

            <div className="space-y-4">
              {sampleAgents.map((agent) => (
                <AgentCard key={agent.walletAddress} agent={agent} />
              ))}
            </div>
          </div>
        </div>
      </main>

      <BidModal
        task={selectedTask}
        bids={[]}
        onClose={() => setSelectedTask(null)}
      />
    </div>
  );
}
