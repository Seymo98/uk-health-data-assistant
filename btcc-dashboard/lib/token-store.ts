import { promises as fs } from 'fs';
import path from 'path';
import { FreeAgentTokens, refreshAccessToken } from './freeagent';

const TOKEN_FILE = path.join(process.cwd(), 'data', 'freeagent-tokens.json');

export interface StoredTokens extends FreeAgentTokens {
  company_name?: string;
  connected_at?: string;
}

export async function getStoredTokens(): Promise<StoredTokens | null> {
  try {
    const data = await fs.readFile(TOKEN_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return null;
  }
}

export async function saveTokens(tokens: StoredTokens): Promise<void> {
  await fs.writeFile(TOKEN_FILE, JSON.stringify(tokens, null, 2), 'utf-8');
}

export async function deleteTokens(): Promise<void> {
  try {
    await fs.unlink(TOKEN_FILE);
  } catch {
    // File doesn't exist, that's fine
  }
}

export async function getValidAccessToken(): Promise<string | null> {
  const tokens = await getStoredTokens();
  if (!tokens) return null;

  // Check if token is expired or about to expire (within 1 hour)
  const obtainedAt = new Date(tokens.obtained_at).getTime();
  const expiresAt = obtainedAt + (tokens.expires_in * 1000);
  const now = Date.now();
  const oneHour = 60 * 60 * 1000;

  if (now < expiresAt - oneHour) {
    return tokens.access_token;
  }

  // Token expired or about to expire — refresh it
  try {
    const refreshed = await refreshAccessToken(tokens.refresh_token);
    await saveTokens({
      ...refreshed,
      company_name: tokens.company_name,
      connected_at: tokens.connected_at,
    });
    return refreshed.access_token;
  } catch (err) {
    console.error('Failed to refresh FreeAgent token:', err);
    return null;
  }
}
