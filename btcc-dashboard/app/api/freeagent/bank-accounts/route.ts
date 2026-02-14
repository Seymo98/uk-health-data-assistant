import { NextResponse, NextRequest } from 'next/server';
import { getValidAccessToken, getStoredTokens, saveTokens } from '@/lib/token-store';
import { getBankAccounts } from '@/lib/freeagent';

export async function GET() {
  const accessToken = await getValidAccessToken();
  if (!accessToken) {
    return NextResponse.json({ accounts: [], selected: '' });
  }

  const tokens = await getStoredTokens();

  try {
    const accounts = await getBankAccounts(accessToken);
    return NextResponse.json({
      accounts: accounts.map(a => ({
        url: a.url,
        name: a.name,
        current_balance: a.current_balance,
        type: a.type,
      })),
      selected: tokens?.bank_account_url || '',
    });
  } catch {
    return NextResponse.json({ accounts: [], selected: '' });
  }
}

export async function POST(request: NextRequest) {
  const tokens = await getStoredTokens();
  if (!tokens) {
    return NextResponse.json({ error: 'Not connected' }, { status: 401 });
  }

  const { bankAccountUrl } = await request.json();
  await saveTokens({ ...tokens, bank_account_url: bankAccountUrl });

  return NextResponse.json({ success: true });
}
