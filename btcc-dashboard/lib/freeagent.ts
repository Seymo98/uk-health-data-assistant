const LIVE_BASE = 'https://api.freeagent.com/v2';
const SANDBOX_BASE = 'https://api.sandbox.freeagent.com/v2';

function getBaseUrl(): string {
  return process.env.FREEAGENT_SANDBOX === 'true' ? SANDBOX_BASE : LIVE_BASE;
}

function getAuthBaseUrl(): string {
  return process.env.FREEAGENT_SANDBOX === 'true'
    ? 'https://api.sandbox.freeagent.com/v2'
    : 'https://api.freeagent.com/v2';
}

export function getAuthorizeUrl(): string {
  const clientId = process.env.FREEAGENT_CLIENT_ID;
  const redirectUri = process.env.FREEAGENT_REDIRECT_URI || `${process.env.NEXT_PUBLIC_BASE_URL}/api/freeagent/callback`;
  const base = getAuthBaseUrl();
  return `${base}/approve_app?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code`;
}

export interface FreeAgentTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  obtained_at: string;
}

export async function exchangeCodeForTokens(code: string): Promise<FreeAgentTokens> {
  const base = getAuthBaseUrl();
  const clientId = process.env.FREEAGENT_CLIENT_ID!;
  const clientSecret = process.env.FREEAGENT_CLIENT_SECRET!;
  const redirectUri = process.env.FREEAGENT_REDIRECT_URI || `${process.env.NEXT_PUBLIC_BASE_URL}/api/freeagent/callback`;

  const credentials = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');

  const res = await fetch(`${base}/token_endpoint`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Token exchange failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  return {
    ...data,
    obtained_at: new Date().toISOString(),
  };
}

export async function refreshAccessToken(refreshToken: string): Promise<FreeAgentTokens> {
  const base = getAuthBaseUrl();
  const clientId = process.env.FREEAGENT_CLIENT_ID!;
  const clientSecret = process.env.FREEAGENT_CLIENT_SECRET!;

  const credentials = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');

  const res = await fetch(`${base}/token_endpoint`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Token refresh failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  return {
    ...data,
    obtained_at: new Date().toISOString(),
  };
}

async function freeagentFetch(path: string, accessToken: string, params?: Record<string, string>): Promise<Record<string, unknown>> {
  const base = getBaseUrl();
  const url = new URL(`${base}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }

  const res = await fetch(url.toString(), {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/json',
      'User-Agent': 'BTCCDashboard/1.0',
    },
  });

  if (res.status === 429) {
    const retryAfter = res.headers.get('Retry-After') || '60';
    throw new Error(`Rate limited. Retry after ${retryAfter}s`);
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`FreeAgent API error (${res.status}): ${text}`);
  }

  return res.json();
}

export interface FreeAgentCompany {
  name: string;
  currency: string;
  freeagent_start_date: string;
}

export async function getCompany(accessToken: string): Promise<FreeAgentCompany> {
  const data = await freeagentFetch('/company', accessToken);
  const company = data.company as Record<string, unknown>;
  return {
    name: company.name as string,
    currency: company.currency as string,
    freeagent_start_date: company.freeagent_start_date as string,
  };
}

export interface FreeAgentBankAccount {
  url: string;
  name: string;
  current_balance: string;
  type: string;
}

export async function getBankAccounts(accessToken: string): Promise<FreeAgentBankAccount[]> {
  const data = await freeagentFetch('/bank_accounts', accessToken);
  return (data.bank_accounts as FreeAgentBankAccount[]) || [];
}

export interface FreeAgentBankTransaction {
  url: string;
  dated_on: string;
  amount: string;
  description: string;
  bank_account: string;
}

export async function getBankTransactions(
  accessToken: string,
  bankAccountUrl: string,
  fromDate: string,
  toDate: string
): Promise<FreeAgentBankTransaction[]> {
  const allTransactions: FreeAgentBankTransaction[] = [];
  let page = 1;

  while (true) {
    const data = await freeagentFetch('/bank_transactions', accessToken, {
      bank_account: bankAccountUrl,
      from_date: fromDate,
      to_date: toDate,
      per_page: '100',
      page: page.toString(),
    });

    const transactions = (data.bank_transactions as FreeAgentBankTransaction[]) || [];
    allTransactions.push(...transactions);

    if (transactions.length < 100) break;
    page++;
  }

  return allTransactions;
}

export interface ProfitAndLossSummary {
  [category: string]: string; // category name -> amount as string
}

export async function getProfitAndLoss(
  accessToken: string,
  fromDate: string,
  toDate: string
): Promise<Record<string, unknown>> {
  return freeagentFetch('/accounting/profit_and_loss/summary', accessToken, {
    from_date: fromDate,
    to_date: toDate,
  });
}

export async function getTrialBalance(
  accessToken: string,
  fromDate: string,
  toDate: string
): Promise<Record<string, unknown>> {
  return freeagentFetch('/accounting/trial_balance/summary', accessToken, {
    from_date: fromDate,
    to_date: toDate,
  });
}
