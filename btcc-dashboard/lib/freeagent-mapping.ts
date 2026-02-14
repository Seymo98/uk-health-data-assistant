import { ActualsData } from './types';
import { getTrialBalance, getCategories, FreeAgentCategory } from './freeagent';

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

// Configurable mapping from FreeAgent category names to BTCC dashboard categories.
// FreeAgent keys are case-insensitive substrings matched against category descriptions.
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

// Determine if a FreeAgent category group is income
function isIncomeGroup(groupDescription: string): boolean {
  const lower = groupDescription.toLowerCase();
  return lower.includes('income') || lower.includes('revenue') || lower.includes('sales');
}

// Build URL-to-category lookup map from the /categories endpoint
function buildCategoryMap(categories: FreeAgentCategory[]): Map<string, FreeAgentCategory> {
  const map = new Map<string, FreeAgentCategory>();
  for (const cat of categories) {
    map.set(cat.url, cat);
  }
  return map;
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

// Sync actuals from FreeAgent Trial Balance for each month.
// Uses the Trial Balance endpoint (per-category breakdown) instead of P&L Summary
// (which only returns aggregate totals).
export async function syncFromFreeAgent(
  accessToken: string,
  mappings: CategoryMapping[] = DEFAULT_CATEGORY_MAPPINGS
): Promise<ActualsData> {
  const actuals = emptyActuals();
  const today = new Date();

  // Fetch all categories once — builds URL → { description, group_description } map
  const categories = await getCategories(accessToken);
  const categoryMap = buildCategoryMap(categories);

  for (let monthIdx = 0; monthIdx < 12; monthIdx++) {
    const range = MONTH_RANGES[monthIdx];
    const monthStart = new Date(range.from);

    // Only fetch months that have started
    if (monthStart > today) continue;

    try {
      const tbData = await getTrialBalance(accessToken, range.from, range.to);

      // Parse trial balance response — handle both array and nested structures
      const summary = tbData.trial_balance_summary;
      let entries: Array<Record<string, unknown>> = [];

      if (Array.isArray(summary)) {
        entries = summary;
      } else if (summary && typeof summary === 'object') {
        const obj = summary as Record<string, unknown>;
        if (Array.isArray(obj.categories)) {
          entries = obj.categories as Array<Record<string, unknown>>;
        } else if (Array.isArray(obj.trial_balance_items)) {
          entries = obj.trial_balance_items as Array<Record<string, unknown>>;
        }
      }

      for (const entry of entries) {
        // Resolve category name: use URL lookup first, fall back to direct name field
        const categoryUrl = (entry.category as string) || '';
        const catInfo = categoryMap.get(categoryUrl);
        const name = catInfo?.description || (entry.name as string) || (entry.description as string) || '';

        if (!name) continue;

        // Get the amounts for this period
        // Handle both flat (debit/credit at top level) and nested (activity.debit/credit)
        let debit: number;
        let credit: number;

        const activity = entry.activity as Record<string, string> | undefined;
        if (activity) {
          debit = parseFloat(activity.debit || '0');
          credit = parseFloat(activity.credit || '0');
        } else {
          debit = parseFloat(String(entry.debit || '0'));
          credit = parseFloat(String(entry.credit || '0'));
        }

        if (isNaN(debit)) debit = 0;
        if (isNaN(credit)) credit = 0;

        // Skip entries with no activity
        if (debit === 0 && credit === 0) continue;

        // Try to match against our category mappings
        const match = matchCategory(name, mappings);

        if (match) {
          if (match.type === 'revenue') {
            // Income: credit side represents revenue
            const amount = Math.abs(credit - debit);
            if (amount > 0) {
              actuals.revenue[match.dashboardCategory][monthIdx] =
                (actuals.revenue[match.dashboardCategory][monthIdx] ?? 0) + amount;
            }
          } else {
            // Costs: debit side represents expenses
            const amount = Math.abs(debit - credit);
            if (amount > 0) {
              actuals.costs[match.dashboardCategory][monthIdx] =
                (actuals.costs[match.dashboardCategory][monthIdx] ?? 0) + amount;
            }
          }
        } else if (catInfo) {
          // Unmatched category: use group_description to determine income vs expense
          if (isIncomeGroup(catInfo.group_description)) {
            const amount = Math.abs(credit - debit);
            if (amount > 0) {
              actuals.revenue['Other Revenue'][monthIdx] =
                (actuals.revenue['Other Revenue'][monthIdx] ?? 0) + amount;
            }
          } else {
            const amount = Math.abs(debit - credit);
            if (amount > 0) {
              actuals.costs['Other Costs'][monthIdx] =
                (actuals.costs['Other Costs'][monthIdx] ?? 0) + amount;
            }
          }
        }
      }
    } catch (err) {
      console.error(`Failed to fetch trial balance for month ${monthIdx} (${range.from}):`, err);
      // Skip this month on error, leave as null
    }
  }

  // For months that have started but yielded no data, set all categories to 0
  // (meaning no transactions recorded in FreeAgent for that month yet)
  for (let monthIdx = 0; monthIdx < 12; monthIdx++) {
    const monthStart = new Date(MONTH_RANGES[monthIdx].from);
    if (monthStart > today) continue;

    const hasRevData = Object.values(actuals.revenue).some(arr => arr[monthIdx] !== null);
    const hasCostData = Object.values(actuals.costs).some(arr => arr[monthIdx] !== null);

    if (!hasRevData && !hasCostData) {
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
