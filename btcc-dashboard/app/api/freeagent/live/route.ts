import { NextResponse } from 'next/server';
import { getValidAccessToken, getStoredTokens } from '@/lib/token-store';
import { getBankAccounts, getOutstandingInvoices, getOutstandingBills } from '@/lib/freeagent';

export async function GET() {
  const accessToken = await getValidAccessToken();
  if (!accessToken) {
    return NextResponse.json({ error: 'Not connected' }, { status: 401 });
  }

  const tokens = await getStoredTokens();
  const bankAccountUrl = tokens?.bank_account_url;

  try {
    const [bankAccounts, invoices, bills] = await Promise.all([
      getBankAccounts(accessToken),
      getOutstandingInvoices(accessToken),
      getOutstandingBills(accessToken),
    ]);

    // Find selected bank account or use first one
    const selectedAccount = bankAccountUrl
      ? bankAccounts.find(a => a.url === bankAccountUrl) || bankAccounts[0]
      : bankAccounts[0];

    const today = new Date().toISOString().split('T')[0];

    const overdueInvoices = invoices.filter(i => i.due_on < today);
    const overdueBills = bills.filter(b => b.due_on < today);

    return NextResponse.json({
      bankBalance: selectedAccount ? {
        accountName: selectedAccount.name,
        currentBalance: parseFloat(selectedAccount.current_balance),
        accountUrl: selectedAccount.url,
      } : null,
      outstandingInvoices: {
        count: invoices.length,
        totalValue: invoices.reduce((sum, i) => sum + parseFloat(i.outstanding_value), 0),
        overdueCount: overdueInvoices.length,
        overdueValue: overdueInvoices.reduce((sum, i) => sum + parseFloat(i.outstanding_value), 0),
      },
      outstandingBills: {
        count: bills.length,
        totalValue: bills.reduce((sum, b) => sum + parseFloat(b.outstanding_value), 0),
        overdueCount: overdueBills.length,
        overdueValue: overdueBills.reduce((sum, b) => sum + parseFloat(b.outstanding_value), 0),
      },
      lastFetched: new Date().toISOString(),
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
