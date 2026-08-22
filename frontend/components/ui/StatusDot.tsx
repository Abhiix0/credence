import React from 'react';
import { cn } from '@/lib/utils';

export interface StatusDotProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: 'accent' | 'secondary' | 'tertiary' | 'destructive' | 'neutral';
  pulse?: boolean;
}

export const StatusDot: React.FC<StatusDotProps> = ({
  tone = 'accent',
  pulse = false,
  className,
  ...props
}) => {
  const baseStyles = 'inline-block w-2 h-2 rounded-full';
  
  const toneStyles = {
    accent: 'bg-accent',
    secondary: 'bg-accentSecondary',
    tertiary: 'bg-accentTertiary',
    destructive: 'bg-destructive',
    neutral: 'bg-mutedForeground',
  };

  const pulseStyles = pulse ? 'animate-blink' : '';

  return (
    <span
      className={cn(baseStyles, toneStyles[tone], pulseStyles, className)}
      {...props}
    />
  );
};
