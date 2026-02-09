import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const filePath = path.join(process.cwd(), 'data', 'actuals-2025-26.json');

export async function GET() {
  try {
    const data = await fs.readFile(filePath, 'utf-8');
    return NextResponse.json(JSON.parse(data));
  } catch {
    return NextResponse.json({ error: 'Failed to read actuals data' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    body.lastUpdated = new Date().toISOString();
    await fs.writeFile(filePath, JSON.stringify(body, null, 2), 'utf-8');
    return NextResponse.json({ success: true, lastUpdated: body.lastUpdated });
  } catch {
    return NextResponse.json({ error: 'Failed to save actuals data' }, { status: 500 });
  }
}
