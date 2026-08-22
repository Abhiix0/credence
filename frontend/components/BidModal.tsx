import React from 'react';
import { Task, Bid } from '../lib/types';
import { X, CheckCircle, Clock, DollarSign } from 'lucide-react';

interface BidModalProps {
  task: Task | null;
  bids?: Bid[];
  onClose: () => void;
}

export const BidModal: React.FC<BidModalProps> = ({ task, bids = [], onClose }) => {
  if (!task) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl border border-zinc-200 shadow-xl max-w-lg w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-600 p-1"
        >
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-lg font-bold text-zinc-900 font-mono">
          Task #{task.id} Overview
        </h3>
        <p className="text-xs text-zinc-500 mt-0.5">
          Capability: <span className="font-mono text-zinc-800">{task.requiredCapability}</span>
        </p>

        <div className="mt-4 p-3 bg-zinc-50 border border-zinc-200 rounded-xl space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-zinc-500">Reward:</span>
            <span className="font-mono font-bold text-zinc-900">{task.rewardFormatted}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-500">Status:</span>
            <span className="font-medium text-zinc-800">{task.status}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-500">Spec URI:</span>
            <span className="font-mono text-zinc-600 truncate max-w-[240px]">
              {task.specificationUri}
            </span>
          </div>
        </div>

        <div className="mt-6">
          <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-500 mb-3">
            Submitted Agent Bids ({bids.length})
          </h4>

          {bids.length === 0 ? (
            <div className="p-4 border border-dashed border-zinc-200 rounded-xl text-center text-xs text-zinc-400">
              No bids submitted yet for this task.
            </div>
          ) : (
            <div className="space-y-2">
              {bids.map((bid) => (
                <div
                  key={bid.id}
                  className="p-3 rounded-lg border border-zinc-200 flex items-center justify-between text-xs"
                >
                  <div>
                    <div className="font-mono font-medium text-zinc-900">{bid.bidder}</div>
                    <div className="text-zinc-400 text-[11px]">
                      Est. Duration: {bid.estimatedDurationSec}s
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-bold text-zinc-900">
                      {bid.proposedPriceFormatted}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
