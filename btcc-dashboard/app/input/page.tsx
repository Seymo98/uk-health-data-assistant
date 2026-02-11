'use client';

import { useEffect, useState, useCallback } from 'react';
import { BudgetData, ActualsData } from '@/lib/types';
import DataGrid from '@/components/Input/DataGrid';
import PasteImport from '@/components/Input/PasteImport';
import MonthSelector from '@/components/Input/MonthSelector';

export default function InputPage() {
  const [budget, setBudget] = useState<BudgetData | null>(null);
  const [actuals, setActuals] = useState<ActualsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);
  const [view, setView] = useState<'grid' | 'month'>('grid');
  const [type, setType] = useState<'revenue' | 'costs'>('revenue');

  useEffect(() => {
    Promise.all([
      fetch('/api/budget').then(r => r.json()),
      fetch('/api/actuals').then(r => r.json()),
    ]).then(([b, a]) => {
      setBudget(b);
      setActuals(a);
      setLoading(false);
    });
  }, []);

  const handleUpdate = useCallback((updated: ActualsData) => {
    setActuals(updated);
  }, []);

  const handleSave = async () => {
    if (!actuals) return;
    setSaving(true);
    setSaveStatus(null);
    try {
      const res = await fetch('/api/actuals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(actuals),
      });
      const result = await res.json();
      if (result.success) {
        setActuals({ ...actuals, lastUpdated: result.lastUpdated });
        setSaveStatus('Saved successfully');
      } else {
        setSaveStatus('Save failed');
      }
    } catch {
      setSaveStatus('Save failed — check console');
    }
    setSaving(false);
  };

  if (loading || !budget || !actuals) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-[#8888aa]">Loading...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#e8e8f0]">Data Entry</h1>
          <p className="text-[#8888aa] text-sm">
            Enter actual figures for the {budget.financialYear} season
            {actuals.lastUpdated && ` — Last saved ${new Date(actuals.lastUpdated).toLocaleDateString('en-GB')}`}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2 bg-[#00d4aa] text-[#0d0d1a] rounded-lg text-sm font-semibold disabled:opacity-50 hover:bg-[#00d4aa]/80 transition-colors"
          >
            {saving ? 'Saving...' : 'Save All'}
          </button>
          {saveStatus && (
            <span className={`self-center text-xs ${saveStatus.includes('success') ? 'text-[#00d4aa]' : 'text-[#ff6b6b]'}`}>
              {saveStatus}
            </span>
          )}
        </div>
      </div>

      {/* View toggle */}
      <div className="flex gap-2 flex-wrap">
        <div className="flex gap-1 bg-[#1e1e3a] rounded-lg p-1">
          <button
            onClick={() => setView('grid')}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              view === 'grid' ? 'bg-[#141428] text-[#e8e8f0]' : 'text-[#8888aa]'
            }`}
          >
            Full Grid
          </button>
          <button
            onClick={() => setView('month')}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              view === 'month' ? 'bg-[#141428] text-[#e8e8f0]' : 'text-[#8888aa]'
            }`}
          >
            Month View
          </button>
        </div>

        <div className="flex gap-1 bg-[#1e1e3a] rounded-lg p-1">
          <button
            onClick={() => setType('revenue')}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              type === 'revenue' ? 'bg-[#00d4aa]/20 text-[#00d4aa]' : 'text-[#8888aa]'
            }`}
          >
            Revenue
          </button>
          <button
            onClick={() => setType('costs')}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              type === 'costs' ? 'bg-[#ff6b6b]/20 text-[#ff6b6b]' : 'text-[#8888aa]'
            }`}
          >
            Costs
          </button>
        </div>
      </div>

      {view === 'grid' ? (
        <DataGrid budget={budget} actuals={actuals} type={type} onUpdate={handleUpdate} />
      ) : (
        <MonthSelector budget={budget} actuals={actuals} type={type} onUpdate={handleUpdate} />
      )}

      <PasteImport budget={budget} actuals={actuals} onUpdate={handleUpdate} />
    </div>
  );
}
