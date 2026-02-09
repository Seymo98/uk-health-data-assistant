'use client';

import { useState } from 'react';
import { MONTHS } from '@/lib/calculations';
import { BudgetData, ActualsData } from '@/lib/types';
import { formatCurrency } from '../shared/formatters';

interface MonthSelectorProps {
  budget: BudgetData;
  actuals: ActualsData;
  type: 'revenue' | 'costs';
  onUpdate: (actuals: ActualsData) => void;
}

export default function MonthSelector({ budget, actuals, type, onUpdate }: MonthSelectorProps) {
  const [selectedMonth, setSelectedMonth] = useState(0);
  const categories = Object.keys(budget[type]);

  const handleValueChange = (category: string, value: string) => {
    const updated = { ...actuals };
    updated[type] = { ...updated[type] };
    updated[type][category] = [...updated[type][category]];
    updated[type][category][selectedMonth] = value === '' ? null : Number(value);
    onUpdate(updated);
  };

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Quick Month Entry — {type === 'revenue' ? 'Revenue' : 'Costs'}</h3>
      <div className="flex gap-2 mb-4 flex-wrap">
        {MONTHS.map((m, i) => (
          <button
            key={m}
            onClick={() => setSelectedMonth(i)}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              selectedMonth === i
                ? 'bg-[#00d4aa]/20 text-[#00d4aa] border border-[#00d4aa]/40'
                : 'bg-[#1e1e3a] text-[#8888aa] hover:text-[#e8e8f0] border border-transparent'
            }`}
          >
            {m}
          </button>
        ))}
      </div>
      <div className="space-y-2">
        {categories.map(cat => {
          const budgetVal = budget[type][cat]?.[selectedMonth] ?? 0;
          const actualVal = actuals[type][cat]?.[selectedMonth];
          return (
            <div key={cat} className="flex items-center gap-3">
              <label className="text-[#e8e8f0] text-sm w-40 shrink-0">{cat}</label>
              <input
                type="number"
                value={actualVal ?? ''}
                onChange={e => handleValueChange(cat, e.target.value)}
                placeholder={budgetVal.toString()}
                className="flex-1 bg-[#0d0d1a] border border-[#2a2a4a] rounded px-3 py-1.5 text-[#e8e8f0] font-mono text-sm placeholder:text-[#8888aa]/50 focus:border-[#00d4aa] focus:outline-none"
              />
              <span className="text-[#8888aa] text-xs font-mono w-16 text-right">
                {formatCurrency(budgetVal)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
