import { BudgetData, ActualsData, MonthSummary, YTDSummary, MonthlyData, VarianceAlert } from './types';

export const MONTHS = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

function sumCategory(data: MonthlyData, monthIndex: number): number {
  return Object.values(data).reduce((sum, values) => {
    const val = values[monthIndex];
    return sum + (val ?? 0);
  }, 0);
}

function sumCategoryTotal(data: MonthlyData): number {
  return Object.values(data).reduce((sum, values) => {
    return sum + values.reduce((s: number, v) => s + (v ?? 0), 0 as number);
  }, 0);
}

function sumCategoryAnnual(data: MonthlyData, category: string): number {
  const values = data[category];
  if (!values) return 0;
  return values.reduce((s: number, v) => s + (v ?? 0), 0 as number);
}

function hasAnyActual(data: MonthlyData, monthIndex: number): boolean {
  return Object.values(data).some(values => values[monthIndex] !== null);
}

export function getMonthSummaries(budget: BudgetData, actuals: ActualsData): MonthSummary[] {
  return MONTHS.map((month, i) => {
    const budgetRev = sumCategory(budget.revenue, i);
    const budgetCost = sumCategory(budget.costs, i);
    const hasActualRev = hasAnyActual(actuals.revenue, i);
    const hasActualCost = hasAnyActual(actuals.costs, i);
    const hasActual = hasActualRev || hasActualCost;

    const actualRev = hasActualRev ? sumCategory(actuals.revenue, i) : null;
    const actualCost = hasActualCost ? sumCategory(actuals.costs, i) : null;

    return {
      month,
      monthIndex: i,
      budgetRev,
      budgetCost,
      budgetNet: budgetRev - budgetCost,
      actualRev,
      actualCost,
      actualNet: actualRev !== null && actualCost !== null ? actualRev - actualCost : null,
      hasActual,
    };
  });
}

export function getYTDSummary(budget: BudgetData, actuals: ActualsData): YTDSummary {
  const summaries = getMonthSummaries(budget, actuals);
  const reported = summaries.filter(s => s.hasActual);
  const monthsReported = reported.length;

  let ytdBudgetRev = 0;
  let ytdActualRev = 0;
  let ytdBudgetCost = 0;
  let ytdActualCost = 0;

  for (const s of reported) {
    ytdBudgetRev += s.budgetRev;
    ytdActualRev += s.actualRev ?? 0;
    ytdBudgetCost += s.budgetCost;
    ytdActualCost += s.actualCost ?? 0;
  }

  const fullYearBudgetNet = sumCategoryTotal(budget.revenue) - sumCategoryTotal(budget.costs);
  const ytdVariance = (ytdActualRev - ytdActualCost) - (ytdBudgetRev - ytdBudgetCost);
  const projectedYearEnd = budget.openingBalance + fullYearBudgetNet + ytdVariance;

  return {
    monthsReported,
    ytdBudgetRev,
    ytdActualRev,
    ytdBudgetCost,
    ytdActualCost,
    ytdVarianceRev: ytdActualRev - ytdBudgetRev,
    ytdVarianceCost: ytdActualCost - ytdBudgetCost,
    ytdBudgetNet: ytdBudgetRev - ytdBudgetCost,
    ytdActualNet: ytdActualRev - ytdActualCost,
    projectedYearEnd,
  };
}

export function getBankBalanceProjection(budget: BudgetData, actuals: ActualsData): { month: string; budget: number; actual: number | null }[] {
  let budgetBalance = budget.openingBalance;
  let actualBalance: number | null = budget.openingBalance;
  const summaries = getMonthSummaries(budget, actuals);
  const result: { month: string; budget: number; actual: number | null }[] = [];

  for (const s of summaries) {
    budgetBalance += s.budgetNet;
    if (s.hasActual && actualBalance !== null) {
      actualBalance += (s.actualNet ?? s.budgetNet);
    } else if (!s.hasActual) {
      actualBalance = null;
    }
    result.push({ month: s.month, budget: budgetBalance, actual: actualBalance });
  }
  return result;
}

export function getCategoryBreakdown(
  budget: BudgetData,
  actuals: ActualsData,
  type: 'revenue' | 'costs'
): { category: string; annual: number; ytdBudget: number; ytdActual: number; variance: number; variancePct: number }[] {
  const budgetData = budget[type];
  const actualsData = actuals[type];
  const summaries = getMonthSummaries(budget, actuals);
  const reportedMonths = summaries.filter(s => s.hasActual).map(s => s.monthIndex);

  return Object.keys(budgetData).map(category => {
    const annual = sumCategoryAnnual(budgetData, category);
    let ytdBudget = 0;
    let ytdActual = 0;

    for (const mi of reportedMonths) {
      ytdBudget += budgetData[category]?.[mi] ?? 0;
      ytdActual += actualsData[category]?.[mi] ?? 0;
    }

    const variance = type === 'revenue'
      ? ytdActual - ytdBudget
      : ytdBudget - ytdActual;
    const variancePct = ytdBudget !== 0 ? (variance / ytdBudget) * 100 : 0;

    return { category, annual, ytdBudget, ytdActual, variance, variancePct };
  });
}

export function generateVarianceAlerts(budget: BudgetData, actuals: ActualsData): VarianceAlert[] {
  const alerts: VarianceAlert[] = [];
  const summaries = getMonthSummaries(budget, actuals);
  const reportedMonths = summaries.filter(s => s.hasActual);

  if (reportedMonths.length === 0) return alerts;

  // Check revenue categories below budget
  const revBreakdown = getCategoryBreakdown(budget, actuals, 'revenue');
  for (const item of revBreakdown) {
    if (item.ytdBudget > 0 && item.variancePct < -15) {
      alerts.push({
        id: `rev-${item.category}`,
        type: item.variancePct < -25 ? 'critical' : 'warning',
        category: item.category,
        message: `${item.category} is ${Math.abs(item.variancePct).toFixed(0)}% below budget YTD`,
      });
    }
  }

  // Check cost categories above budget
  const costBreakdown = getCategoryBreakdown(budget, actuals, 'costs');
  for (const item of costBreakdown) {
    if (item.ytdBudget > 0 && item.variancePct < -15) {
      alerts.push({
        id: `cost-${item.category}`,
        type: item.variancePct < -25 ? 'critical' : 'warning',
        category: item.category,
        message: `${item.category} is ${Math.abs(item.variancePct).toFixed(0)}% above budget YTD`,
      });
    }
  }

  // Bar margin check
  const actualBarSales = reportedMonths.reduce((sum, s) => {
    return sum + (actuals.revenue['Bar Sales']?.[s.monthIndex] ?? 0);
  }, 0);
  const actualBarStock = reportedMonths.reduce((sum, s) => {
    return sum + (actuals.costs['Bar Stock']?.[s.monthIndex] ?? 0);
  }, 0);

  if (actualBarSales > 0) {
    const margin = (actualBarSales - actualBarStock) / actualBarSales;
    if (margin < 0.50) {
      alerts.push({
        id: 'bar-margin-critical',
        type: 'critical',
        category: 'Bar Margin',
        message: `Bar margin is ${(margin * 100).toFixed(1)}% — critically below 50% target`,
      });
    } else if (margin < 0.55) {
      alerts.push({
        id: 'bar-margin-warning',
        type: 'warning',
        category: 'Bar Margin',
        message: `Bar margin is ${(margin * 100).toFixed(1)}% — below 55% target`,
      });
    }
  }

  // Projected year-end bank balance
  const ytd = getYTDSummary(budget, actuals);
  if (ytd.projectedYearEnd < 15000) {
    alerts.push({
      id: 'bank-balance-low',
      type: ytd.projectedYearEnd < 10000 ? 'critical' : 'warning',
      category: 'Bank Balance',
      message: `Projected year-end balance £${ytd.projectedYearEnd.toLocaleString()} — below £15,000 threshold`,
    });
  }

  // Monthly net cashflow significantly worse than budget
  for (const s of reportedMonths) {
    if (s.actualNet !== null && s.budgetNet !== undefined) {
      const diff = s.actualNet - s.budgetNet;
      if (diff < -500) {
        alerts.push({
          id: `month-${s.month}-cashflow`,
          type: diff < -1000 ? 'critical' : 'warning',
          category: s.month,
          message: `${s.month} net cashflow £${diff.toFixed(0)} worse than budget`,
        });
      }
    }
  }

  return alerts;
}
