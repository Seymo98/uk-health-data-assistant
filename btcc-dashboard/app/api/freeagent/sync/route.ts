import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { getValidAccessToken } from '@/lib/token-store';
import { syncFromFreeAgent } from '@/lib/freeagent-mapping';

const ACTUALS_FILE = path.join(process.cwd(), 'data', 'actuals-2025-26.json');

export async function POST() {
  const accessToken = await getValidAccessToken();
  if (!accessToken) {
    return NextResponse.json(
      { error: 'Not connected to FreeAgent or token expired. Please reconnect.' },
      { status: 401 }
    );
  }

  try {
    const actuals = await syncFromFreeAgent(accessToken);

    // Save to the actuals file
    await fs.writeFile(ACTUALS_FILE, JSON.stringify(actuals, null, 2), 'utf-8');

    return NextResponse.json({
      success: true,
      lastUpdated: actuals.lastUpdated,
      message: 'Actuals synced from FreeAgent successfully',
    });
  } catch (err) {
    console.error('FreeAgent sync error:', err);
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json(
      { error: `Sync failed: ${message}` },
      { status: 500 }
    );
  }
}
