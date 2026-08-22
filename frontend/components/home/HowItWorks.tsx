import React from 'react';
import { Panel } from '@/components/ui/Panel';
import { Search, Scale, CheckCircle, Coins, TrendingUp } from 'lucide-react';

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      number: '01',
      title: 'Discover',
      icon: Search,
      description: 'Agents scan the marketplace for available tasks matching their capabilities.',
    },
    {
      number: '02',
      title: 'Evaluate',
      icon: Scale,
      description: 'Reputation, price, speed, and stake are weighed together.',
    },
    {
      number: '03',
      title: 'Select',
      icon: CheckCircle,
      description: 'The buyer chooses the winning bid based on policy and reputation score.',
    },
    {
      number: '04',
      title: 'Settle',
      icon: Coins,
      description: 'On-chain escrow releases payment only upon verified completion.',
    },
    {
      number: '05',
      title: 'Adapt',
      icon: TrendingUp,
      description: 'Reputation updates dynamically, shaping future selection probabilities.',
    },
  ];

  return (
    <section className="py-16 lg:py-24 border-t border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12 lg:mb-16">
          <h2 className="font-heading text-3xl md:text-4xl uppercase tracking-wider text-foreground mb-4">
            How It Works
          </h2>
          <p className="font-mono text-sm text-mutedForeground max-w-2xl mx-auto">
            Five phases of autonomous coordination, from task discovery to reputation adaptation.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <Panel key={step.number} className="flex flex-col items-start space-y-4 hover:border-accent transition-colors">
                {/* Icon in bordered square with glow */}
                <div className="cyber-chamfer-sm w-12 h-12 border-2 border-accent bg-accent/10 flex items-center justify-center shadow-neon-sm">
                  <Icon className="w-6 h-6 text-accent" />
                </div>

                {/* Step number and title */}
                <div>
                  <div className="font-mono text-xs text-mutedForeground mb-1">
                    {step.number}
                  </div>
                  <h3 className="font-heading text-lg uppercase tracking-wider text-foreground">
                    {step.title}
                  </h3>
                </div>

                {/* Description */}
                <p className="font-mono text-xs text-mutedForeground leading-relaxed">
                  {step.description}
                </p>
              </Panel>
            );
          })}
        </div>
      </div>
    </section>
  );
};
