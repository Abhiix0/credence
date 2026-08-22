import React from 'react';
import Link from 'next/link';
import { StatusDot } from '@/components/ui/StatusDot';
import { Github } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-border bg-card/50 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          {/* Left: Project Info */}
          <div className="space-y-2">
            <h3 className="font-heading text-sm uppercase tracking-wider text-foreground">
              Credence
            </h3>
            <p className="font-mono text-xs text-mutedForeground leading-relaxed">
              Autonomous agent economy on Monad testnet
            </p>
          </div>

          {/* Center: Network Info */}
          <div className="flex flex-col items-center gap-2">
            <div className="flex items-center gap-2">
              <StatusDot tone="accent" pulse />
              <span className="font-mono text-xs text-foreground">System Online</span>
            </div>
            <span className="font-mono text-xs text-mutedForeground">Monad Testnet</span>
          </div>

          {/* Right: Links */}
          <div className="flex items-center justify-end gap-4">
            <Link
              href="#"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-mutedForeground hover:text-accent transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
