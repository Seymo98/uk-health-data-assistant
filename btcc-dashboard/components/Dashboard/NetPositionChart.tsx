'use client';

import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer, Cell } from 'recharts';
import { MonthSummary } from '@/lib/types';
import { formatCurrency } from '../shared/formatters';

interface NetPositionChartProps {
  data: MonthSummary[];
}

export default function NetPositionChart({ data }: NetPositionChartProps) {
  const chartData = data.map(d => ({
    month: d.month,
    budgetNet: d.budgetNet,
    actualNet: d.actualNet,
  }));

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Monthly Net Position</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e3a" />
          <XAxis dataKey="month" stroke="#8888aa" fontSize={12} />
          <YAxis stroke="#8888aa" fontSize={12} tickFormatter={(v: number) => `£${(v / 1000).toFixed(1)}k`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#141428', border: '1px solid #2a2a4a', borderRadius: '8px' }}
            labelStyle={{ color: '#e8e8f0' }}
            formatter={(value) => [value != null ? formatCurrency(Number(value)) : '—', '']}
          />
          <Legend wrapperStyle={{ color: '#8888aa' }} />
          <ReferenceLine y={0} stroke="#8888aa" strokeDasharray="3 3" />
          <Bar dataKey="budgetNet" name="Budget Net" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={index} fill={entry.budgetNet >= 0 ? '#00d4aa' : '#ff6b6b'} opacity={0.4} />
            ))}
          </Bar>
          <Line type="monotone" dataKey="actualNet" stroke="#ffd93d" strokeWidth={2} dot={{ fill: '#ffd93d', r: 4 }} connectNulls={false} name="Actual Net" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
