export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  const abs = Math.abs(value);
  const formatted = abs >= 1000
    ? `£${abs.toLocaleString('en-GB', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
    : `£${abs.toFixed(0)}`;
  return value < 0 ? `-${formatted}` : formatted;
}

export function formatCurrencyShort(value: number): string {
  if (Math.abs(value) >= 1000) {
    return `£${(value / 1000).toFixed(1)}k`;
  }
  return `£${value.toFixed(0)}`;
}

export function formatPercent(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
}

export function formatVariance(value: number): string {
  const prefix = value >= 0 ? '+' : '';
  return `${prefix}${formatCurrency(value)}`;
}

export function varianceColor(value: number, isCost: boolean = false): string {
  const favourable = isCost ? value <= 0 : value >= 0;
  return favourable ? 'text-emerald-400' : 'text-red-400';
}

export function varianceBg(value: number, isCost: boolean = false): string {
  const favourable = isCost ? value <= 0 : value >= 0;
  return favourable ? 'bg-emerald-400/10' : 'bg-red-400/10';
}
