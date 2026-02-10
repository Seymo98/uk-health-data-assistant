export interface MonthlyData {
  [category: string]: (number | null)[];
}

export interface BudgetData {
  openingBalance: number;
  financialYear: string;
  revenue: MonthlyData;
  costs: MonthlyData;
}

export interface ActualsData {
  lastUpdated: string | null;
  revenue: MonthlyData;
  costs: MonthlyData;
}

export interface MonthSummary {
  month: string;
  monthIndex: number;
  budgetRev: number;
  budgetCost: number;
  budgetNet: number;
  actualRev: number | null;
  actualCost: number | null;
  actualNet: number | null;
  hasActual: boolean;
}

export interface YTDSummary {
  monthsReported: number;
  ytdBudgetRev: number;
  ytdActualRev: number;
  ytdBudgetCost: number;
  ytdActualCost: number;
  ytdVarianceRev: number;
  ytdVarianceCost: number;
  ytdBudgetNet: number;
  ytdActualNet: number;
  projectedYearEnd: number;
}

export interface HistoricalData {
  years: string[];
  barSales: number[];
  barStock: number[];
  barMargin: number[];
  totalRev: number[];
  totalCost: number[];
  netSurplus: number[];
  improvements: number[];
  bankBalance: number[];
  notes: { [year: string]: string };
}

export interface VarianceAlert {
  id: string;
  type: 'warning' | 'critical';
  category: string;
  message: string;
}
