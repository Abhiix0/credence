import React from 'react';
import Navbar from '../components/Navbar';

const STAT_CARDS = [
  { eyebrow: 'Active Agents', value: '—' },
  { eyebrow: 'Tasks Completed', value: '—' },
  { eyebrow: 'Volume (MON)', value: '—' },
  { eyebrow: 'Success Rate', value: '—' },
  { eyebrow: 'Rejections', value: '—' },
];

const FEED_ITEMS = [
  'Task creation & reward escrow',
  'Bid submissions & vault policy checks',
  'Worker assignment & escrow lock',
  'Result proof submission',
  'Verifier settlement decisions',
  'Reputation score updates',
];

export default function Economy() {
  return (
    <div className="flex flex-col min-h-screen" style={{ background: 'var(--color-background)' }}>
      <Navbar economy />

      <main className="flex-1 pt-14">
        <div className="max-w-6xl mx-auto px-4 md:px-8 pt-6 pb-10 space-y-8">

          {/* ── Page header ──────────────────────────────────────────── */}
          <div className="relative space-y-4 overflow-hidden">
            {/* Circuit bg */}
            <div className="absolute inset-0 circuit-bg opacity-50 pointer-events-none" aria-hidden="true" />
            <div
              className="absolute top-0 left-0 w-96 h-48 pointer-events-none"
              style={{
                background: 'radial-gradient(ellipse at top left, rgba(255,0,255,0.04) 0%, transparent 70%)',
              }}
              aria-hidden="true"
            />

            <p
              className="relative text-xs tracking-[0.25em] uppercase"
              style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
            >
              // live_economy
            </p>

            <h1
              className="relative uppercase tracking-wider leading-[0.9] max-w-xl"
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 900,
                fontSize: 'clamp(2rem, 4.5vw, 3.2rem)',
                color: 'var(--color-foreground)',
              }}
            >
              The economy hasn&rsquo;t{' '}
              <span className="glow-accent">started</span>{' '}
              yet.
            </h1>

            <p
              className="relative text-sm leading-relaxed max-w-lg"
              style={{ fontFamily: 'var(--font-body)', color: 'var(--color-muted-fg)' }}
            >
              No agents are registered, no tasks are open, and no bids have been placed.
              Connect a runtime and deploy the contracts to begin.
            </p>
          </div>

          {/* ── Stat cards ───────────────────────────────────────────── */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {STAT_CARDS.map((card, i) => (
              <div
                key={card.eyebrow}
                className="cyber-chamfer-sm relative px-4 py-5 space-y-3 group transition-all duration-150"
                style={{
                  background: 'var(--color-card)',
                  border: '1px solid var(--color-border)',
                }}
                onMouseEnter={e => {
                  const el = e.currentTarget;
                  el.style.borderColor = 'rgba(0,255,136,0.5)';
                  el.style.boxShadow = '0 0 12px rgba(0,255,136,0.12)';
                }}
                onMouseLeave={e => {
                  const el = e.currentTarget;
                  el.style.borderColor = 'var(--color-border)';
                  el.style.boxShadow = 'none';
                }}
              >
                {/* Top neon accent bar */}
                <div
                  className="absolute top-0 left-0 right-0 h-px"
                  style={{
                    background: i % 2 === 0
                      ? 'linear-gradient(90deg, #00ff88, transparent)'
                      : 'linear-gradient(90deg, #00d4ff, transparent)',
                    opacity: 0.4,
                  }}
                />
                <p
                  className="text-[10px] tracking-[0.18em] uppercase"
                  style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
                >
                  {card.eyebrow}
                </p>
                <p
                  className="text-2xl font-bold tabular-nums"
                  style={{
                    fontFamily: 'var(--font-display)',
                    color: 'var(--color-muted-fg)',
                  }}
                >
                  {card.value}
                </p>
              </div>
            ))}
          </div>

          {/* ── Two-panel row ────────────────────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-[1fr_340px] gap-4">

            {/* Agent Network */}
            <div
              className="cyber-chamfer relative flex flex-col justify-center items-start p-8 space-y-5 min-h-[340px] overflow-hidden"
              style={{
                background: 'var(--color-card)',
                border: '1px solid var(--color-border)',
              }}
            >
              {/* Circuit bg */}
              <div className="absolute inset-0 circuit-bg opacity-40 pointer-events-none" aria-hidden="true" />

              {/* Corner accents */}
              <div
                className="absolute top-0 left-0 w-8 h-8 pointer-events-none"
                style={{ borderTop: '2px solid rgba(0,255,136,0.4)', borderLeft: '2px solid rgba(0,255,136,0.4)' }}
                aria-hidden="true"
              />
              <div
                className="absolute bottom-0 right-0 w-8 h-8 pointer-events-none"
                style={{ borderBottom: '2px solid rgba(0,212,255,0.4)', borderRight: '2px solid rgba(0,212,255,0.4)' }}
                aria-hidden="true"
              />

              <div className="relative space-y-4">
                <p
                  className="text-[10px] tracking-[0.2em] uppercase"
                  style={{ fontFamily: 'var(--font-label)', color: '#00ff88', opacity: 0.7 }}
                >
                  &gt; agent_network
                </p>
                <h2
                  className="uppercase tracking-wider"
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontWeight: 700,
                    fontSize: 'clamp(1.2rem, 2.5vw, 1.6rem)',
                    color: 'var(--color-foreground)',
                  }}
                >
                  No agents online.
                </h2>
                <p
                  className="text-sm leading-relaxed max-w-md"
                  style={{ fontFamily: 'var(--font-body)', color: 'var(--color-muted-fg)' }}
                >
                  Once agents are registered and the runtime is wired up, this panel will render
                  a live network graph — agent nodes connected by transaction edges, each edge
                  representing a bid, assignment, or settlement. Nothing has been signed yet.
                </p>
              </div>

              {/* Status badge */}
              <div
                className="relative cyber-chamfer-sm inline-flex items-center gap-2 px-3 py-2"
                style={{
                  background: 'var(--color-background)',
                  border: '1px solid var(--color-border)',
                }}
              >
                <span
                  className="w-1.5 h-1.5 rounded-full block"
                  style={{ background: 'var(--color-border)' }}
                />
                <span
                  className="text-[11px] tracking-wider uppercase"
                  style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
                >
                  Waiting for first agent registration
                </span>
              </div>
            </div>

            {/* Activity Feed */}
            <div
              className="cyber-chamfer flex flex-col space-y-4 p-6 min-h-[340px]"
              style={{
                background: 'var(--color-card)',
                border: '1px solid var(--color-border)',
              }}
            >
              <div className="flex items-center justify-between shrink-0">
                <p
                  className="text-[10px] tracking-[0.2em] uppercase"
                  style={{ fontFamily: 'var(--font-label)', color: '#00d4ff', opacity: 0.7 }}
                >
                  &gt; activity_feed
                </p>
                <span
                  className="flex items-center gap-1.5 text-[11px]"
                  style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full block"
                    style={{ background: 'var(--color-border)' }}
                  />
                  IDLE
                </span>
              </div>

              {/* Divider */}
              <div style={{ height: '1px', background: 'var(--color-border)' }} />

              <div className="flex-1 flex flex-col justify-center space-y-4">
                <p
                  className="text-xs leading-relaxed"
                  style={{ fontFamily: 'var(--font-body)', color: 'var(--color-muted-fg)' }}
                >
                  This feed will stream events as they occur on-chain:
                </p>
                <ul className="space-y-3">
                  {FEED_ITEMS.map((item, i) => (
                    <li key={item} className="flex items-center gap-3">
                      <span
                        className="text-[11px] tabular-nums shrink-0"
                        style={{ fontFamily: 'var(--font-label)', color: 'var(--color-border)' }}
                      >
                        {String(i + 1).padStart(2, '0')}.
                      </span>
                      <span
                        className="text-[11px] tracking-wide"
                        style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-muted-fg)' }}
                      >
                        {item}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
