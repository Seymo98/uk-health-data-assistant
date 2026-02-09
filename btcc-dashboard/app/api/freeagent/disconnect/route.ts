import { NextResponse } from 'next/server';
import { deleteTokens } from '@/lib/token-store';

export async function POST() {
  try {
    await deleteTokens();
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: 'Failed to disconnect' }, { status: 500 });
  }
}
