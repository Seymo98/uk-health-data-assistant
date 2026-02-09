'use client';

import MetricCard from '../shared/MetricCard';
import { formatCurrency, formatVariance } from '../shared/formatters';
import { YTDSummary } from '@/lib/types';

interface KPIStripProps {
  ytd: YTDSummary;
}

export default function KPIStrip({ ytd }: KPIStripProps) {
  const revVariance = ytd.ytdVarianceRev;
  const costVariance = ytd.ytdVarianceCost;
  const netVariance = ytd.ytdActualNet - ytd.ytdBudgetNet;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="YTD Revenue"
        value={formatCurrency(ytd.ytdActualRev)}
        subtitle={`Budget: ${formatCurrency(ytd.ytdBudgetRev)}`}
        variance={formatVariance(revVariance)}
        varianceType={revVariance >= 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        title="YTD Costs"
        value={formatCurrency(ytd.ytdActualCost)}
        subtitle={`Budget: ${formatCurrency(ytd.ytdBudgetCost)}`}
        variance={formatVariance(-costVariance)}
        varianceType={costVariance <= 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        title="YTD Net Position"
        value={formatCurrency(ytd.ytdActualNet)}
        subtitle={`Budget: ${formatCurrency(ytd.ytdBudgetNet)}`}
        variance={formatVariance(netVariance)}
        varianceType={netVariance >= 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        title="Months Reported"
        value={`${ytd.monthsReported} / 12`}
        subtitle={ytd.monthsReported === 0 ? 'No actuals entered yet' : `Projected year-end: ${formatCurrency(ytd.projectedYearEnd)}`}
        progress={(ytd.monthsReported / 12) * 100}
      />
    </div>
  );
}
