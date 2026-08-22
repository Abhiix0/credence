import React from 'react';
import { Bot, Cpu, ShieldCheck, Zap } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-zinc-200 bg-white sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-zinc-900 flex items-center justify-center text-white">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-zinc-900 tracking-tight">
              Autonomous Agent Economy
            </h1>
            <p className="text-xs text-zinc-500 font-mono">Monad Testnet • Chain ID 10143</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-md bg-zinc-100 border border-zinc-200 text-xs font-mono text-zinc-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Market Active</span>
          </div>
          <div className="px-3 py-1.5 rounded-md bg-zinc-900 text-white text-xs font-medium flex items-center space-x-1.5">
            <Zap className="w-3.5 h-3.5" />
            <span>Escrow Protocol</span>
          </div>
        </div>
      </div>
    </header>
  );
};
