import React from 'react';
import type { Metadata } from 'next';
import { Orbitron, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const orbitron = Orbitron({
  variable: '--font-orbitron',
  subsets: ['latin'],
});

const jetbrainsMono = JetBrains_Mono({
  variable: '--font-jetbrains-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'Autonomous Agent Economy',
  description: 'On-chain economy for autonomous AI agents on Monad testnet',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${orbitron.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-background text-foreground antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
