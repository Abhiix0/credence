import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer
      className="mt-auto relative overflow-hidden"
      style={{ borderTop: '1px solid var(--color-border)' }}
    >
      {/* Circuit grid background strip */}
      <div className="absolute inset-0 circuit-bg opacity-60 pointer-events-none" aria-hidden="true" />

      {/* Top neon hairline */}
      <div
        className="absolute top-0 left-0 right-0 h-px pointer-events-none"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(0,255,136,0.25) 30%, rgba(0,212,255,0.25) 70%, transparent 100%)',
        }}
        aria-hidden="true"
      />

      <div className="relative max-w-5xl mx-auto px-6 md:px-10 py-10 space-y-6">
        {/* Wordmark + description */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <Link
            to="/"
            className="flex items-center gap-1 w-fit group"
            aria-label="credence home"
          >
            <span
              className="text-sm font-bold tracking-wider glow-accent"
              style={{ fontFamily: 'var(--font-label)' }}
            >
              &gt;_
            </span>
            <span
              className="text-sm font-medium tracking-wider transition-colors duration-150 group-hover:text-[#00ff88]"
              style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
            >
              credence
            </span>
          </Link>
          <p
            className="text-sm leading-relaxed max-w-sm"
            style={{ fontFamily: 'var(--font-body)', color: 'var(--color-muted-fg)' }}
          >
            A decentralized protocol for autonomous agents to earn, bid, and settle work on-chain.
          </p>
        </div>

        {/* Divider */}
        <div style={{ height: '1px', background: 'var(--color-border)' }} />

        {/* Signature */}
        <p
          className="text-xs leading-relaxed"
          style={{ fontFamily: 'var(--font-label)', color: '#3a3a52' }}
        >
          {'// signed into the ledger by '}
          <span style={{ color: '#00ff88', textShadow: '0 0 8px rgba(0,255,136,0.4)' }}>
            Vedik G
          </span>
          {', '}
          <span style={{ color: '#00ff88', textShadow: '0 0 8px rgba(0,255,136,0.4)' }}>
            Abhinav Sai G
          </span>
          {', and '}
          <span style={{ color: '#00ff88', textShadow: '0 0 8px rgba(0,255,136,0.4)' }}>
            Mahesh G
          </span>
          {' — Monad Blitz Hyderabad'}
        </p>
      </div>
    </footer>
  );
}
