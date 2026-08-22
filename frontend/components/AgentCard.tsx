import React from 'react';
import { Agent } from '../lib/types';
import { Bot, Star, ShieldCheck, Activity } from 'lucide-react';

interface AgentCardProps {
  agent: Agent;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent }) => {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5 hover:border-zinc-300 transition">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-zinc-100 border border-zinc-200 flex items-center justify-center text-zinc-700">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900">{agent.name}</h3>
            <p className="text-xs font-mono text-zinc-500 truncate max-w-[160px]">
              {agent.walletAddress}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1 px-2.5 py-1 rounded-md bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold">
          <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
          <span>{agent.reputation.score}</span>
        </div>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500">Active Policy</span>
          <span className="font-mono font-medium text-zinc-800 bg-zinc-100 px-2 py-0.5 rounded">
            {agent.policyName || 'ConservativePolicy'}
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5 pt-2">
          {agent.capabilities.map((cap) => (
            <span
              key={cap}
              className="px-2 py-0.5 rounded text-[11px] font-mono bg-zinc-50 border border-zinc-200 text-zinc-600"
            >
              {cap}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-zinc-100 flex items-center justify-between text-xs text-zinc-500">
        <span>Completed: {agent.reputation.completedTasks}</span>
        <span>Failed: {agent.reputation.failedTasks}</span>
      </div>
    </div>
  );
};
