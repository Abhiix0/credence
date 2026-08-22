'use client';

import React, { useState, useMemo } from 'react';
import { useAgents, useActivityFeed } from '@/lib/data/useEconomyData';
import { Agent } from '@/lib/types';
import { AgentDetailPanel } from './AgentDetailPanel';
import { cn } from '@/lib/utils';

export const AgentNetwork: React.FC = () => {
  const { data: agents, isLoading } = useAgents();
  const { data: activityFeed } = useActivityFeed();
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  // Group agents by role
  const groupedAgents = useMemo(() => {
    if (!agents) return { buyers: [], workers: [], verifiers: [] };

    return {
      buyers: agents.filter((a) => a.role === 'buyer'),
      workers: agents.filter((a) => a.role === 'worker'),
      verifiers: agents.filter((a) => a.role === 'verifier'),
    };
  }, [agents]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[500px]">
        <div className="font-mono text-sm text-mutedForeground animate-pulse">
          Loading agent network...
        </div>
      </div>
    );
  }

  if (!agents || agents.length === 0) {
    return (
      <div className="flex items-center justify-center h-[500px]">
        <div className="font-mono text-sm text-mutedForeground">
          No agents available
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full">
      {/* Desktop: SVG Network Diagram */}
      <div className="hidden md:block">
        <svg
          viewBox="0 0 800 400"
          className="w-full h-auto"
          style={{ minHeight: '400px' }}
        >
          {/* Connection lines */}
          {/* Buyers to Workers */}
          <line x1="100" y1="200" x2="400" y2="200" stroke="#00d4ff" strokeWidth="2" opacity="0.4" />
          
          {/* Workers to Verifiers */}
          <line x1="400" y1="200" x2="700" y2="200" stroke="#00ff88" strokeWidth="2" opacity="0.4" />

          {/* Animated transaction pulse - travels from buyer to worker to verifier */}
          {/* Animation triggered by most recent activity feed event (periodic CSS animation) */}
          <circle className="transaction-pulse" r="4" fill="#00ff88">
            <animateMotion
              dur="6s"
              repeatCount="indefinite"
              path="M 100,200 L 400,200 L 700,200"
            />
          </circle>

          {/* Buyer Nodes (Left, Cyan/Tertiary) */}
          {groupedAgents.buyers.map((agent, idx) => {
            const y = 200 + (idx - (groupedAgents.buyers.length - 1) / 2) * 80;
            return (
              <g key={agent.walletAddress}>
                <rect
                  x="20"
                  y={y - 25}
                  width="160"
                  height="50"
                  fill="#12121a"
                  stroke="#00d4ff"
                  strokeWidth="2"
                  rx="4"
                  className="cursor-pointer hover:fill-[#1a1a28] transition-colors"
                  onClick={() => setSelectedAgent(agent)}
                />
                <text
                  x="100"
                  y={y - 5}
                  textAnchor="middle"
                  fill="#00d4ff"
                  fontSize="12"
                  fontFamily="monospace"
                  fontWeight="bold"
                  className="pointer-events-none"
                >
                  {agent.name}
                </text>
                <text
                  x="100"
                  y={y + 12}
                  textAnchor="middle"
                  fill="#e0e0e0"
                  fontSize="10"
                  fontFamily="monospace"
                  className="pointer-events-none"
                >
                  Rep: {agent.reputation.score}
                </text>
              </g>
            );
          })}

          {/* Worker Nodes (Center, Green/Accent) */}
          {groupedAgents.workers.map((agent, idx) => {
            const y = 100 + idx * 60;
            return (
              <g key={agent.walletAddress}>
                <rect
                  x="320"
                  y={y - 25}
                  width="160"
                  height="50"
                  fill="#12121a"
                  stroke="#00ff88"
                  strokeWidth="2"
                  rx="4"
                  className="cursor-pointer hover:fill-[#1a1a28] transition-colors"
                  onClick={() => setSelectedAgent(agent)}
                />
                <text
                  x="400"
                  y={y - 5}
                  textAnchor="middle"
                  fill="#00ff88"
                  fontSize="12"
                  fontFamily="monospace"
                  fontWeight="bold"
                  className="pointer-events-none"
                >
                  {agent.name}
                </text>
                <text
                  x="400"
                  y={y + 12}
                  textAnchor="middle"
                  fill="#e0e0e0"
                  fontSize="10"
                  fontFamily="monospace"
                  className="pointer-events-none"
                >
                  Rep: {agent.reputation.score}
                </text>
              </g>
            );
          })}

          {/* Verifier Nodes (Right, Magenta/Secondary) */}
          {groupedAgents.verifiers.map((agent, idx) => {
            const y = 150 + idx * 100;
            return (
              <g key={agent.walletAddress}>
                <rect
                  x="620"
                  y={y - 25}
                  width="160"
                  height="50"
                  fill="#12121a"
                  stroke="#ff00ff"
                  strokeWidth="2"
                  rx="4"
                  className="cursor-pointer hover:fill-[#1a1a28] transition-colors"
                  onClick={() => setSelectedAgent(agent)}
                />
                <text
                  x="700"
                  y={y - 5}
                  textAnchor="middle"
                  fill="#ff00ff"
                  fontSize="12"
                  fontFamily="monospace"
                  fontWeight="bold"
                  className="pointer-events-none"
                >
                  {agent.name}
                </text>
                <text
                  x="700"
                  y={y + 12}
                  textAnchor="middle"
                  fill="#e0e0e0"
                  fontSize="10"
                  fontFamily="monospace"
                  className="pointer-events-none"
                >
                  Rep: {agent.reputation.score}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Mobile: Stacked List */}
      <div className="md:hidden space-y-4">
        {/* Buyers */}
        {groupedAgents.buyers.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-mono text-xs text-accentTertiary uppercase tracking-wider">
              Buyers
            </h3>
            {groupedAgents.buyers.map((agent) => (
              <button
                key={agent.walletAddress}
                onClick={() => setSelectedAgent(agent)}
                className={cn(
                  "w-full cyber-chamfer-sm p-4 bg-card border-2 border-accentTertiary/30 hover:border-accentTertiary transition-colors text-left",
                  "min-h-[44px]"
                )}
              >
                <div className="font-mono text-sm text-accentTertiary font-bold">
                  {agent.name}
                </div>
                <div className="font-mono text-xs text-mutedForeground mt-1">
                  Rep: {agent.reputation.score}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Workers */}
        {groupedAgents.workers.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-mono text-xs text-accent uppercase tracking-wider">
              Workers
            </h3>
            {groupedAgents.workers.map((agent) => (
              <button
                key={agent.walletAddress}
                onClick={() => setSelectedAgent(agent)}
                className={cn(
                  "w-full cyber-chamfer-sm p-4 bg-card border-2 border-accent/30 hover:border-accent transition-colors text-left",
                  "min-h-[44px]"
                )}
              >
                <div className="font-mono text-sm text-accent font-bold">
                  {agent.name}
                </div>
                <div className="font-mono text-xs text-mutedForeground mt-1">
                  Rep: {agent.reputation.score}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Verifiers */}
        {groupedAgents.verifiers.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-mono text-xs text-accentSecondary uppercase tracking-wider">
              Verifiers
            </h3>
            {groupedAgents.verifiers.map((agent) => (
              <button
                key={agent.walletAddress}
                onClick={() => setSelectedAgent(agent)}
                className={cn(
                  "w-full cyber-chamfer-sm p-4 bg-card border-2 border-accentSecondary/30 hover:border-accentSecondary transition-colors text-left",
                  "min-h-[44px]"
                )}
              >
                <div className="font-mono text-sm text-accentSecondary font-bold">
                  {agent.name}
                </div>
                <div className="font-mono text-xs text-mutedForeground mt-1">
                  Rep: {agent.reputation.score}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Agent Detail Panel */}
      <AgentDetailPanel agent={selectedAgent} onClose={() => setSelectedAgent(null)} />
    </div>
  );
};
