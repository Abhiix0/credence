import React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'glitch';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'default',
  className,
  children,
  ...props
}) => {
  const baseStyles = 'cyber-chamfer-sm inline-flex items-center justify-center gap-2 px-6 py-3 font-mono text-xs uppercase tracking-wider font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantStyles = {
    default: 'bg-card border border-border text-foreground hover:border-accent hover:text-accent',
    secondary: 'bg-muted border border-border text-foreground hover:bg-card hover:border-accentSecondary hover:text-accentSecondary',
    outline: 'bg-transparent border border-accent text-accent hover:bg-accent hover:text-background',
    ghost: 'bg-transparent border-none text-mutedForeground hover:text-accent hover:bg-card/50',
    glitch: 'bg-accent border border-accent text-background cyber-glitch hover:bg-accentSecondary hover:border-accentSecondary',
  };

  return (
    <button
      className={cn(baseStyles, variantStyles[variant], className)}
      {...props}
    >
      {children}
    </button>
  );
};
