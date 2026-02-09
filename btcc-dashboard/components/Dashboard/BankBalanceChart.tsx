'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts';
import { formatCurrency } from '../shared/formatters';

interface BankBalanceChartProps {
  data: { month: string; budget: number; actual: number | null }[];
  openingBalance: number;
}

export default function BankBalanceChart({ data, openingBalance }: BankBalanceChartProps) {
  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Projected Bank Balance</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e3a" />
          <XAxis dataKey="month" stroke="#8888aa" fontSize={12} />
          <YAxis stroke="#8888aa" fontSize={12} tickFormatter={(v: number) => `£${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#141428', border: '1px solid #2a2a4a', borderRadius: '8px' }}
            labelStyle={{ color: '#e8e8f0' }}
            formatter={(value) => [value != null ? formatCurrency(Number(value)) : '—', '']}
          />
          <Legend wrapperStyle={{ color: '#8888aa' }} />
          <ReferenceLine y={openingBalance} stroke="#8888aa" strokeDasharray="5 5" label={{ value: `Opening £${(openingBalance / 1000).toFixed(1)}k`, fill: '#8888aa', fontSize: 11 }} />
          <Line type="monotone" dataKey="budget" stroke="#4a7dff" strokeDasharray="8 4" strokeWidth={2} dot={false} name="Budget" />
          <Line type="monotone" dataKey="actual" stroke="#00d4aa" strokeWidth={2} dot={{ fill: '#00d4aa', r: 4 }} connectNulls={false} name="Actual" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
