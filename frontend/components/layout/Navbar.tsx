'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { Cpu, Menu, X } from 'lucide-react';

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/agents', label: 'Agents' },
    { href: '/about', label: 'About' },
  ];

  const isActiveLink = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  return (
    <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left: Logo/Wordmark */}
          <Link href="/" className="flex items-center gap-2 group">
            <Cpu className="w-5 h-5 text-accent group-hover:text-accentSecondary transition-colors" />
            <span className="font-heading text-lg uppercase tracking-wider text-foreground group-hover:text-accent transition-colors">
              Credence
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <div className="flex items-center gap-6">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'font-mono text-xs uppercase tracking-wider transition-all relative',
                    'hover:text-accent',
                    isActiveLink(link.href)
                      ? 'text-accent after:absolute after:bottom-[-4px] after:left-0 after:right-0 after:h-[1px] after:bg-accent after:shadow-neon-sm'
                      : 'text-mutedForeground'
                  )}
                >
                  {link.label}
                </Link>
              ))}
            </div>
            
            <Link href="/agents">
              <Button variant="glitch" className="min-h-[44px]">
                Start Economy →
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 text-foreground hover:text-accent transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-card/95 backdrop-blur-sm">
          <div className="px-4 py-4 space-y-3">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={cn(
                  'block py-3 px-4 font-mono text-sm uppercase tracking-wider transition-all rounded',
                  'min-h-[44px] flex items-center',
                  isActiveLink(link.href)
                    ? 'text-accent bg-accent/10 border-l-2 border-accent'
                    : 'text-mutedForeground hover:text-accent hover:bg-muted'
                )}
              >
                {link.label}
              </Link>
            ))}
            
            <Link href="/agents" onClick={() => setIsMobileMenuOpen(false)} className="block pt-2">
              <Button variant="glitch" className="w-full min-h-[44px]">
                Start Economy →
              </Button>
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};
