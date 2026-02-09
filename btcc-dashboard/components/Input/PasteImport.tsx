'use client';

import { useState } from 'react';
import { BudgetData, ActualsData } from '@/lib/types';

interface PasteImportProps {
  budget: BudgetData;
  actuals: ActualsData;
  onUpdate: (actuals: ActualsData) => void;
}

export default function PasteImport({ budget, actuals, onUpdate }: PasteImportProps) {
  const [type, setType] = useState<'revenue' | 'costs'>('revenue');
  const [pasteText, setPasteText] = useState('');
  const [status, setStatus] = useState<string | null>(null);

  const categories = Object.keys(budget[type]);

  const handleApply = () => {
    try {
      const lines = pasteText.trim().split('\n').filter(l => l.trim());
      if (lines.length !== categories.length) {
        setStatus(`Expected ${categories.length} rows, got ${lines.length}. Categories: ${categories.join(', ')}`);
        return;
      }

      const updated = { ...actuals };
      updated[type] = { ...updated[type] };

      lines.forEach((line, i) => {
        const values = line.split(/[\t,]/).map(v => {
          const trimmed = v.trim().replace(/[£$,]/g, '');
          if (trimmed === '' || trimmed === '-') return null;
          const num = Number(trimmed);
          return isNaN(num) ? null : num;
        });

        while (values.length < 12) values.push(null);
        updated[type][categories[i]] = values.slice(0, 12);
      });

      onUpdate(updated);
      setStatus(`Imported ${lines.length} categories successfully`);
      setPasteText('');
    } catch {
      setStatus('Failed to parse pasted data. Check format and try again.');
    }
  };

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <h3 className="text-[#e8e8f0] text-sm font-semibold mb-4">Paste from Excel</h3>
      <div className="flex gap-3 mb-3">
        <button
          onClick={() => setType('revenue')}
          className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
            type === 'revenue'
              ? 'bg-[#00d4aa]/20 text-[#00d4aa]'
              : 'bg-[#1e1e3a] text-[#8888aa]'
          }`}
        >
          Revenue
        </button>
        <button
          onClick={() => setType('costs')}
          className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
            type === 'costs'
              ? 'bg-[#ff6b6b]/20 text-[#ff6b6b]'
              : 'bg-[#1e1e3a] text-[#8888aa]'
          }`}
        >
          Costs
        </button>
      </div>

      <div className="mb-3">
        <p className="text-[#8888aa] text-xs mb-2">
          Expected row order ({categories.length} rows, 12 columns Oct–Sep):
        </p>
        <div className="text-[#8888aa] text-xs font-mono bg-[#0d0d1a] rounded p-2 max-h-24 overflow-y-auto">
          {categories.map((cat, i) => (
            <div key={cat}>{i + 1}. {cat}</div>
          ))}
        </div>
      </div>

      <textarea
        value={pasteText}
        onChange={e => setPasteText(e.target.value)}
        placeholder="Paste tab-separated or CSV data here..."
        className="w-full h-32 bg-[#0d0d1a] border border-[#2a2a4a] rounded-lg px-3 py-2 text-[#e8e8f0] font-mono text-sm placeholder:text-[#8888aa]/50 focus:border-[#00d4aa] focus:outline-none resize-none"
      />

      <div className="flex items-center gap-3 mt-3">
        <button
          onClick={handleApply}
          disabled={!pasteText.trim()}
          className="px-4 py-2 bg-[#00d4aa] text-[#0d0d1a] rounded-lg text-sm font-semibold disabled:opacity-30 hover:bg-[#00d4aa]/80 transition-colors"
        >
          Apply Import
        </button>
        {status && (
          <p className={`text-xs ${status.includes('success') ? 'text-[#00d4aa]' : 'text-[#ffd93d]'}`}>
            {status}
          </p>
        )}
      </div>
    </div>
  );
}
