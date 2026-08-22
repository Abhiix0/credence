import React from 'react';
import { cn } from '@/lib/utils';

export interface EconomyHUDPreviewProps {
  className?: string;
}

export const EconomyHUDPreview: React.FC<EconomyHUDPreviewProps> = ({ className }) => {
  return (
    <div className={cn('relative w-full max-w-md', className)}>
      <svg
        viewBox="0 0 400 300"
        className="w-full h-auto"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Connection lines */}
        <line x1="100" y1="75" x2="300" y2="75" stroke="#00d4ff" strokeWidth="2" opacity="0.6" />
        <line x1="100" y1="150" x2="300" y2="150" stroke="#00ff88" strokeWidth="2" opacity="0.6" />
        <line x1="100" y1="225" x2="300" y2="225" stroke="#ff00ff" strokeWidth="2" opacity="0.6" />
        
        {/* Vertical connector */}
        <line x1="300" y1="75" x2="300" y2="225" stroke="#2a2a3a" strokeWidth="2" opacity="0.4" />

        {/* BUYER Node (Cyan/Tertiary) */}
        <g className="buyer-node">
          <rect x="20" y="50" width="80" height="50" fill="#12121a" stroke="#00d4ff" strokeWidth="2" rx="2" />
          <text x="60" y="70" textAnchor="middle" fill="#00d4ff" fontSize="10" fontFamily="monospace" fontWeight="bold">
            BUYER
          </text>
          <text x="60" y="85" textAnchor="middle" fill="#e0e0e0" fontSize="8" fontFamily="monospace">
            5.2 MON
          </text>
        </g>

        {/* WORKER Node (Green/Accent) */}
        <g className="worker-node">
          <rect x="20" y="125" width="80" height="50" fill="#12121a" stroke="#00ff88" strokeWidth="2" rx="2" />
          <text x="60" y="145" textAnchor="middle" fill="#00ff88" fontSize="10" fontFamily="monospace" fontWeight="bold">
            WORKER
          </text>
          <text x="60" y="160" textAnchor="middle" fill="#e0e0e0" fontSize="8" fontFamily="monospace">
            ACTIVE
          </text>
        </g>

        {/* VERIFIER Node (Magenta/Secondary) */}
        <g className="verifier-node">
          <rect x="20" y="200" width="80" height="50" fill="#12121a" stroke="#ff00ff" strokeWidth="2" rx="2" />
          <text x="60" y="220" textAnchor="middle" fill="#ff00ff" fontSize="10" fontFamily="monospace" fontWeight="bold">
            VERIFIER
          </text>
          <text x="60" y="235" textAnchor="middle" fill="#e0e0e0" fontSize="8" fontFamily="monospace">
            READY
          </text>
        </g>

        {/* SETTLEMENT Node (Accent) */}
        <g className="settlement-node">
          <rect x="260" y="125" width="120" height="50" fill="#12121a" stroke="#00ff88" strokeWidth="2" rx="2" />
          <text x="320" y="145" textAnchor="middle" fill="#00ff88" fontSize="10" fontFamily="monospace" fontWeight="bold">
            SETTLEMENT
          </text>
          <text x="320" y="160" textAnchor="middle" fill="#e0e0e0" fontSize="8" fontFamily="monospace">
            ON-CHAIN
          </text>
        </g>

        {/* Animated pulse dot traveling along paths */}
        <circle className="hud-pulse-dot" r="3" fill="#00ff88">
          <animateMotion
            dur="4s"
            repeatCount="indefinite"
            path="M 100,150 L 300,150"
          />
        </circle>
      </svg>
    </div>
  );
};
