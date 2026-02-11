import { ActualsData, MonthlyData } from './types';
import { getProfitAndLoss, getBankTransactions } from './freeagent';

// Financial year Oct 2025 to Sep 2026
// Month index 0 = Oct 2025, index 11 = Sep 2026
const MONTH_RANGES: { from: string; to: string }[] = [
  { from: '2025-10-01', to: '2025-10-31' },
  { from: '2025-11-01', to: '2025-11-30' },
  { from: '2025-12-01', to: '2025-12-31' },
  { from: '2026-01-01', to: '2026-01-31' },
  { from: '2026-02-01', to: '2026-02-28' },
  { from: '2026-03-01', to: '2026-03-31' },
  { from: '2026-04-01', to: '2026-04-30' },
  { from: '2026-05-01', to: '2026-05-31' },
  { from: '2026-06-01', to: '2026-06-30' },
  { from: '2026-07-01', to: '2026-07-31' },
  { from: '2026-08-01', to: '2026-08-31' },
  { from: '2026-09-01', to: '2026-09-30' },
];

// Configurable mapping from FreeAgent P&L category names to BTCC dashboard categories.
// Users can customise this to match their FreeAgent chart of accounts.
// FreeAgent keys are case-insensitive substrings matched against the P&L category names.
export interface CategoryMapping {
  freeagentPattern: string;
  dashboardCategory: string;
  type: 'revenue' | 'costs';
}

export const DEFAULT_CATEGORY_MAPPINGS: CategoryMapping[] = [
  // Revenue
  { freeagentPattern: 'bar sales', dashboardCategory: 'Bar Sales', type: 'revenue' },
  { freeagentPattern: 'bar income', dashboardCategory: 'Bar Sales', type: 'revenue' },
  { freeagentPattern: '100 club', dashboardCategory: '100 Club', type: 'revenue' },
  { freeagentPattern: 'hundred club', dashboardCategory: '100 Club', type: 'revenue' },
  { freeagentPattern: 'sponsor', dashboardCategory: 'Sponsorship', type: 'revenue' },
  { freeagentPattern: 'match fee', dashboardCategory: 'Match Fees', type: 'revenue' },
  { freeagentPattern: 'junior sub', dashboardCategory: 'Junior Subs', type: 'revenue' },
  { freeagentPattern: 'all star', dashboardCategory: 'All Stars Subs', type: 'revenue' },
  { freeagentPattern: 'winter net', dashboardCategory: 'Winter Nets', type: 'revenue' },
  { freeagentPattern: 'hire of facilities', dashboardCategory: 'Hire of Facilities', type: 'revenue' },
  { freeagentPattern: 'facility hire', dashboardCategory: 'Hire of Facilities', type: 'revenue' },
  { freeagentPattern: 'room hire', dashboardCategory: 'Hire of Facilities', type: 'revenue' },

  // Costs
  { freeagentPattern: 'bar stock', dashboardCategory: 'Bar Stock', type: 'costs' },
  { freeagentPattern: 'bar purchase', dashboardCategory: 'Bar Stock', type: 'costs' },
  { freeagentPattern: '100 club payout', dashboardCategory: '100 Club Payouts', type: 'costs' },
  { freeagentPattern: 'hundred club payout', dashboardCategory: '100 Club Payouts', type: 'costs' },
  { freeagentPattern: 'ground', dashboardCategory: 'G&C Running', type: 'costs' },
  { freeagentPattern: 'clubhouse', dashboardCategory: 'G&C Running', type: 'costs' },
  { freeagentPattern: 'g&c', dashboardCategory: 'G&C Running', type: 'costs' },
  { freeagentPattern: 'electric', dashboardCategory: 'Electricity', type: 'costs' },
  { freeagentPattern: 'energy', dashboardCategory: 'Electricity', type: 'costs' },
  { freeagentPattern: 'insurance', dashboardCategory: 'Insurance', type: 'costs' },
  { freeagentPattern: 'presentation', dashboardCategory: 'Presentation Eve', type: 'costs' },
  { freeagentPattern: 'awards', dashboardCategory: 'Presentation Eve', type: 'costs' },
  { freeagentPattern: 'umpire', dashboardCategory: 'Umpires', type: 'costs' },
  { freeagentPattern: 'kit', dashboardCategory: 'Kit & Equipment', type: 'costs' },
  { freeagentPattern: 'equipment', dashboardCategory: 'Kit & Equipment', type: 'costs' },
  { freeagentPattern: 'competition', dashboardCategory: 'Competitions', type: 'costs' },
  { freeagentPattern: 'league fee', dashboardCategory: 'Competitions', type: 'costs' },
  { freeagentPattern: 'hire of net', dashboardCategory: 'Hire of Nets', type: 'costs' },
  { freeagentPattern: 'net hire', dashboardCategory: 'Hire of Nets', type: 'costs' },
  { freeagentPattern: 'improvement', dashboardCategory: 'Improvements', type: 'costs' },
  { freeagentPattern: 'capital', dashboardCategory: 'Improvements', type: 'costs' },
  { freeagentPattern: 'refurbish', dashboardCategory: 'Improvements', type: 'costs' },
];

function matchCategory(
  freeagentName: string,
  mappings: CategoryMapping[]
): { dashboardCategory: string; type: 'revenue' | 'costs' } | null {
  const lower = freeagentName.toLowerCase();
  for (const mapping of mappings) {
    if (lower.includes(mapping.freeagentPattern.toLowerCase())) {
      return { dashboardCategory: mapping.dashboardCategory, type: mapping.type };
    }
  }
  return null;
}

// Empty actuals template
function emptyActuals(): ActualsData {
  const emptyRow = (): (number | null)[] => Array(12).fill(null);
  return {
    lastUpdated: null,
    revenue: {
      'Bar Sales': emptyRow(),
      '100 Club': emptyRow(),
      'Sponsorship': emptyRow(),
      'Match Fees': emptyRow(),
      'Junior Subs': emptyRow(),
      'All Stars Subs': emptyRow(),
      'Winter Nets': emptyRow(),
      'Hire of Facilities': emptyRow(),
      'Other Revenue': emptyRow(),
    },
    costs: {
      'Bar Stock': emptyRow(),
      '100 Club Payouts': emptyRow(),
      'G&C Running': emptyRow(),
      'Electricity': emptyRow(),
      'Insurance': emptyRow(),
      'Presentation Eve': emptyRow(),
      'Umpires': emptyRow(),
      'Kit & Equipment': emptyRow(),
      'Competitions': emptyRow(),
      'Hire of Nets': emptyRow(),
      'Improvements': emptyRow(),
      'Other Costs': emptyRow(),
    },
  };
}

// Sync actuals from FreeAgent P&L data for each month
export async function syncFromFreeAgent(
  accessToken: string,
  mappings: CategoryMapping[] = DEFAULT_CATEGORY_MAPPINGS
): Promise<ActualsData> {
  const actuals = emptyActuals();
  const today = new Date();

  for (let monthIdx = 0; monthIdx < 12; monthIdx++) {
    const range = MONTH_RANGES[monthIdx];
    const monthEnd = new Date(range.to);

    // Only fetch months that have started (don't query future months)
    const monthStart = new Date(range.from);
    if (monthStart > today) continue;

    try {
      const pnlData = await getProfitAndLoss(accessToken, range.from, range.to);

      // FreeAgent P&L response structure varies, but typically has
      // profit_and_loss.income and profit_and_loss.expenditure sections
      const pnl = pnlData.profit_and_loss as Record<string, unknown> | undefined;
      if (!pnl) continue;

      // Process income categories
      const incomeCategories = extractCategories(pnl, 'income');
      for (const [name, amount] of Object.entries(incomeCategories)) {
        const match = matchCategory(name, mappings);
        if (match && match.type === 'revenue' && actuals.revenue[match.dashboardCategory]) {
          actuals.revenue[match.dashboardCategory][monthIdx] =
            (actuals.revenue[match.dashboardCategory][monthIdx] ?? 0) + amount;
        } else if (!match) {
          // Unmapped revenue goes to Other Revenue
          actuals.revenue['Other Revenue'][monthIdx] =
            (actuals.revenue['Other Revenue'][monthIdx] ?? 0) + amount;
        }
      }

      // Process expenditure categories
      const costCategories = extractCategories(pnl, 'expenditure');
      for (const [name, amount] of Object.entries(costCategories)) {
        const match = matchCategory(name, mappings);
        if (match && match.type === 'costs' && actuals.costs[match.dashboardCategory]) {
          actuals.costs[match.dashboardCategory][monthIdx] =
            (actuals.costs[match.dashboardCategory][monthIdx] ?? 0) + Math.abs(amount);
        } else if (!match) {
          // Unmapped costs go to Other Costs
          actuals.costs['Other Costs'][monthIdx] =
            (actuals.costs['Other Costs'][monthIdx] ?? 0) + Math.abs(amount);
        }
      }

      // If the month hasn't ended yet, still count it as having data
      // (partial month is better than nothing)

    } catch (err) {
      console.error(`Failed to fetch P&L for month ${monthIdx} (${range.from}):`, err);
      // Skip this month on error, leave as null
    }
  }

  // Only set months with actual data to non-null; leave future months as null
  // Check each month — if all categories are still null, leave it
  for (let monthIdx = 0; monthIdx < 12; monthIdx++) {
    const monthStart = new Date(MONTH_RANGES[monthIdx].from);
    if (monthStart > today) continue;

    const hasRevData = Object.values(actuals.revenue).some(arr => arr[monthIdx] !== null);
    const hasCostData = Object.values(actuals.costs).some(arr => arr[monthIdx] !== null);

    // If the month has started but we got no data at all, set all to 0
    // (meaning the treasurer has no transactions for that month yet)
    if (!hasRevData && !hasCostData && monthStart <= today) {
      Object.keys(actuals.revenue).forEach(cat => {
        actuals.revenue[cat][monthIdx] = 0;
      });
      Object.keys(actuals.costs).forEach(cat => {
        actuals.costs[cat][monthIdx] = 0;
      });
    }
  }

  actuals.lastUpdated = new Date().toISOString();
  return actuals;
}

// Extract category names and amounts from a P&L section
function extractCategories(
  pnl: Record<string, unknown>,
  section: 'income' | 'expenditure'
): Record<string, number> {
  const result: Record<string, number> = {};

  // FreeAgent P&L structure can be nested. Common patterns:
  // pnl.income_categories, pnl.expenditure_categories (array of {name, total})
  // or pnl[section] as array

  // Try different known structures
  const sectionData =
    pnl[`${section}_categories`] ||
    pnl[section] ||
    pnl[`${section}_summary`];

  if (Array.isArray(sectionData)) {
    for (const item of sectionData) {
      const entry = item as Record<string, unknown>;
      const name = (entry.name || entry.description || entry.category || '') as string;
      const total = parseFloat(String(entry.total || entry.amount || entry.value || '0'));
      if (name && !isNaN(total)) {
        result[name] = (result[name] || 0) + total;
      }

      // Handle sub-categories if present
      const subCategories = entry.sub_categories || entry.children;
      if (Array.isArray(subCategories)) {
        for (const sub of subCategories) {
          const subEntry = sub as Record<string, unknown>;
          const subName = (subEntry.name || subEntry.description || '') as string;
          const subTotal = parseFloat(String(subEntry.total || subEntry.amount || '0'));
          if (subName && !isNaN(subTotal)) {
            result[subName] = (result[subName] || 0) + subTotal;
          }
        }
      }
    }
  } else if (typeof sectionData === 'object' && sectionData !== null) {
    // Object format: { "Category Name": amount }
    for (const [name, value] of Object.entries(sectionData as Record<string, unknown>)) {
      const amount = parseFloat(String(value));
      if (!isNaN(amount)) {
        result[name] = amount;
      }
    }
  }

  return result;
}

// Get bank balance from FreeAgent
export async function getBankBalance(
  accessToken: string,
  bankAccountUrl: string
): Promise<{ currentBalance: number; transactions: { date: string; amount: number; description: string }[] }> {
  const transactions = await getBankTransactions(
    accessToken,
    bankAccountUrl,
    '2025-10-01',
    new Date().toISOString().split('T')[0]
  );

  const currentBalance = transactions.reduce((bal, t) => bal + parseFloat(t.amount), 0);

  return {
    currentBalance,
    transactions: transactions.map(t => ({
      date: t.dated_on,
      amount: parseFloat(t.amount),
      description: t.description,
    })),
  };
}
