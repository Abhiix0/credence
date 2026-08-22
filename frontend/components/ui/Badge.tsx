import React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: 'accent' | 'secondary' | 'tertiary' | 'destructive' | 'neutral';
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  tone = 'neutral',
  className,
  children,
  ...props
}) => {
  const baseStyles = 'cyber-chamfer-sm inline-flex items-center justify-center px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider font-semibold';
  
  const toneStyles = {
    accent: 'bg-accent/10 border border-accent/30 text-accent',
    secondary: 'bg-accentSecondary/10 border border-accentSecondary/30 text-accentSecondary',
    tertiary: 'bg-accentTertiary/10 border border-accentTertiary/30 text-accentTertiary',
    destructive: 'bg-destructive/10 border border-destructive/30 text-destructive',
    neutral: 'bg-muted border border-border text-mutedForeground',
  };

  return (
    <span
      className={cn(baseStyles, toneStyles[tone], className)}
      {...props}
    >
      {children}
    </span>
  );
};
