import React from 'react';
import { useLocation } from 'react-router-dom';

const PAGE_NAMES: Record<string, string> = {
  '/':        'Home',
  '/about':   'About',
  '/economy': 'Economy',
};

interface BrowserChromeProps {
  children: React.ReactNode;
}

export default function BrowserChrome({ children }: BrowserChromeProps) {
  const location = useLocation();
  const pageName = PAGE_NAMES[location.pathname] ?? 'credence';

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: 'var(--color-background)' }}
    >
      {/* ── Browser chrome bar ─────────────────────────────────────────────── */}
      <div
        className="hidden md:flex items-center gap-4 px-4 py-2 shrink-0 select-none relative overflow-hidden"
        style={{
          background: 'var(--color-card)',
          borderBottom: '1px solid var(--color-border)',
        }}
        aria-hidden="true"
      >
        {/* Subtle top neon line */}
        <div
          className="absolute top-0 left-0 right-0 h-px"
          style={{ background: 'linear-gradient(90deg, transparent 0%, #00ff88 40%, #00d4ff 60%, transparent 100%)', opacity: 0.4 }}
        />

        {/* Traffic lights */}
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="w-3 h-3 rounded-full bg-[#ff5f57] block shadow-[0_0_4px_rgba(255,95,87,0.6)]" />
          <span className="w-3 h-3 rounded-full bg-[#febc2e] block shadow-[0_0_4px_rgba(254,188,46,0.6)]" />
          <span className="w-3 h-3 rounded-full bg-[#28c840] block shadow-[0_0_4px_rgba(40,200,64,0.6)]" />
        </div>

        {/* Tab — chamfered */}
        <div
          className="flex items-center gap-2 px-3 py-1 text-xs shrink-0"
          style={{
            background: 'var(--color-background)',
            border: '1px solid var(--color-border)',
            fontFamily: 'var(--font-label)',
            color: 'var(--color-muted-fg)',
            clipPath: 'polygon(0 4px, 4px 0, calc(100% - 4px) 0, 100% 4px, 100% 100%, 0 100%)',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full pulse-dot block"
            style={{ background: '#00ff88' }}
          />
          {pageName}
        </div>

        {/* Address bar */}
        <div className="flex-1 max-w-md mx-auto">
          <div
            className="flex items-center gap-2 px-3 py-1"
            style={{
              background: 'var(--color-background)',
              border: '1px solid var(--color-border)',
              clipPath: 'polygon(0 4px, 4px 0, calc(100% - 4px) 0, 100% 4px, 100% calc(100% - 4px), calc(100% - 4px) 100%, 4px 100%, 0 calc(100% - 4px))',
            }}
          >
            {/* Lock icon */}
            <svg className="w-3 h-3 shrink-0" style={{ color: '#00ff88', opacity: 0.7 }} fill="none" viewBox="0 0 16 16">
              <rect x="3" y="7" width="10" height="7" rx="1" stroke="currentColor" strokeWidth="1.2"/>
              <path d="M5 7V5a3 3 0 0 1 6 0v2" stroke="currentColor" strokeWidth="1.2"/>
            </svg>
            <span
              className="text-xs truncate"
              style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
            >
              credence.dev{location.pathname === '/' ? '' : location.pathname}
            </span>
          </div>
        </div>

        {/* Spacer */}
        <div className="w-[72px] shrink-0" />
      </div>

      {/* Page content */}
      <div className="flex-1 flex flex-col">
        {children}
      </div>
    </div>
  );
}
