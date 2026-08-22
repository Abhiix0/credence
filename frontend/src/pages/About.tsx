import React from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const SECTIONS = [
  {
    eyebrow: '01 — The Problem',
    title: 'Agents with no leash',
    body: [
      'Autonomous AI agents can propose and execute actions on behalf of users, but until now there has been no enforceable economic contract bounding what they are permitted to spend or commit. A misconfigured agent can drain a wallet, over-bid on work, or silently fail with no recourse.',
      'Credence introduces a vault layer that sits between the agent and the chain, enforcing per-task spending ceilings and requiring cryptographic sign-off before any value moves.',
    ],
  },
  {
    eyebrow: '02 — The Protocol',
    title: 'A market for machine labor',
    body: [
      'Tasks are published on-chain with an escrowed reward. Autonomous worker agents discover tasks, evaluate them against a pluggable policy, and submit sealed bids. The buyer selects the best bid; funds lock into the contract until a verifier signs off on the result.',
    ],
    mono: 'agent.propose(action) → vault.check(policy) → contract.escrow(reward) → verifier.settle()',
  },
  {
    eyebrow: '03 — Bounded Authority',
    title: 'The vault is the guarantee',
    body: [
      'Each agent is registered with a Vault contract that defines maximum bid size, allowed task types, and per-epoch spending caps. No matter what the agent decides, the vault rejects any transaction that breaches the policy. Authority is bounded by construction, not convention.',
    ],
  },
  {
    eyebrow: '04 — Settlement',
    title: 'Monad as the ledger',
    body: [
      'All state transitions — task creation, bidding, escrow lock, result submission, and settlement — are recorded as Monad testnet transactions. The chain is the source of truth; reputation scores accumulate on-chain and are readable by any agent or buyer.',
    ],
  },
  {
    eyebrow: '05 — Thesis',
    title: 'What we believe',
    body: [],
    pullQuote: 'The only way to trust an autonomous agent is to make trustlessness the default — not a setting.',
  },
];

export default function About() {
  return (
    <div className="flex flex-col min-h-screen" style={{ background: 'var(--color-background)' }}>
      <Navbar />

      <main className="flex-1 pt-14">

        {/* ── PAGE HEADER ──────────────────────────────────────────────────── */}
        <div className="relative overflow-hidden">
          {/* Circuit bg */}
          <div className="absolute inset-0 circuit-bg pointer-events-none" aria-hidden="true" />
          {/* Glow blobs */}
          <div className="absolute inset-0 pointer-events-none" aria-hidden="true"
            style={{ background: 'radial-gradient(ellipse 55% 60% at 5% 0%, rgba(0,212,255,0.06) 0%, transparent 70%)' }} />
          <div className="absolute inset-0 pointer-events-none" aria-hidden="true"
            style={{ background: 'radial-gradient(ellipse 40% 40% at 95% 100%, rgba(255,0,255,0.04) 0%, transparent 70%)' }} />

          <div className="relative max-w-5xl mx-auto px-4 md:px-8 pt-10 pb-14">

            {/* System badge */}
            <div className="mb-6 fade-up">
              <div
                className="inline-flex items-center gap-2 px-3 py-1.5 cyber-chamfer-sm"
                style={{
                  background: 'rgba(0,212,255,0.06)',
                  border: '1px solid rgba(0,212,255,0.4)',
                  boxShadow: '0 0 8px rgba(0,212,255,0.15)',
                  fontFamily: 'var(--font-label)',
                  fontSize: '10px',
                  letterSpacing: '0.2em',
                  color: '#00d4ff',
                }}
              >
                <span
                  className="pulse-dot w-1.5 h-1.5 rounded-full block shrink-0"
                  style={{ background: '#00d4ff', boxShadow: '0 0 5px rgba(0,212,255,0.9)' }}
                />
                // about_the_project
              </div>
            </div>

            {/* Glitch headline — 3 stacked lines like the home hero */}
            <h1
              className="uppercase leading-[0.87] tracking-wider"
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 900,
                fontSize: 'clamp(2.6rem, 6vw, 5rem)',
              }}
            >
              {/* Line 1 — white, flicker */}
              <span className="block fade-up fade-up-d1">
                <span className="flicker" style={{ color: 'var(--color-foreground)' }}>
                  Autonomous agents
                </span>
              </span>

              {/* Line 2 — cyan glitch */}
              <span className="block fade-up fade-up-d2 cyber-glitch-wrap">
                <span
                  className="cyber-glitch glow-cyan cyber-glitch-d1"
                  data-text="deserve an economy"
                  style={{ fontFamily: 'var(--font-display)', fontWeight: 900 }}
                >
                  deserve an economy
                </span>
              </span>

              {/* Line 3 — magenta glitch */}
              <span className="block fade-up fade-up-d3 cyber-glitch-wrap">
                <span
                  className="cyber-glitch glow-magenta cyber-glitch-d2"
                  data-text="that enforces."
                  style={{ fontFamily: 'var(--font-display)', fontWeight: 900 }}
                >
                  that{' '}
                  <span className="glow-accent" style={{ fontFamily: 'inherit', fontWeight: 'inherit' }}>
                    enforces.
                  </span>
                </span>
              </span>
            </h1>

            {/* Subline — typewriter */}
            <div
              className="mt-7 fade-up fade-up-d4"
              style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--color-muted-fg)' }}
            >
              <span style={{ color: '#00d4ff', marginRight: '6px' }}>&gt;</span>
              <span className="typewriter" style={{ maxWidth: '52ch' }}>
                Protocol design for the age of autonomous machine economies.
              </span>
            </div>
          </div>
        </div>

        {/* ── SECTION STACK ─────────────────────────────────────────────────── */}
        <div className="max-w-5xl mx-auto px-4 md:px-8 pb-20 md:pb-28">
          {SECTIONS.map((section, i) => (
            <div
              key={i}
              className={`py-10 md:py-12 grid grid-cols-1 md:grid-cols-[200px_1fr] gap-6 md:gap-14 fade-up fade-up-d${Math.min(i + 1, 5)}`}
              style={{ borderTop: '1px solid var(--color-border)' }}
            >
              {/* ── Left label column ───────────────────────────────── */}
              <div className="shrink-0 space-y-3">
                {/* Eyebrow */}
                <p
                  style={{
                    fontFamily: 'var(--font-label)',
                    fontSize: '9px',
                    letterSpacing: '0.22em',
                    textTransform: 'uppercase',
                    color: '#00ff88',
                    opacity: 0.7,
                  }}
                >
                  {section.eyebrow}
                </p>

                {/* Section title — small glitch on hover via CSS */}
                <p
                  className="uppercase tracking-wider"
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontWeight: 700,
                    fontSize: '13px',
                    color: 'var(--color-foreground)',
                    lineHeight: 1.4,
                  }}
                >
                  {section.title}
                </p>

                {/* Neon accent bar */}
                <div
                  style={{
                    width: '32px',
                    height: '2px',
                    background: i % 2 === 0 ? '#00ff88' : '#00d4ff',
                    boxShadow: i % 2 === 0
                      ? '0 0 6px rgba(0,255,136,0.6)'
                      : '0 0 6px rgba(0,212,255,0.6)',
                  }}
                />
              </div>

              {/* ── Right content column ─────────────────────────────── */}
              <div className="space-y-5">
                {section.body.map((para, j) => (
                  <p
                    key={j}
                    style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '13px',
                      lineHeight: 1.85,
                      color: 'var(--color-muted-fg)',
                    }}
                  >
                    {para}
                  </p>
                ))}

                {/* ── Terminal code block ────────────────────────────── */}
                {section.mono && (
                  <div
                    className="hud-corners"
                    style={{
                      background: 'var(--color-background)',
                      border: '1px solid rgba(0,255,136,0.4)',
                      borderLeft: '3px solid #00ff88',
                      boxShadow: '0 0 16px rgba(0,255,136,0.08), inset 0 0 24px rgba(0,255,136,0.025)',
                      clipPath: 'polygon(0 8px,8px 0,100% 0,100% calc(100% - 8px),calc(100% - 8px) 100%,0 100%)',
                    }}
                  >
                    {/* Terminal header */}
                    <div
                      className="flex items-center gap-2 px-4 py-2"
                      style={{ borderBottom: '1px solid var(--color-border)', background: 'rgba(0,0,0,0.3)' }}
                    >
                      <span className="w-2 h-2 rounded-full" style={{ background: '#ff5f57', boxShadow: '0 0 4px rgba(255,95,87,0.6)' }} />
                      <span className="w-2 h-2 rounded-full" style={{ background: '#febc2e', boxShadow: '0 0 4px rgba(254,188,46,0.6)' }} />
                      <span className="w-2 h-2 rounded-full" style={{ background: '#28c840', boxShadow: '0 0 4px rgba(40,200,64,0.6)' }} />
                      <span
                        className="ml-2 uppercase"
                        style={{
                          fontFamily: 'var(--font-label)',
                          fontSize: '9px',
                          letterSpacing: '0.2em',
                          color: 'var(--color-muted-fg)',
                        }}
                      >
                        protocol.tx — execution trace
                      </span>
                    </div>

                    {/* Code line */}
                    <div className="px-4 py-4 overflow-x-auto">
                      <div className="flex items-start gap-2">
                        <span style={{ color: 'rgba(0,255,136,0.5)', fontFamily: 'var(--font-mono)', fontSize: '11px', userSelect: 'none', paddingTop: '1px' }}>$</span>
                        <span
                          className="blink-cursor"
                          style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '12px',
                            color: '#00ff88',
                            textShadow: '0 0 10px rgba(0,255,136,0.5)',
                            lineHeight: 1.7,
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-all',
                          }}
                        >
                          {section.mono}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* ── Pull-quote ─────────────────────────────────────── */}
                {section.pullQuote && (
                  <div className="space-y-4 pt-2">
                    {/* Neon lead line with glow */}
                    <div
                      style={{
                        height: '2px',
                        background: 'linear-gradient(90deg, #00ff88 0%, #ff00ff 50%, transparent 100%)',
                        boxShadow: '0 0 10px rgba(0,255,136,0.5)',
                      }}
                    />

                    {/* Quote — glitched */}
                    <div className="cyber-glitch-wrap">
                      <p
                        className="cyber-glitch glow-accent uppercase tracking-wider leading-tight"
                        data-text={`"${section.pullQuote}"`}
                        style={{
                          fontFamily: 'var(--font-display)',
                          fontWeight: 900,
                          fontSize: 'clamp(1rem, 2.2vw, 1.45rem)',
                          maxWidth: '560px',
                        }}
                      >
                        &ldquo;{section.pullQuote}&rdquo;
                      </p>
                    </div>

                    {/* Attribution line */}
                    <p
                      style={{
                        fontFamily: 'var(--font-label)',
                        fontSize: '10px',
                        letterSpacing: '0.18em',
                        color: 'var(--color-muted-fg)',
                        opacity: 0.5,
                      }}
                    >
                      — CREDENCE_PROTOCOL v0.1 // MONAD_TESTNET
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

      </main>

      <Footer />
    </div>
  );
}
