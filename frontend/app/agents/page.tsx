'use client';

import React from 'react';
import { EconomyHeader } from '@/components/agents/EconomyHeader';
import { AgentNetwork } from '@/components/agents/AgentNetwork';
import { Panel } from '@/components/ui/Panel';

export default function AgentsPage() {
  return (
    <main className="flex-1">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Economy Stats Header */}
        <EconomyHeader />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agent Network Panel - Takes 2/3 width on desktop */}
          <div className="lg:col-span-2">
            <Panel variant="terminal" className="min-h-[500px]">
              <div className="space-y-4">
                <h2 className="font-heading text-lg uppercase tracking-wider text-accent">
                  Agent Network
                </h2>
                <AgentNetwork />
              </div>
            </Panel>
          </div>

          {/* Right Column - Current Task + Live Activity */}
          <div className="space-y-6">
            {/* Current Task Panel */}
            <Panel variant="terminal" className="min-h-[240px]">
              <div className="space-y-4">
                <h2 className="font-heading text-lg uppercase tracking-wider text-accentSecondary">
                  Current Task
                </h2>
                <p className="font-mono text-xs text-mutedForeground">
                  Task detail view coming in Phase 6...
                </p>
              </div>
            </Panel>

            {/* Live Activity Panel */}
            <Panel variant="terminal" className="min-h-[240px]">
              <div className="space-y-4">
                <h2 className="font-heading text-lg uppercase tracking-wider text-accentTertiary">
                  Live Activity
                </h2>
                <p className="font-mono text-xs text-mutedForeground">
                  Real-time activity feed coming in Phase 6...
                </p>
              </div>
            </Panel>
          </div>
        </div>
      </div>
    </main>
  );
}
