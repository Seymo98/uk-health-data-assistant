'use client';

import { DEFAULT_CATEGORY_MAPPINGS, CategoryMapping } from '@/lib/freeagent-mapping';

export default function CategoryMappingEditor() {
  const revenueMappings = DEFAULT_CATEGORY_MAPPINGS.filter(m => m.type === 'revenue');
  const costMappings = DEFAULT_CATEGORY_MAPPINGS.filter(m => m.type === 'costs');

  const renderTable = (mappings: CategoryMapping[], label: string) => (
    <div>
      <h4 className="text-xs uppercase tracking-wider text-[#8888aa] mb-2">{label}</h4>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[#8888aa] text-xs border-b border-[#2a2a4a]">
            <th className="text-left py-1.5">FreeAgent Pattern</th>
            <th className="text-left py-1.5">Dashboard Category</th>
          </tr>
        </thead>
        <tbody>
          {mappings.map((m, i) => (
            <tr key={i} className="border-b border-[#1e1e3a]">
              <td className="py-1.5 font-mono text-xs text-[#e8e8f0]">{m.freeagentPattern}</td>
              <td className="py-1.5 text-[#8888aa]">{m.dashboardCategory}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-6 space-y-5">
      <div>
        <h3 className="text-[#e8e8f0] font-semibold">Category Mappings</h3>
        <p className="text-[#8888aa] text-xs mt-1">
          How FreeAgent P&amp;L categories map to your dashboard. The sync uses case-insensitive substring matching.
          Unmapped income goes to &quot;Other Revenue&quot; and unmapped expenses go to &quot;Other Costs&quot;.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderTable(revenueMappings, 'Revenue')}
        {renderTable(costMappings, 'Costs')}
      </div>

      <p className="text-[#8888aa] text-xs">
        To customise mappings, edit <code className="text-[#e8e8f0] bg-[#0d0d1a] px-1.5 py-0.5 rounded font-mono text-xs">lib/freeagent-mapping.ts</code>
      </p>
    </div>
  );
}
