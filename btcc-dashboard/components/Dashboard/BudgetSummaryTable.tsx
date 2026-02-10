'use client';

import { BudgetData, ActualsData } from '@/lib/types';
import { getCategoryBreakdown } from '@/lib/calculations';
import { formatCurrency, varianceColor } from '../shared/formatters';

interface BudgetSummaryTableProps {
  budget: BudgetData;
  actuals: ActualsData;
}

export default function BudgetSummaryTable({ budget, actuals }: BudgetSummaryTableProps) {
  const revBreakdown = getCategoryBreakdown(budget, actuals, 'revenue');
  const costBreakdown = getCategoryBreakdown(budget, actuals, 'costs');

  const hasActuals = revBreakdown.some(r => r.ytdActual !== null);

  const totalRevAnnual = revBreakdown.reduce((s, r) => s + r.annual, 0);
  const totalRevYtdBudget = revBreakdown.reduce((s, r) => s + r.ytdBudget, 0);
  const totalRevYtdActual = hasActuals ? revBreakdown.reduce((s, r) => s + (r.ytdActual ?? 0), 0) : null;
  const totalRevVariance = hasActuals ? revBreakdown.reduce((s, r) => s + (r.variance ?? 0), 0) : null;

  const totalCostAnnual = costBreakdown.reduce((s, r) => s + r.annual, 0);
  const totalCostYtdBudget = costBreakdown.reduce((s, r) => s + r.ytdBudget, 0);
  const totalCostYtdActual = hasActuals ? costBreakdown.reduce((s, r) => s + (r.ytdActual ?? 0), 0) : null;
  const totalCostVariance = hasActuals ? costBreakdown.reduce((s, r) => s + (r.variance ?? 0), 0) : null;

  const renderVariance = (variance: number | null, isCost: boolean = false) => {
    if (variance === null) return <span className="text-[#8888aa]">—</span>;
    return (
      <span className={varianceColor(variance, isCost)}>
        {variance >= 0 ? '+' : ''}{formatCurrency(variance)}
      </span>
    );
  };

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5 overflow-x-auto">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Budget Summary</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[#8888aa] text-xs uppercase tracking-wider border-b border-[#2a2a4a]">
            <th className="text-left py-2 pr-4">Category</th>
            <th className="text-right py-2 px-3">Annual Budget</th>
            <th className="text-right py-2 px-3">YTD Budget</th>
            <th className="text-right py-2 px-3">YTD Actual</th>
            <th className="text-right py-2 px-3">Variance</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colSpan={5} className="pt-3 pb-1 text-[#00d4aa] text-xs font-semibold uppercase tracking-wider">Revenue</td>
          </tr>
          {revBreakdown.map(row => (
            <tr key={row.category} className="border-b border-[#1e1e3a] hover:bg-[#1e1e3a]/50">
              <td className="py-2 pr-4 text-[#e8e8f0]">{row.category}</td>
              <td className="py-2 px-3 text-right text-[#8888aa] font-mono">{formatCurrency(row.annual)}</td>
              <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(row.ytdBudget)}</td>
              <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(row.ytdActual)}</td>
              <td className="py-2 px-3 text-right font-mono">{renderVariance(row.variance)}</td>
            </tr>
          ))}
          <tr className="border-b border-[#2a2a4a] font-semibold">
            <td className="py-2 pr-4 text-[#00d4aa]">Total Revenue</td>
            <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(totalRevAnnual)}</td>
            <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(totalRevYtdBudget)}</td>
            <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(totalRevYtdActual)}</td>
            <td className="py-2 px-3 text-right font-mono">{renderVariance(totalRevVariance)}</td>
          </tr>

          <tr>
            <td colSpan={5} className="pt-4 pb-1 text-[#ff6b6b] text-xs font-semibold uppercase tracking-wider">Costs</td>
          </tr>
          {costBreakdown.map(row => (
            <tr key={row.category} className="border-b border-[#1e1e3a] hover:bg-[#1e1e3a]/50">
              <td className="py-2 pr-4 text-[#e8e8f0]">{row.category}</td>
              <td className="py-2 px-3 text-right text-[#8888aa] font-mono">{formatCurrency(row.annual)}</td>
              <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(row.ytdBudget)}</td>
              <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(row.ytdActual)}</td>
              <td className="py-2 px-3 text-right font-mono">{renderVariance(row.variance, true)}</td>
            </tr>
          ))}
          <tr className="font-semibold">
            <td className="py-2 pr-4 text-[#ff6b6b]">Total Costs</td>
            <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(totalCostAnnual)}</td>
            <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(totalCostYtdBudget)}</td>
            <td className="py-2 px-3 text-right text-[#e8e8f0] font-mono">{formatCurrency(totalCostYtdActual)}</td>
            <td className="py-2 px-3 text-right font-mono">{renderVariance(totalCostVariance, true)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
