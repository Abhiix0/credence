import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface NavbarProps {
  economy?: boolean;
}

export default function Navbar({ economy = false }: NavbarProps) {
  const location = useLocation();

  return (
    <header
      className="fixed top-0 left-0 right-0 z-40 flex items-center justify-between px-6 md:px-10 h-14"
      style={{
        background: 'rgba(10, 10, 15, 0.88)',
        backdropFilter: 'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      {/* Bottom neon hairline */}
      <div
        className="absolute bottom-0 left-0 right-0 h-px pointer-events-none"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(0,255,136,0.3) 30%, rgba(0,212,255,0.3) 70%, transparent 100%)',
        }}
        aria-hidden="true"
      />

      {/* Wordmark */}
      <Link
        to="/"
        className="group flex items-center gap-1"
        aria-label="credence home"
      >
        <span
          className="text-sm font-bold tracking-wider glow-accent transition-all duration-150"
          style={{ fontFamily: 'var(--font-label)' }}
        >
          &gt;_
        </span>
        <span
          className="text-sm font-medium tracking-wider transition-colors duration-150"
          style={{
            fontFamily: 'var(--font-label)',
            color: 'var(--color-foreground)',
          }}
        >
          credence
        </span>
      </Link>

      {/* Right side */}
      {economy ? (
        <span
          className="text-xs tracking-[0.25em] uppercase"
          style={{ fontFamily: 'var(--font-label)', color: 'var(--color-muted-fg)' }}
        >
          The Economy
        </span>
      ) : (
        <nav aria-label="Main navigation">
          <Link
            to="/about"
            className="text-sm tracking-wider uppercase transition-all duration-150 relative group"
            style={{
              fontFamily: 'var(--font-label)',
              color: location.pathname === '/about' ? '#00ff88' : 'var(--color-muted-fg)',
              textShadow: location.pathname === '/about'
                ? '0 0 8px rgba(0,255,136,0.5)'
                : 'none',
            }}
          >
            About
            {/* Underline neon bar */}
            <span
              className="absolute -bottom-0.5 left-0 right-0 h-px transition-all duration-150"
              style={{
                background: '#00ff88',
                opacity: location.pathname === '/about' ? 1 : 0,
                boxShadow: '0 0 6px rgba(0,255,136,0.8)',
              }}
            />
          </Link>
        </nav>
      )}
    </header>
  );
}
