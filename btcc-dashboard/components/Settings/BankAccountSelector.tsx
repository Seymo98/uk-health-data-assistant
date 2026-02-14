'use client';

import { useState, useEffect } from 'react';

interface BankAccount {
  url: string;
  name: string;
  current_balance: string;
  type: string;
}

export default function BankAccountSelector() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch('/api/freeagent/bank-accounts')
      .then(r => r.ok ? r.json() : { accounts: [], selected: '' })
      .then(data => {
        setAccounts(data.accounts || []);
        setSelected(data.selected || '');
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await fetch('/api/freeagent/bank-accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bankAccountUrl: selected }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      // ignore
    }
    setSaving(false);
  };

  if (loading || accounts.length === 0) return null;

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-6 space-y-4">
      <div>
        <h3 className="text-[#e8e8f0] font-semibold">Bank Account</h3>
        <p className="text-[#8888aa] text-xs mt-1">
          Select which FreeAgent bank account to display on the dashboard
        </p>
      </div>
      <div className="flex gap-3 items-end flex-wrap">
        <select
          value={selected}
          onChange={e => setSelected(e.target.value)}
          className="bg-[#0d0d1a] border border-[#2a2a4a] rounded-lg px-3 py-2 text-[#e8e8f0] text-sm flex-1 min-w-[200px]"
        >
          <option value="">Auto-detect (first account)</option>
          {accounts.map(a => (
            <option key={a.url} value={a.url}>
              {a.name} ({a.type}) — £{parseFloat(a.current_balance).toLocaleString()}
            </option>
          ))}
        </select>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 bg-[#4a7dff] text-white rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-[#4a7dff]/80 transition-colors"
        >
          {saving ? 'Saving...' : 'Save'}
        </button>
        {saved && (
          <span className="text-[#00d4aa] text-xs">Saved</span>
        )}
      </div>
    </div>
  );
}
