'use client';

import MetricCard from '../shared/MetricCard';
import { formatCurrency, formatVariance } from '../shared/formatters';
import { YTDSummary } from '@/lib/types';

interface KPIStripProps {
  ytd: YTDSummary;
}

export default function KPIStrip({ ytd }: KPIStripProps) {
  const hasActuals = ytd.monthsReported > 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="YTD Revenue"
        value={hasActuals ? formatCurrency(ytd.ytdActualRev) : formatCurrency(ytd.ytdBudgetRev)}
        subtitle={hasActuals ? `Budget: ${formatCurrency(ytd.ytdBudgetRev)}` : `Budget (${ytd.monthsElapsed} months elapsed)`}
        variance={hasActuals && ytd.ytdVarianceRev !== null ? formatVariance(ytd.ytdVarianceRev) : undefined}
        varianceType={ytd.ytdVarianceRev !== null && ytd.ytdVarianceRev >= 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        title="YTD Costs"
        value={hasActuals ? formatCurrency(ytd.ytdActualCost) : formatCurrency(ytd.ytdBudgetCost)}
        subtitle={hasActuals ? `Budget: ${formatCurrency(ytd.ytdBudgetCost)}` : `Budget (${ytd.monthsElapsed} months elapsed)`}
        variance={hasActuals && ytd.ytdVarianceCost !== null ? formatVariance(-ytd.ytdVarianceCost) : undefined}
        varianceType={ytd.ytdVarianceCost !== null && ytd.ytdVarianceCost <= 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        title="YTD Net Position"
        value={hasActuals ? formatCurrency(ytd.ytdActualNet) : formatCurrency(ytd.ytdBudgetNet)}
        subtitle={hasActuals ? `Budget: ${formatCurrency(ytd.ytdBudgetNet)}` : `Budget (${ytd.monthsElapsed} months elapsed)`}
        variance={hasActuals && ytd.ytdActualNet !== null ? formatVariance(ytd.ytdActualNet - ytd.ytdBudgetNet) : undefined}
        varianceType={ytd.ytdActualNet !== null && ytd.ytdActualNet - ytd.ytdBudgetNet >= 0 ? 'positive' : 'negative'}
      />
      <MetricCard
        title="Months Reported"
        value={`${ytd.monthsReported} / ${ytd.monthsElapsed}`}
        subtitle={ytd.monthsReported === 0
          ? `No actuals yet — projected: ${formatCurrency(ytd.projectedYearEnd)}`
          : `Projected year-end: ${formatCurrency(ytd.projectedYearEnd)}`}
        progress={(ytd.monthsReported / ytd.monthsElapsed) * 100}
      />
    </div>
  );
}
