'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { HistoricalData } from '@/lib/types';
import { formatCurrency } from '../shared/formatters';

interface NetSurplusChartProps {
  data: HistoricalData;
}

export default function NetSurplusChart({ data }: NetSurplusChartProps) {
  const chartData = data.years.map((year, i) => ({
    year,
    surplus: data.netSurplus[i],
  }));

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Net Surplus / Deficit</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e3a" />
          <XAxis dataKey="year" stroke="#8888aa" fontSize={12} />
          <YAxis stroke="#8888aa" fontSize={12} tickFormatter={(v: number) => `£${(v / 1000).toFixed(1)}k`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#141428', border: '1px solid #2a2a4a', borderRadius: '8px' }}
            labelStyle={{ color: '#e8e8f0' }}
            formatter={(value) => [formatCurrency(Number(value)), 'Net Surplus']}
          />
          <Bar dataKey="surplus" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={index} fill={entry.surplus >= 0 ? '#00d4aa' : '#ff6b6b'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
