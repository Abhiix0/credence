import React from 'react';
import type { Metadata } from 'next';
import './globals.css';

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
    <html lang="en">
      <body className="bg-zinc-50 text-zinc-900 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
