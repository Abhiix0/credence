import React from 'react';
import { Agent } from '@/lib/types';
import { Panel } from '@/components/ui/Panel';
import { Badge } from '@/components/ui/Badge';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface AgentDetailPanelProps {
  agent: Agent | null;
  onClose: () => void;
}

export const AgentDetailPanel: React.FC<AgentDetailPanelProps> = ({ agent, onClose }) => {
  if (!agent) return null;

  const successRate = agent.reputation.completedTasks + agent.reputation.failedTasks > 0
    ? ((agent.reputation.completedTasks / (agent.reputation.completedTasks + agent.reputation.failedTasks)) * 100).toFixed(1)
    : '0.0';

  const truncateAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const getRoleTone = (role?: 'buyer' | 'worker' | 'verifier'): 'accent' | 'secondary' | 'tertiary' | 'neutral' => {
    if (role === 'buyer') return 'tertiary';
    if (role === 'worker') return 'accent';
    if (role === 'verifier') return 'secondary';
    return 'neutral';
  };

  return (
    <>
      {/* Mobile: Bottom sheet overlay */}
      <div 
        className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
        onClick={onClose}
      />
      
      {/* Panel - bottom sheet on mobile, side panel on desktop */}
      <div className={cn(
        "fixed z-50 bg-card border border-border cyber-chamfer",
        "bottom-0 left-0 right-0 max-h-[80vh] overflow-y-auto",
        "lg:top-24 lg:right-6 lg:bottom-auto lg:left-auto lg:w-96 lg:max-h-[calc(100vh-8rem)]"
      )}>
        <Panel variant="terminal" className="!border-0">
          <div className="space-y-6">
            {/* Header with close button */}
            <div className="flex items-start justify-between">
              <div>
                <h2 className="font-heading text-xl uppercase tracking-wider text-foreground">
                  {agent.name}
                </h2>
                <p className="font-mono text-xs text-mutedForeground mt-1">
                  {truncateAddress(agent.walletAddress)}
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-muted rounded transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                aria-label="Close panel"
              >
                <X className="w-5 h-5 text-mutedForeground" />
              </button>
            </div>

            {/* Role Badge */}
            {agent.role && (
              <div>
                <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-2">
                  Role
                </div>
                <Badge tone={getRoleTone(agent.role)}>
                  {agent.role}
                </Badge>
              </div>
            )}

            {/* Reputation Score */}
            <div>
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-2">
                Reputation Score
              </div>
              <div className="font-heading text-3xl text-accent">
                {agent.reputation.score}
              </div>
            </div>

            {/* Balance (mock, labeled) */}
            {agent.balanceFormatted && (
              <div>
                <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-2">
                  Balance <span className="text-accentSecondary">(mock)</span>
                </div>
                <div className="font-mono text-lg text-foreground">
                  {agent.balanceFormatted}
                </div>
              </div>
            )}

            {/* Success Rate */}
            <div>
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-2">
                Success Rate
              </div>
              <div className="font-heading text-2xl text-accentTertiary">
                {successRate}%
              </div>
              <div className="flex items-center gap-4 mt-2 font-mono text-xs text-mutedForeground">
                <span>Completed: {agent.reputation.completedTasks}</span>
                <span>Failed: {agent.reputation.failedTasks}</span>
              </div>
            </div>

            {/* Capabilities */}
            <div>
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-2">
                Capabilities
              </div>
              <div className="flex flex-wrap gap-2">
                {agent.capabilities.map((cap) => (
                  <Badge key={cap} tone="neutral">
                    {cap}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Policy */}
            {agent.policyName && (
              <div>
                <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-2">
                  Policy
                </div>
                <div className="font-mono text-sm text-foreground">
                  {agent.policyName}
                </div>
              </div>
            )}
          </div>
        </Panel>
      </div>
    </>
  );
};
