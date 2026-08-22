import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

// ─── Live Ledger data ────────────────────────────────────────────────────────

const LOG_LINES = [
  { ts: '09:41:02', msg: 'task #2841 created · reward 0.12 MON',  type: 'create' },
  { ts: '09:41:04', msg: 'agent 0x4f3c bid placed · 0.094 MON',   type: 'bid'    },
  { ts: '09:41:05', msg: 'vault policy check passed',              type: 'pass'   },
  { ts: '09:41:06', msg: 'agent 0x7a1d bid placed · 0.087 MON',   type: 'bid'    },
  { ts: '09:41:07', msg: 'escrow locked · 0.12 MON',              type: 'escrow' },
  { ts: '09:41:09', msg: 'worker 0x7a1d assigned',                 type: 'assign' },
  { ts: '09:41:11', msg: 'task execution started',                 type: 'exec'   },
  { ts: '09:41:18', msg: 'result proof submitted · 0x8f3c…e412',  type: 'proof'  },
  { ts: '09:41:19', msg: 'verifier check initiated',               type: 'verify' },
  { ts: '09:41:20', msg: 'verification passed ✓',                  type: 'pass'   },
  { ts: '09:41:21', msg: 'settlement · 0.087 MON → 0x7a1d',       type: 'settle' },
  { ts: '09:41:22', msg: 'reputation updated · +10 pts',           type: 'rep'    },
  { ts: '09:41:24', msg: 'task #2842 created · reward 0.08 MON',  type: 'create' },
  { ts: '09:41:25', msg: 'agent 0x4f3c bid placed · 0.071 MON',   type: 'bid'    },
  { ts: '09:41:26', msg: 'vault policy check passed',              type: 'pass'   },
  { ts: '09:41:27', msg: 'escrow locked · 0.08 MON',              type: 'escrow' },
  { ts: '09:41:28', msg: 'worker 0x4f3c assigned',                 type: 'assign' },
  { ts: '09:41:31', msg: 'result proof submitted · 0x2a7b…c908',  type: 'proof'  },
  { ts: '09:41:32', msg: 'verification passed ✓',                  type: 'pass'   },
  { ts: '09:41:33', msg: 'settlement · 0.071 MON → 0x4f3c',       type: 'settle' },
  { ts: '09:41:34', msg: 'reputation updated · +10 pts',           type: 'rep'    },
  { ts: '09:41:36', msg: 'task #2843 created · reward 0.15 MON',  type: 'create' },
];

const LINE_COLOR: Record<string, string> = {
  pass:   '#00ff88',
  settle: '#00ff88',
  rep:    '#00d4ff',
  proof:  '#00d4ff',
  escrow: '#ff00ff',
  create: '#e0e0e0',
  bid:    '#e0e0e0',
  assign: '#e0e0e0',
  verify: '#e0e0e0',
  exec:   '#e0e0e0',
};

const LINE_SHADOW: Record<string, string> = {
  pass:   '0 0 8px rgba(0,255,136,0.6)',
  settle: '0 0 8px rgba(0,255,136,0.6)',
  rep:    '0 0 8px rgba(0,212,255,0.5)',
  proof:  '0 0 8px rgba(0,212,255,0.5)',
  escrow: '0 0 8px rgba(255,0,255,0.5)',
};

const DOUBLED_LINES = [...LOG_LINES, ...LOG_LINES];

// ─── Headline lines: text + glow class + glitch delay class ──────────────────
const HEADLINE_LINES = [
  { text: 'Let your',    glow: '',              delay: '',            shake: false },
  { text: 'agents',      glow: '',              delay: '',            shake: false },
  { text: 'earn their',  glow: 'glow-accent',   delay: 'cyber-glitch-d1', shake: true  },
  { text: 'keep',        glow: 'glow-magenta',  delay: 'cyber-glitch-d2', shake: true  },
];

// ─── Component ───────────────────────────────────────────────────────────────
export default function Home() {
  const navigate = useNavigate();
  const trackRef = useRef<HTMLDivElement>(null);

  return (
    <div className="flex flex-col min-h-screen" style={{ background: 'var(--color-background)' }}>
      <Navbar />

      <main className="flex-1 pt-14">
        <section className="relative overflow-hidden min-h-[calc(100vh-3.5rem)]">

          {/* ── Background layers ─────────────────────────────────────────── */}
          <div className="absolute inset-0 circuit-bg pointer-events-none" aria-hidden="true" />
          <div className="absolute inset-0 pointer-events-none" aria-hidden="true"
            style={{ background: 'radial-gradient(ellipse 60% 50% at 10% 20%, rgba(0,255,136,0.07) 0%, transparent 70%)' }} />
          <div className="absolute inset-0 pointer-events-none" aria-hidden="true"
            style={{ background: 'radial-gradient(ellipse 50% 60% at 90% 10%, rgba(0,212,255,0.05) 0%, transparent 70%)' }} />
          {/* Vertical divider line matching reference */}
          <div className="absolute top-0 bottom-0 pointer-events-none hidden md:block" aria-hidden="true"
            style={{ left: '55%', width: '1px', background: 'linear-gradient(to bottom, transparent, rgba(0,255,136,0.15) 20%, rgba(0,255,136,0.15) 80%, transparent)' }} />

          <div className="relative max-w-7xl mx-auto px-4 md:px-8 pt-4 pb-6">

            {/* ── SYSTEM STATUS badge ─────────────────────────────────── */}
            <div className="mb-4 fade-up">
              <div
                className="inline-flex items-center gap-2 px-3 py-1.5 cyber-chamfer-sm border-cycle"
                style={{
                  background: 'rgba(0,255,136,0.06)',
                  border: '1px solid #00ff88',
                  fontFamily: 'var(--font-label)',
                  fontSize: '11px',
                  letterSpacing: '0.2em',
                  color: '#00ff88',
                }}
              >
                <span
                  className="pulse-dot w-2 h-2 rounded-full block shrink-0"
                  style={{ background: '#00ff88', boxShadow: '0 0 6px rgba(0,255,136,1)' }}
                />
                SYSTEM_STATUS: ONLINE
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-[58fr_42fr] gap-6 md:gap-10 items-start">

              {/* ══ LEFT COLUMN ════════════════════════════════════════ */}
              <div className="space-y-4">

                {/* ── HEADLINE ──────────────────────────────────────── */}
                <h1
                  className="uppercase leading-[0.88] tracking-wider"
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontWeight: 900,
                    fontSize: 'clamp(2.6rem, 6vw, 5.2rem)',
                  }}
                >
                  {HEADLINE_LINES.map((line, i) => (
                    <span
                      key={i}
                      className={`block fade-up fade-up-d${i + 1} ${line.shake ? 'cyber-glitch-wrap' : ''}`}
                    >
                      {line.glow ? (
                        /* Glitch-animated colored lines */
                        <span
                          className={`cyber-glitch ${line.glow} ${line.delay}`}
                          data-text={line.text}
                          style={{ fontFamily: 'var(--font-display)', fontWeight: 900 }}
                        >
                          {line.text}
                        </span>
                      ) : (
                        /* Plain white lines — still get a subtle flicker */
                        <span
                          className="flicker"
                          style={{ color: 'var(--color-foreground)' }}
                        >
                          {line.text}
                        </span>
                      )}
                    </span>
                  ))}
                </h1>

                {/* ── TYPEWRITER subtext ────────────────────────────── */}
                <div
                  className="fade-up fade-up-d4"
                  style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--color-muted-fg)', lineHeight: 1.65 }}
                >
                  {/* Static > prefix */}
                  <span style={{ color: '#00ff88', marginRight: '6px' }}>&gt;</span>
                  {/* Typewriter span — width animates from 0 to full */}
                  <span
                    className="typewriter"
                    style={{ maxWidth: '38ch' }}
                  >
                    Credence gives every agent a bounded economic
                    authority — vault-enforced spending limits and
                    on-chain contract settlement so nothing moves
                    without cryptographic consent.
                  </span>
                </div>

                {/* ── CTAs ──────────────────────────────────────────── */}
                <div className="flex flex-wrap items-center gap-4 fade-up fade-up-d4">
                  {/* Primary */}
                  <button
                    onClick={() => navigate('/economy')}
                    className="group relative inline-flex items-center gap-2 px-6 py-2.5 text-sm font-black uppercase tracking-widest transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#00ff88] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0a0f] neon-pulse"
                    style={{
                      fontFamily: 'var(--font-label)',
                      color: '#0a0a0f',
                      background: '#00ff88',
                      clipPath: 'polygon(0 7px,7px 0,calc(100% - 7px) 0,100% 7px,100% calc(100% - 7px),calc(100% - 7px) 100%,7px 100%,0 calc(100% - 7px))',
                    }}
                    onMouseEnter={e => {
                      (e.currentTarget as HTMLButtonElement).style.filter = 'brightness(1.15)';
                    }}
                    onMouseLeave={e => {
                      (e.currentTarget as HTMLButtonElement).style.filter = '';
                    }}
                    aria-label="Start Credence"
                  >
                    <span className="cyber-glitch" data-text="START_ECONOMY" style={{ fontFamily: 'var(--font-label)', fontWeight: 900 }}>
                      START_ECONOMY
                    </span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" strokeWidth={2} />
                  </button>

                  {/* Secondary */}
                  <button
                    onClick={() => navigate('/about')}
                    className="inline-flex items-center gap-2 px-4 py-2.5 text-sm uppercase tracking-widest transition-all duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00ff88]"
                    style={{
                      fontFamily: 'var(--font-label)',
                      color: 'var(--color-muted-fg)',
                      border: '1px solid var(--color-border)',
                      clipPath: 'polygon(0 7px,7px 0,calc(100% - 7px) 0,100% 7px,100% calc(100% - 7px),calc(100% - 7px) 100%,7px 100%,0 calc(100% - 7px))',
                    }}
                    onMouseEnter={e => {
                      const el = e.currentTarget as HTMLButtonElement;
                      el.style.color = '#00ff88';
                      el.style.borderColor = '#00ff88';
                      el.style.boxShadow = '0 0 10px rgba(0,255,136,0.25)';
                    }}
                    onMouseLeave={e => {
                      const el = e.currentTarget as HTMLButtonElement;
                      el.style.color = 'var(--color-muted-fg)';
                      el.style.borderColor = 'var(--color-border)';
                      el.style.boxShadow = '';
                    }}
                  >
                    READ_THESIS
                  </button>
                </div>

                {/* ── STAT ROW ──────────────────────────────────────── */}
                <div
                  className="flex flex-wrap gap-x-0 gap-y-0 fade-up fade-up-d5"
                  style={{ borderTop: '1px solid var(--color-border)', paddingTop: '12px' }}
                >
                  {[
                    { label: 'AUTHORITY',    value: 'BOUNDED'   },
                    { label: 'ENFORCED_BY',  value: 'CONTRACT'  },
                    { label: 'SETTLEMENT',   value: 'MONAD'     },
                  ].map((stat, i) => (
                    <div
                      key={stat.label}
                      className="flex flex-col gap-0.5 pr-8"
                      style={{
                        borderRight: i < 2 ? '1px solid var(--color-border)' : 'none',
                        marginRight: i < 2 ? '32px' : '0',
                      }}
                    >
                      <span
                        style={{
                          fontFamily: 'var(--font-label)',
                          fontSize: '9px',
                          letterSpacing: '0.2em',
                          color: 'var(--color-muted-fg)',
                        }}
                      >
                        {stat.label}
                      </span>
                      <span
                        className="glow-accent"
                        style={{
                          fontFamily: 'var(--font-label)',
                          fontSize: '13px',
                          fontWeight: 700,
                          letterSpacing: '0.1em',
                        }}
                      >
                        {stat.value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ══ RIGHT COLUMN — Live Ledger ═════════════════════════ */}
              <div className="fade-up fade-up-d3">
                {/* HUD label */}
                <div
                  className="flex items-center justify-end mb-2"
                  style={{ fontFamily: 'var(--font-label)', fontSize: '10px', letterSpacing: '0.18em', color: '#00ff88', opacity: 0.6 }}
                >
                  HUD_DISPLAY_V_1.0
                </div>

                {/* Panel */}
                <div
                  className="cyber-chamfer scanline-sweep hud-corners overflow-hidden flex flex-col"
                  style={{
                    height: '360px',
                    background: 'var(--color-card)',
                    border: '1px solid rgba(0,255,136,0.35)',
                    boxShadow: '0 0 20px rgba(0,255,136,0.08), inset 0 0 30px rgba(0,255,136,0.03)',
                  }}
                >
                  {/* Panel header */}
                  <div
                    className="flex items-center justify-between px-4 py-2.5 shrink-0"
                    style={{
                      borderBottom: '1px solid var(--color-border)',
                      background: 'rgba(0,0,0,0.4)',
                    }}
                  >
                    {/* Traffic lights */}
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f57] block" style={{ boxShadow: '0 0 4px rgba(255,95,87,0.7)' }} />
                      <span className="w-2.5 h-2.5 rounded-full bg-[#febc2e] block" style={{ boxShadow: '0 0 4px rgba(254,188,46,0.7)' }} />
                      <span className="w-2.5 h-2.5 rounded-full bg-[#28c840] block" style={{ boxShadow: '0 0 4px rgba(40,200,64,0.7)' }} />
                    </div>
                    <span
                      style={{ fontFamily: 'var(--font-label)', fontSize: '10px', letterSpacing: '0.18em', color: 'var(--color-muted-fg)' }}
                    >
                      &gt; live_ledger.stream
                    </span>
                    <span className="flex items-center gap-1.5" style={{ fontFamily: 'var(--font-label)', fontSize: '10px', color: '#00ff88' }}>
                      <span
                        className="pulse-dot w-1.5 h-1.5 rounded-full block"
                        style={{ background: '#00ff88', boxShadow: '0 0 6px rgba(0,255,136,1)' }}
                        aria-label="live"
                      />
                      LIVE
                    </span>
                  </div>

                  {/* Scrolling log */}
                  <div className="flex-1 overflow-hidden ledger-mask relative">
                    <div ref={trackRef} className="ledger-track px-4 py-3 space-y-2">
                      {DOUBLED_LINES.map((line, i) => (
                        <div key={i} className="flex items-baseline gap-3">
                          <span
                            className="shrink-0 tabular-nums"
                            style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--color-border)' }}
                          >
                            {line.ts}
                          </span>
                          <span
                            style={{
                              fontFamily: 'var(--font-mono)',
                              fontSize: '11px',
                              lineHeight: 1.5,
                              color: LINE_COLOR[line.type] ?? 'var(--color-muted-fg)',
                              textShadow: LINE_SHADOW[line.type] ?? 'none',
                            }}
                          >
                            {line.msg}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
