'use client';

import { useEffect, useState } from 'react';
import { BudgetData, ActualsData } from '@/lib/types';
import { getMonthSummaries, getYTDSummary, getBankBalanceProjection, generateVarianceAlerts } from '@/lib/calculations';
import KPIStrip from '@/components/Dashboard/KPIStrip';
import RevenueChart from '@/components/Dashboard/RevenueChart';
import BankBalanceChart from '@/components/Dashboard/BankBalanceChart';
import NetPositionChart from '@/components/Dashboard/NetPositionChart';
import BudgetSummaryTable from '@/components/Dashboard/BudgetSummaryTable';
import VarianceAlerts from '@/components/Dashboard/VarianceAlerts';
import FreeAgentLiveStrip from '@/components/Dashboard/FreeAgentLiveStrip';

export default function DashboardPage() {
  const [budget, setBudget] = useState<BudgetData | null>(null);
  const [actuals, setActuals] = useState<ActualsData | null>(null);
  const [loading, setLoading] = useState(true);

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

  if (loading || !budget || !actuals) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-[#8888aa]">Loading dashboard...</p>
      </div>
    );
  }

  const summaries = getMonthSummaries(budget, actuals);
  const ytd = getYTDSummary(budget, actuals);
  const bankBalance = getBankBalanceProjection(budget, actuals);
  const alerts = generateVarianceAlerts(budget, actuals);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#e8e8f0]">Dashboard</h1>
          <p className="text-[#8888aa] text-sm">
            {budget.financialYear} Season
            {actuals.lastUpdated && ` — Last updated ${new Date(actuals.lastUpdated).toLocaleDateString('en-GB')}`}
          </p>
        </div>
      </div>

      <KPIStrip ytd={ytd} />

      <FreeAgentLiveStrip />

      {alerts.length > 0 && <VarianceAlerts alerts={alerts} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart data={summaries} />
        <BankBalanceChart data={bankBalance} openingBalance={budget.openingBalance} />
      </div>

      <NetPositionChart data={summaries} />

      <BudgetSummaryTable budget={budget} actuals={actuals} />
    </div>
  );
}
