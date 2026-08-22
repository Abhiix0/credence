import React from 'react';
import { Hero } from '@/components/home/Hero';
import { HowItWorks } from '@/components/home/HowItWorks';

export default function Home() {
  return (
    <main className="flex-1">
      <Hero />
      <HowItWorks />
    </main>
  );
}
