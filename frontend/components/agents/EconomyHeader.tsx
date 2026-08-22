'use client';

import React from 'react';
import { StatusDot } from '@/components/ui/StatusDot';
import { Panel } from '@/components/ui/Panel';
import { useEconomyStats } from '@/lib/data/useEconomyData';

export const EconomyHeader: React.FC = () => {
  const { data: stats, isLoading } = useEconomyStats();

  return (
    <div className="space-y-4">
      {/* Title Row */}
      <div className="flex items-center gap-3">
        <h1 className="font-heading text-2xl md:text-3xl uppercase tracking-wider text-foreground">
          Economy
        </h1>
        <StatusDot tone="accent" pulse />
        <span className="font-mono text-sm text-accent uppercase tracking-wider">
          Live
        </span>
      </div>

      {/* Stats Panel */}
      <Panel className="!p-0 overflow-hidden">
        {isLoading ? (
          // Loading skeleton
          <div className="grid grid-cols-2 lg:grid-cols-5">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="p-4 lg:p-6 border-r border-b lg:border-b-0 last:border-r-0 border-border"
              >
                <div className="space-y-2">
                  <div className="h-3 bg-muted animate-pulse rounded w-20" />
                  <div className="h-6 bg-muted animate-pulse rounded w-12" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          // Actual stats
          <div className="grid grid-cols-2 lg:grid-cols-5 divide-x-0 lg:divide-x divide-border">
            <div className="p-4 lg:p-6 border-r border-b lg:border-b-0 border-border">
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-1">
                Agents Online
              </div>
              <div className="font-heading text-2xl text-accent">
                {stats?.agentsOnline ?? 0}
              </div>
            </div>

            <div className="p-4 lg:p-6 border-b lg:border-b-0 border-border lg:border-r-0">
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-1">
                Active Tasks
              </div>
              <div className="font-heading text-2xl text-accentSecondary">
                {stats?.activeTasks ?? 0}
              </div>
            </div>

            <div className="p-4 lg:p-6 border-r border-border">
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-1">
                Transactions
              </div>
              <div className="font-heading text-2xl text-foreground">
                {stats?.totalTransactions ?? 0}
              </div>
            </div>

            <div className="p-4 lg:p-6 border-b lg:border-b-0 border-border lg:border-r-0">
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-1">
                Volume
              </div>
              <div className="font-heading text-2xl text-accentTertiary">
                {stats?.volumeFormatted ?? '0 MON'}
              </div>
            </div>

            <div className="p-4 lg:p-6">
              <div className="font-mono text-xs text-mutedForeground uppercase tracking-wider mb-1">
                Success Rate
              </div>
              <div className="font-heading text-2xl text-accent">
                {stats?.successRatePct ?? 0}%
              </div>
            </div>
          </div>
        )}
      </Panel>
    </div>
  );
};
