'use client';

import { MONTHS } from '@/lib/calculations';
import { BudgetData, ActualsData } from '@/lib/types';
import { formatCurrency } from '../shared/formatters';

interface DataGridProps {
  budget: BudgetData;
  actuals: ActualsData;
  type: 'revenue' | 'costs';
  onUpdate: (actuals: ActualsData) => void;
}

export default function DataGrid({ budget, actuals, type, onUpdate }: DataGridProps) {
  const categories = Object.keys(budget[type]);

  const handleCellChange = (category: string, monthIndex: number, value: string) => {
    const updated = { ...actuals };
    updated[type] = { ...updated[type] };
    updated[type][category] = [...updated[type][category]];
    updated[type][category][monthIndex] = value === '' ? null : Number(value);
    onUpdate(updated);
  };

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5 overflow-x-auto">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">
        {type === 'revenue' ? 'Revenue' : 'Costs'} — Editable Grid
      </h3>
      <table className="w-full text-xs">
        <thead>
          <tr className="text-[#8888aa] uppercase tracking-wider border-b border-[#2a2a4a]">
            <th className="text-left py-2 pr-2 sticky left-0 bg-[#141428] min-w-[140px]">Category</th>
            {MONTHS.map(m => (
              <th key={m} className="text-center py-2 px-1 min-w-[72px]">{m}</th>
            ))}
            <th className="text-right py-2 pl-2">Total</th>
          </tr>
        </thead>
        <tbody>
          {categories.map(cat => {
            const rowTotal = (actuals[type][cat] ?? []).reduce((sum: number, v) => sum + (v ?? 0), 0);
            const hasAnyValue = actuals[type][cat]?.some(v => v !== null);
            return (
              <tr key={cat} className="border-b border-[#1e1e3a]">
                <td className="py-1.5 pr-2 text-[#e8e8f0] sticky left-0 bg-[#141428] text-xs">{cat}</td>
                {MONTHS.map((_, mi) => {
                  const budgetVal = budget[type][cat]?.[mi] ?? 0;
                  const actualVal = actuals[type][cat]?.[mi];
                  const isOverBudget = type === 'costs' && actualVal !== null && budgetVal > 0 && actualVal > budgetVal * 1.2;
                  return (
                    <td key={mi} className="py-1 px-0.5">
                      <input
                        type="number"
                        value={actualVal ?? ''}
                        onChange={e => handleCellChange(cat, mi, e.target.value)}
                        placeholder={budgetVal.toString()}
                        className={`w-full bg-[#0d0d1a] border rounded px-1.5 py-1 text-right font-mono text-xs focus:border-[#00d4aa] focus:outline-none placeholder:text-[#8888aa]/40 ${
                          isOverBudget
                            ? 'border-[#ff6b6b]/50 text-[#ff6b6b]'
                            : 'border-[#2a2a4a] text-[#e8e8f0]'
                        }`}
                      />
                    </td>
                  );
                })}
                <td className="py-1.5 pl-2 text-right font-mono text-[#e8e8f0]">
                  {hasAnyValue ? formatCurrency(rowTotal) : '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
