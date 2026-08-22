import React from 'react';
import { Task } from '../lib/types';
import { Clock, Shield, Coins, ArrowUpRight } from 'lucide-react';

interface TaskBoardProps {
  tasks: Task[];
  onSelectTask?: (task: Task) => void;
}

const STATUS_BADGE: Record<string, string> = {
  Open: 'bg-blue-50 text-blue-700 border-blue-200',
  Assigned: 'bg-amber-50 text-amber-700 border-amber-200',
  Submitted: 'bg-purple-50 text-purple-700 border-purple-200',
  VerifiedPass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  VerifiedFail: 'bg-rose-50 text-rose-700 border-rose-200',
  Cancelled: 'bg-zinc-100 text-zinc-600 border-zinc-200',
};

export const TaskBoard: React.FC<TaskBoardProps> = ({ tasks, onSelectTask }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
          Discovered Tasks ({tasks.length})
        </h2>
      </div>

      {tasks.length === 0 ? (
        <div className="rounded-xl border border-zinc-200 p-8 text-center bg-white">
          <p className="text-sm text-zinc-500">
            No active tasks found on Monad TaskMarket contract.
          </p>
          <p className="text-xs text-zinc-400 mt-1 font-mono">
            Deploy contracts and post tasks to see autonomous bidding in action.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tasks.map((task) => (
            <div
              key={task.id}
              onClick={() => onSelectTask?.(task)}
              className="rounded-xl border border-zinc-200 bg-white p-5 hover:border-zinc-300 hover:shadow-xs transition cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                      STATUS_BADGE[task.status] || STATUS_BADGE.Open
                    }`}
                  >
                    {task.status}
                  </span>
                  <h3 className="text-base font-semibold text-zinc-900 mt-2 font-mono">
                    Task #{task.id}
                  </h3>
                </div>
                <div className="text-right">
                  <div className="text-sm font-bold text-zinc-900 font-mono">
                    {task.rewardFormatted}
                  </div>
                  <div className="text-xs text-zinc-400">Escrow Reward</div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-zinc-100 grid grid-cols-2 gap-2 text-xs text-zinc-600">
                <div className="flex items-center space-x-1.5">
                  <Shield className="w-3.5 h-3.5 text-zinc-400" />
                  <span className="font-mono">{task.requiredCapability}</span>
                </div>
                <div className="flex items-center space-x-1.5 justify-end">
                  <Clock className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Expires: {new Date(task.deadline * 1000).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
