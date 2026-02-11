'use client';

import { useEffect, useState } from 'react';
import { HistoricalData } from '@/lib/types';
import BarProfitChart from '@/components/History/BarProfitChart';
import RevenueVsCostsChart from '@/components/History/RevenueVsCostsChart';
import NetSurplusChart from '@/components/History/NetSurplusChart';
import BankBalanceHistory from '@/components/History/BankBalanceHistory';

export default function HistoryPage() {
  const [data, setData] = useState<HistoricalData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/budget')
      .then(r => r.json())
      .then(() => {
        return import('@/data/historical.json');
      })
      .then(mod => {
        setData(mod.default as HistoricalData);
        setLoading(false);
      });
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-[#8888aa]">Loading history...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#e8e8f0]">Historical Trends</h1>
        <p className="text-[#8888aa] text-sm">Four-year financial performance ({data.years[0]} to {data.years[data.years.length - 1]})</p>
      </div>

      {/* Year notes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {data.years.map(year => (
          <div key={year} className="bg-[#141428] border border-[#2a2a4a] rounded-lg p-3">
            <p className="text-[#00d4aa] text-xs font-semibold mb-1">{year}</p>
            <p className="text-[#8888aa] text-xs">{data.notes[year]}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarProfitChart data={data} />
        <RevenueVsCostsChart data={data} />
        <NetSurplusChart data={data} />
        <BankBalanceHistory data={data} />
      </div>
    </div>
  );
}
