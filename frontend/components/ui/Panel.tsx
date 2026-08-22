import React from 'react';
import { cn } from '@/lib/utils';

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'terminal';
  children: React.ReactNode;
}

export const Panel: React.FC<PanelProps> = ({
  variant = 'default',
  className,
  children,
  ...props
}) => {
  const baseStyles = 'cyber-chamfer bg-card border border-border';
  
  if (variant === 'terminal') {
    return (
      <div className={cn(baseStyles, 'relative', className)} {...props}>
        {/* Terminal chrome header */}
        <div className="absolute top-0 left-0 right-0 h-8 bg-muted border-b border-border flex items-center px-4 gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-destructive" />
          <div className="w-2.5 h-2.5 rounded-full bg-accentTertiary" />
          <div className="w-2.5 h-2.5 rounded-full bg-accent" />
        </div>
        {/* Content area with padding to clear header */}
        <div className="pt-12 p-6">
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className={cn(baseStyles, 'p-6', className)} {...props}>
      {children}
    </div>
  );
};
