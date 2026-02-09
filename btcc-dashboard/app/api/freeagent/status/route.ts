import { NextResponse } from 'next/server';
import { getStoredTokens, getValidAccessToken } from '@/lib/token-store';

export async function GET() {
  const configured = !!(process.env.FREEAGENT_CLIENT_ID && process.env.FREEAGENT_CLIENT_SECRET);

  const tokens = await getStoredTokens();
  if (!tokens) {
    return NextResponse.json({
      configured,
      connected: false,
      companyName: null,
      connectedAt: null,
      tokenValid: false,
    });
  }

  // Check if the token is still valid / refreshable
  const accessToken = await getValidAccessToken();

  return NextResponse.json({
    configured,
    connected: true,
    companyName: tokens.company_name || null,
    connectedAt: tokens.connected_at || null,
    tokenValid: !!accessToken,
    sandbox: process.env.FREEAGENT_SANDBOX === 'true',
  });
}
