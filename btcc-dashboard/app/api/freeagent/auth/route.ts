import { NextResponse } from 'next/server';
import { getAuthorizeUrl } from '@/lib/freeagent';

export async function GET() {
  if (!process.env.FREEAGENT_CLIENT_ID) {
    return NextResponse.json(
      { error: 'FreeAgent credentials not configured. Set FREEAGENT_CLIENT_ID and FREEAGENT_CLIENT_SECRET in .env.local' },
      { status: 500 }
    );
  }

  const authorizeUrl = getAuthorizeUrl();
  return NextResponse.redirect(authorizeUrl);
}
