'use client';

import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { HistoricalData } from '@/lib/types';
import { formatCurrency } from '../shared/formatters';

interface RevenueVsCostsChartProps {
  data: HistoricalData;
}

export default function RevenueVsCostsChart({ data }: RevenueVsCostsChartProps) {
  const chartData = data.years.map((year, i) => ({
    year,
    opex: data.totalCost[i] - data.improvements[i],
    investment: data.improvements[i],
    revenue: data.totalRev[i],
  }));

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Revenue vs Costs vs Investment</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e3a" />
          <XAxis dataKey="year" stroke="#8888aa" fontSize={12} />
          <YAxis stroke="#8888aa" fontSize={12} tickFormatter={(v: number) => `£${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#141428', border: '1px solid #2a2a4a', borderRadius: '8px' }}
            labelStyle={{ color: '#e8e8f0' }}
            formatter={(value, name) => [formatCurrency(Number(value)), String(name).charAt(0).toUpperCase() + String(name).slice(1)]}
          />
          <Legend wrapperStyle={{ color: '#8888aa' }} />
          <Bar dataKey="opex" stackId="costs" fill="#ff6b6b" opacity={0.7} name="Operating Costs" />
          <Bar dataKey="investment" stackId="costs" fill="#ffd93d" opacity={0.7} name="Investment" radius={[4, 4, 0, 0]} />
          <Line type="monotone" dataKey="revenue" stroke="#00d4aa" strokeWidth={2} dot={{ fill: '#00d4aa', r: 4 }} name="Revenue" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
