'use client';

import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { HistoricalData } from '@/lib/types';
import { formatCurrency } from '../shared/formatters';

interface BarProfitChartProps {
  data: HistoricalData;
}

export default function BarProfitChart({ data }: BarProfitChartProps) {
  const chartData = data.years.map((year, i) => ({
    year,
    barSales: data.barSales[i],
    barProfit: data.barSales[i] - data.barStock[i],
    barMargin: data.barMargin[i] * 100,
  }));

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Bar Profit &amp; Margin</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e3a" />
          <XAxis dataKey="year" stroke="#8888aa" fontSize={12} />
          <YAxis yAxisId="left" stroke="#8888aa" fontSize={12} tickFormatter={(v: number) => `£${(v / 1000).toFixed(0)}k`} />
          <YAxis yAxisId="right" orientation="right" stroke="#ffd93d" fontSize={12} tickFormatter={(v: number) => `${v}%`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#141428', border: '1px solid #2a2a4a', borderRadius: '8px' }}
            labelStyle={{ color: '#e8e8f0' }}
            formatter={(value, name) => {
              const v = Number(value);
              if (name === 'barMargin') return [`${v.toFixed(1)}%`, 'Margin'];
              return [formatCurrency(v), name === 'barSales' ? 'Bar Sales' : 'Bar Profit'];
            }}
          />
          <Legend wrapperStyle={{ color: '#8888aa' }} />
          <Bar yAxisId="left" dataKey="barSales" fill="#4a7dff" opacity={0.5} name="Bar Sales" radius={[4, 4, 0, 0]} />
          <Bar yAxisId="left" dataKey="barProfit" fill="#00d4aa" name="Bar Profit" radius={[4, 4, 0, 0]} />
          <Line yAxisId="right" type="monotone" dataKey="barMargin" stroke="#ffd93d" strokeWidth={2} dot={{ fill: '#ffd93d', r: 4 }} name="Margin %" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
