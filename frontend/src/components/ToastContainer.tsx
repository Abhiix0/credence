import React from 'react';
import { CheckCircle, XCircle, Info, Loader } from 'lucide-react';
import type { Toast } from '../hooks/useToast';

interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed top-20 right-6 z-50 flex flex-col gap-3 pointer-events-none"
      style={{ maxWidth: '420px' }}
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 shrink-0" style={{ color: '#00ff88' }} />;
      case 'error':
        return <XCircle className="w-5 h-5 shrink-0" style={{ color: '#ff5f57' }} />;
      case 'pending':
        return <Loader className="w-5 h-5 shrink-0 animate-spin" style={{ color: '#00d4ff' }} />;
      default:
        return <Info className="w-5 h-5 shrink-0" style={{ color: '#00d4ff' }} />;
    }
  };

  const getBorderColor = () => {
    switch (toast.type) {
      case 'success':
        return 'rgba(0,255,136,0.5)';
      case 'error':
        return 'rgba(255,95,87,0.5)';
      case 'pending':
        return 'rgba(0,212,255,0.5)';
      default:
        return 'rgba(0,212,255,0.3)';
    }
  };

  const getGlow = () => {
    switch (toast.type) {
      case 'success':
        return '0 0 16px rgba(0,255,136,0.15)';
      case 'error':
        return '0 0 16px rgba(255,95,87,0.15)';
      case 'pending':
        return '0 0 16px rgba(0,212,255,0.15)';
      default:
        return '0 0 12px rgba(0,212,255,0.1)';
    }
  };

  return (
    <div
      className="cyber-chamfer-sm flex items-start gap-3 p-4 pointer-events-auto animate-slide-in"
      style={{
        background: 'rgba(10,10,15,0.95)',
        border: `1px solid ${getBorderColor()}`,
        boxShadow: getGlow(),
        backdropFilter: 'blur(12px)',
      }}
    >
      {getIcon()}
      <div className="flex-1 min-w-0">
        <p
          className="text-sm leading-relaxed"
          style={{
            fontFamily: 'var(--font-body)',
            color: 'var(--color-foreground)',
            wordBreak: 'break-word',
          }}
        >
          {toast.message}
        </p>
      </div>
      {toast.type !== 'pending' && (
        <button
          onClick={() => onRemove(toast.id)}
          className="shrink-0 text-xs opacity-60 hover:opacity-100 transition-opacity"
          style={{ color: 'var(--color-muted-fg)' }}
          aria-label="Close notification"
        >
          ✕
        </button>
      )}
    </div>
  );
}
