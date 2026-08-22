import React from 'react';
import { useAccount, useConnect, useDisconnect } from 'wagmi';
import { Wallet, LogOut } from 'lucide-react';

export function WalletConnect() {
  const { address, isConnected } = useAccount();
  const { connect, connectors, isPending } = useConnect();
  const { disconnect } = useDisconnect();

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  if (isConnected && address) {
    return (
      <div className="flex items-center gap-3">
        <div
          className="cyber-chamfer-sm flex items-center gap-2 px-3 py-1.5"
          style={{
            background: 'rgba(0,255,136,0.08)',
            border: '1px solid rgba(0,255,136,0.4)',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full block pulse-dot"
            style={{ background: '#00ff88', boxShadow: '0 0 6px rgba(0,255,136,1)' }}
          />
          <span
            className="text-xs font-mono tracking-wider"
            style={{ color: '#00ff88', fontFamily: 'var(--font-mono)' }}
          >
            {formatAddress(address)}
          </span>
        </div>
        <button
          onClick={() => disconnect()}
          className="inline-flex items-center gap-1.5 px-2 py-1.5 text-xs transition-all duration-150"
          style={{
            fontFamily: 'var(--font-label)',
            color: 'var(--color-muted-fg)',
            border: '1px solid var(--color-border)',
            background: 'transparent',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#ff5f57';
            e.currentTarget.style.color = '#ff5f57';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--color-border)';
            e.currentTarget.style.color = 'var(--color-muted-fg)';
          }}
          aria-label="Disconnect wallet"
        >
          <LogOut className="w-3 h-3" />
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => {
        const connector = connectors[0];
        if (connector) {
          connect({ connector });
        }
      }}
      disabled={isPending}
      className="cyber-chamfer-sm inline-flex items-center gap-2 px-4 py-2 text-xs uppercase tracking-widest transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
      style={{
        fontFamily: 'var(--font-label)',
        color: 'var(--color-foreground)',
        border: '1px solid rgba(0,255,136,0.5)',
        background: 'rgba(0,255,136,0.05)',
      }}
      onMouseEnter={(e) => {
        if (!isPending) {
          e.currentTarget.style.background = 'rgba(0,255,136,0.12)';
          e.currentTarget.style.boxShadow = '0 0 12px rgba(0,255,136,0.2)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'rgba(0,255,136,0.05)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <Wallet className="w-3.5 h-3.5" />
      {isPending ? 'Connecting...' : 'Connect Wallet'}
    </button>
  );
}
