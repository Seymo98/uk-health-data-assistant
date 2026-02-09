import { NextRequest, NextResponse } from 'next/server';
import { exchangeCodeForTokens, getCompany } from '@/lib/freeagent';
import { saveTokens } from '@/lib/token-store';

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code');
  const error = request.nextUrl.searchParams.get('error');

  if (error) {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    return NextResponse.redirect(`${baseUrl}/settings?error=${encodeURIComponent(error)}`);
  }

  if (!code) {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    return NextResponse.redirect(`${baseUrl}/settings?error=no_code`);
  }

  try {
    const tokens = await exchangeCodeForTokens(code);

    // Fetch company name to display in the UI
    let companyName = 'Unknown';
    try {
      const company = await getCompany(tokens.access_token);
      companyName = company.name;
    } catch {
      // Non-critical if we can't get the company name
    }

    await saveTokens({
      ...tokens,
      company_name: companyName,
      connected_at: new Date().toISOString(),
    });

    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    return NextResponse.redirect(`${baseUrl}/settings?connected=true`);
  } catch (err) {
    console.error('FreeAgent callback error:', err);
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    return NextResponse.redirect(`${baseUrl}/settings?error=token_exchange_failed`);
  }
}
