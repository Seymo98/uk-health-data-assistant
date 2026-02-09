'use client';

import { useState } from 'react';
import { VarianceAlert } from '@/lib/types';

interface VarianceAlertsProps {
  alerts: VarianceAlert[];
}

export default function VarianceAlerts({ alerts }: VarianceAlertsProps) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const visibleAlerts = alerts.filter(a => !dismissed.has(a.id));

  if (visibleAlerts.length === 0) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-2">Variance Alerts</h3>
      {visibleAlerts.map(alert => (
        <div
          key={alert.id}
          className={`flex items-center justify-between rounded-lg px-4 py-3 text-sm ${
            alert.type === 'critical'
              ? 'bg-[#ff6b6b]/10 border border-[#ff6b6b]/30'
              : 'bg-[#ffd93d]/10 border border-[#ffd93d]/30'
          }`}
        >
          <div className="flex items-center gap-3">
            <span className={`text-lg ${alert.type === 'critical' ? 'text-[#ff6b6b]' : 'text-[#ffd93d]'}`}>
              {alert.type === 'critical' ? '!!' : '!'}
            </span>
            <span className="text-[#e8e8f0]">{alert.message}</span>
          </div>
          <button
            onClick={() => setDismissed(prev => new Set(prev).add(alert.id))}
            className="text-[#8888aa] hover:text-[#e8e8f0] text-xs ml-4 shrink-0"
          >
            Dismiss
          </button>
        </div>
      ))}
    </div>
  );
}
