import React, { useState, useEffect } from 'react';
import { useAccount } from 'wagmi';
import { formatEther } from 'viem';
import Navbar from '../components/Navbar';
import { ToastContainer } from '../components/ToastContainer';
import { useToast } from '../hooks/useToast';
import { useGetAllAgents, useRegisterAgent, type Agent } from '../hooks/useAgentRegistry';
import { useTotalTasks, useGetTask, TaskStatus } from '../hooks/useTaskMarket';

const FEED_ITEMS = [
  'Task creation & reward escrow',
  'Bid submissions & vault policy checks',
  'Worker assignment & escrow lock',
  'Result proof submission',
  'Verifier settlement decisions',
  'Reputation score updates',
];

export default function Economy() {
  const { address, isConnected } = useAccount();
  const { toasts, showToast, removeToast } = useToast();
  
  // Fetch all agents
  const { data: agentAddresses, refetch: refetchAgents } = useGetAllAgents();
  
  // Fetch total tasks
  const { data: totalTasks, refetch: refetchTasks } = useTotalTasks();
  
  // Agent registration
  const { registerAgent, isPending: isRegistering, isConfirming: isRegisterConfirming, isSuccess: isRegisterSuccess } = useRegisterAgent();
  
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [agentName, setAgentName] = useState('');
  const [capabilities, setCapabilities] = useState('');

  // Track registration status
  useEffect(() => {
    if (isRegistering) {
      showToast('Submitting registration transaction...', 'pending', 0);
    }
  }, [isRegistering]);

  useEffect(() => {
    if (isRegisterConfirming) {
      showToast('Waiting for confirmation...', 'pending', 0);
    }
  }, [isRegisterConfirming]);

  useEffect(() => {
    if (isRegisterSuccess) {
      showToast('Agent registered successfully!', 'success');
      setShowRegisterModal(false);
      setAgentName('');
      setCapabilities('');
      refetchAgents();
    }
  }, [isRegisterSuccess]);

  const handleRegister = () => {
    if (!agentName.trim()) {
      showToast('Please enter an agent name', 'error');
      return;
    }
    const caps = capabilities.split(',').map(c => c.trim()).filter(c => c);
    if (caps.length === 0) {
      showToast('Please enter at least one capability', 'error');
      return;
    }
    registerAgent(agentName, caps);
  };

  // Calculate stats from contract data
  const activeAgents = agentAddresses?.length || 0;
  const totalTasksNum = totalTasks ? Number(totalTasks) : 0;
  const STAT_CARDS = [
    { eyebrow: 'Active Agents', value: activeAgents.toString() },
    { eyebrow: 'Total Tasks', value: totalTasksNum.toString() },
    { eyebrow: 'Volume (MON)', value: '—' },
    { eyebrow: 'Success Rate', value: '—' },
    { eyebrow: 'Network', value: isConnected ? 'Connected' : 'Disconnected' },
  ];

  return (
    <div className="flex flex-col min-h-screen" style={{ background: 'var(--color-background)' }}>
      <Navbar economy />
      <ToastContainer toasts={toasts} onRemove={removeToast} />

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
              className="relative text-xs tracking-[0.25em] uppercase fade-up"
              style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
            >
              // live_economy
            </p>

            <div className="flex items-start justify-between gap-4">
              <div>
                <h1
                  className="relative uppercase tracking-wider leading-[0.88]"
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontWeight: 900,
                    fontSize: 'clamp(2rem, 4.5vw, 3.2rem)',
                  }}
                >
                  {activeAgents === 0 ? (
                    <>
                      {/* Line 1 — white, flicker */}
                      <span className="block fade-up fade-up-d1">
                        <span className="flicker" style={{ color: 'var(--color-foreground)' }}>
                          The economy
                        </span>
                      </span>
                      {/* Line 2 — white + glitch on "hasn't" */}
                      <span className="block fade-up fade-up-d2 cyber-glitch-wrap">
                        <span className="flicker" style={{ color: 'var(--color-foreground)' }}>hasn&rsquo;t{' '}</span>
                        <span
                          className="cyber-glitch glow-accent cyber-glitch-d1"
                          data-text="started"
                          style={{ fontFamily: 'var(--font-display)', fontWeight: 900 }}
                        >
                          started
                        </span>
                      </span>
                      {/* Line 3 — magenta glitch */}
                      <span className="block fade-up fade-up-d3 cyber-glitch-wrap">
                        <span
                          className="cyber-glitch glow-magenta cyber-glitch-d2"
                          data-text="yet."
                          style={{ fontFamily: 'var(--font-display)', fontWeight: 900 }}
                        >
                          yet.
                        </span>
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="block fade-up fade-up-d1">
                        <span className="flicker" style={{ color: 'var(--color-foreground)' }}>
                          Economy
                        </span>
                      </span>
                      <span className="block fade-up fade-up-d2 cyber-glitch-wrap">
                        <span
                          className="cyber-glitch glow-accent cyber-glitch-d1"
                          data-text="online"
                          style={{ fontFamily: 'var(--font-display)', fontWeight: 900 }}
                        >
                          online
                        </span>
                      </span>
                    </>
                  )}
                </h1>

                <p
                  className="relative text-sm leading-relaxed max-w-lg fade-up fade-up-d4 mt-4"
                  style={{ fontFamily: 'var(--font-body)', color: 'var(--color-muted-fg)' }}
                >
                  {activeAgents === 0
                    ? 'No agents are registered, no tasks are open, and no bids have been placed. Connect your wallet and register as an agent to begin.'
                    : `${activeAgents} agent${activeAgents !== 1 ? 's' : ''} registered · ${totalTasksNum} task${totalTasksNum !== 1 ? 's' : ''} created · Live on Monad`}
                </p>
              </div>

              {isConnected && (
                <button
                  onClick={() => setShowRegisterModal(true)}
                  className="cyber-chamfer-sm px-4 py-2 text-xs uppercase tracking-widest transition-all duration-150 shrink-0"
                  style={{
                    fontFamily: 'var(--font-label)',
                    color: '#0a0a0f',
                    background: '#00ff88',
                    border: '1px solid #00ff88',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.filter = 'brightness(1.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.filter = '';
                  }}
                >
                  Register Agent
                </button>
              )}
            </div>
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
                    color: card.value === '—' ? 'var(--color-muted-fg)' : '#00ff88',
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
                  {activeAgents === 0 ? 'No agents online.' : `${activeAgents} agent${activeAgents !== 1 ? 's' : ''} registered.`}
                </h2>
                <p
                  className="text-sm leading-relaxed max-w-md"
                  style={{ fontFamily: 'var(--font-body)', color: 'var(--color-muted-fg)' }}
                >
                  {activeAgents === 0
                    ? 'Once agents are registered and the runtime is wired up, this panel will render a live network graph — agent nodes connected by transaction edges, each edge representing a bid, assignment, or settlement. Nothing has been signed yet.'
                    : 'Agents are registered on-chain. Connect your wallet and use the agent registry to interact with the economy.'}
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
                  className={`w-1.5 h-1.5 rounded-full block ${activeAgents > 0 ? 'pulse-dot' : ''}`}
                  style={{ background: activeAgents > 0 ? '#00ff88' : 'var(--color-border)', boxShadow: activeAgents > 0 ? '0 0 6px rgba(0,255,136,1)' : 'none' }}
                />
                <span
                  className="text-[11px] tracking-wider uppercase"
                  style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
                >
                  {activeAgents === 0 ? 'Waiting for first agent registration' : `${activeAgents} Active`}
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

      {/* ── Registration Modal ──────────────────────────────────────── */}
      {showRegisterModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)' }}
          onClick={() => setShowRegisterModal(false)}
        >
          <div
            className="cyber-chamfer relative max-w-md w-full p-6 space-y-5"
            style={{
              background: 'var(--color-card)',
              border: '1px solid rgba(0,255,136,0.4)',
              boxShadow: '0 0 24px rgba(0,255,136,0.15)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Corner accents */}
            <div
              className="absolute top-0 left-0 w-6 h-6 pointer-events-none"
              style={{ borderTop: '2px solid rgba(0,255,136,0.6)', borderLeft: '2px solid rgba(0,255,136,0.6)' }}
            />
            <div
              className="absolute bottom-0 right-0 w-6 h-6 pointer-events-none"
              style={{ borderBottom: '2px solid rgba(0,255,136,0.6)', borderRight: '2px solid rgba(0,255,136,0.6)' }}
            />

            <div className="space-y-2">
              <h2
                className="text-xl uppercase tracking-wider"
                style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--color-foreground)' }}
              >
                Register Agent
              </h2>
              <p
                className="text-sm leading-relaxed"
                style={{ fontFamily: 'var(--font-body)', color: 'var(--color-muted-fg)' }}
              >
                Register your wallet as an agent in the Credence economy.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label
                  className="block text-xs uppercase tracking-wider mb-2"
                  style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
                >
                  Agent Name
                </label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="e.g., WorkerAgent-01"
                  className="w-full px-3 py-2 text-sm"
                  style={{
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--color-foreground)',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    outline: 'none',
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(0,255,136,0.5)';
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }}
                />
              </div>

              <div>
                <label
                  className="block text-xs uppercase tracking-wider mb-2"
                  style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
                >
                  Capabilities (comma-separated)
                </label>
                <input
                  type="text"
                  value={capabilities}
                  onChange={(e) => setCapabilities(e.target.value)}
                  placeholder="e.g., data-analysis, code-review"
                  className="w-full px-3 py-2 text-sm"
                  style={{
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--color-foreground)',
                    background: 'var(--color-background)',
                    border: '1px solid var(--color-border)',
                    outline: 'none',
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(0,255,136,0.5)';
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }}
                />
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={handleRegister}
                disabled={isRegistering || isRegisterConfirming}
                className="cyber-chamfer-sm flex-1 px-4 py-2.5 text-xs uppercase tracking-widest transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  fontFamily: 'var(--font-label)',
                  color: '#0a0a0f',
                  background: '#00ff88',
                  border: '1px solid #00ff88',
                }}
                onMouseEnter={(e) => {
                  if (!isRegistering && !isRegisterConfirming) {
                    e.currentTarget.style.filter = 'brightness(1.15)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.filter = '';
                }}
              >
                {isRegistering || isRegisterConfirming ? 'Registering...' : 'Register'}
              </button>
              <button
                onClick={() => setShowRegisterModal(false)}
                disabled={isRegistering || isRegisterConfirming}
                className="cyber-chamfer-sm px-4 py-2.5 text-xs uppercase tracking-widest transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  fontFamily: 'var(--font-label)',
                  color: 'var(--color-muted-fg)',
                  background: 'transparent',
                  border: '1px solid var(--color-border)',
                }}
                onMouseEnter={(e) => {
                  if (!isRegistering && !isRegisterConfirming) {
                    e.currentTarget.style.borderColor = '#ff5f57';
                    e.currentTarget.style.color = '#ff5f57';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                  e.currentTarget.style.color = 'var(--color-muted-fg)';
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
