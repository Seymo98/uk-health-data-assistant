'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { HistoricalData } from '@/lib/types';
import { formatCurrency } from '../shared/formatters';

interface BankBalanceHistoryProps {
  data: HistoricalData;
}

export default function BankBalanceHistory({ data }: BankBalanceHistoryProps) {
  const chartData = data.years.map((year, i) => ({
    year,
    balance: data.bankBalance[i],
  }));

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Year-End Bank Balance</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e3a" />
          <XAxis dataKey="year" stroke="#8888aa" fontSize={12} />
          <YAxis stroke="#8888aa" fontSize={12} tickFormatter={(v: number) => `£${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#141428', border: '1px solid #2a2a4a', borderRadius: '8px' }}
            labelStyle={{ color: '#e8e8f0' }}
            formatter={(value) => [formatCurrency(Number(value)), 'Bank Balance']}
          />
          <defs>
            <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4a7dff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#4a7dff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area type="monotone" dataKey="balance" stroke="#4a7dff" strokeWidth={2} fill="url(#balanceGrad)" dot={{ fill: '#4a7dff', r: 4 }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
