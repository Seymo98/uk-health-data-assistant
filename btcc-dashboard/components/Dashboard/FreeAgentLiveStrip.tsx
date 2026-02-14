'use client';

import { useState, useEffect } from 'react';
import { formatCurrency } from '../shared/formatters';

interface LiveData {
  bankBalance: {
    accountName: string;
    currentBalance: number;
  } | null;
  outstandingInvoices: {
    count: number;
    totalValue: number;
    overdueCount: number;
    overdueValue: number;
  };
  outstandingBills: {
    count: number;
    totalValue: number;
    overdueCount: number;
    overdueValue: number;
  };
}

export default function FreeAgentLiveStrip() {
  const [data, setData] = useState<LiveData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/freeagent/live')
      .then(r => {
        if (!r.ok) throw new Error('Not connected');
        return r.json();
      })
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  // Don't render anything if not connected to FreeAgent
  if (loading || !data) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {/* Live Bank Balance */}
      {data.bankBalance && (
        <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-5 h-5 rounded bg-[#00875a] flex items-center justify-center text-[10px] text-white font-bold">
              FA
            </div>
            <p className="text-[#8888aa] text-xs uppercase tracking-wider">Bank Balance</p>
          </div>
          <p className="text-[#e8e8f0] text-2xl font-mono font-bold">
            {formatCurrency(data.bankBalance.currentBalance)}
          </p>
          <p className="text-[#8888aa] text-xs mt-1">{data.bankBalance.accountName}</p>
        </div>
      )}

      {/* Outstanding Invoices (money owed TO the club) */}
      <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-5 h-5 rounded bg-[#00875a] flex items-center justify-center text-[10px] text-white font-bold">
            FA
          </div>
          <p className="text-[#8888aa] text-xs uppercase tracking-wider">Invoices Due</p>
        </div>
        <p className="text-[#e8e8f0] text-2xl font-mono font-bold">
          {formatCurrency(data.outstandingInvoices.totalValue)}
        </p>
        <p className="text-[#8888aa] text-xs mt-1">
          {data.outstandingInvoices.count} outstanding
          {data.outstandingInvoices.overdueCount > 0 && (
            <span className="text-[#ff6b6b]">
              {' '}({data.outstandingInvoices.overdueCount} overdue — {formatCurrency(data.outstandingInvoices.overdueValue)})
            </span>
          )}
        </p>
      </div>

      {/* Outstanding Bills (money the club OWES) */}
      <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-5 h-5 rounded bg-[#00875a] flex items-center justify-center text-[10px] text-white font-bold">
            FA
          </div>
          <p className="text-[#8888aa] text-xs uppercase tracking-wider">Bills Due</p>
        </div>
        <p className="text-[#e8e8f0] text-2xl font-mono font-bold">
          {formatCurrency(data.outstandingBills.totalValue)}
        </p>
        <p className="text-[#8888aa] text-xs mt-1">
          {data.outstandingBills.count} outstanding
          {data.outstandingBills.overdueCount > 0 && (
            <span className="text-[#ff6b6b]">
              {' '}({data.outstandingBills.overdueCount} overdue — {formatCurrency(data.outstandingBills.overdueValue)})
            </span>
          )}
        </p>
      </div>
    </div>
  );
}
