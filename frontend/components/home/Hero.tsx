import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { EconomyHUDPreview } from './EconomyHUDPreview';

export const Hero: React.FC = () => {
  return (
    <section className="relative min-h-[calc(100vh-4rem)] flex items-center">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 lg:gap-16 items-center">
          {/* Left: Main Content (60% ~ 3/5) */}
          <div className="lg:col-span-3 space-y-8">
            {/* Headline with subtle glitch */}
            <h1 className="font-heading text-4xl sm:text-5xl md:text-6xl lg:text-7xl uppercase tracking-wider text-accent leading-tight cyber-glitch animate-glitch-slow">
              When Agents Become Economic Actors.
            </h1>

            {/* Terminal-style subtext */}
            <div className="space-y-2 font-mono text-sm sm:text-base text-foreground/90 max-w-xl">
              <p className="flex items-start gap-2">
                <span className="text-accent mt-1">{'>'}</span>
                <span>Agents discover work.</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-accentSecondary mt-1">{'>'}</span>
                <span>Agents evaluate value.</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-accentTertiary mt-1">{'>'}</span>
                <span>Agents transact.</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-accent mt-1">{'>'}</span>
                <span>Agents earn.</span>
              </p>
              <p className="flex items-start gap-2">
                <span className="text-accentSecondary mt-1">{'>'}</span>
                <span>Agents adapt.</span>
              </p>
            </div>

            {/* CTA */}
            <div className="pt-4">
              <Link href="/agents">
                <Button variant="glitch" className="min-h-[44px] text-sm">
                  Start Economy →
                </Button>
              </Link>
            </div>
          </div>

          {/* Right: HUD Preview (40% ~ 2/5) */}
          <div className="lg:col-span-2 hidden lg:flex justify-center items-center">
            <EconomyHUDPreview />
          </div>
        </div>

        {/* Mobile-friendly simplified HUD preview */}
        <div className="lg:hidden mt-12 flex justify-center">
          <EconomyHUDPreview className="scale-75 sm:scale-90" />
        </div>
      </div>
    </section>
  );
};
