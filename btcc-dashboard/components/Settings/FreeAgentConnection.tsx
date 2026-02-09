'use client';

import { useState, useEffect } from 'react';

interface ConnectionStatus {
  configured: boolean;
  connected: boolean;
  companyName: string | null;
  connectedAt: string | null;
  tokenValid: boolean;
  sandbox?: boolean;
}

export default function FreeAgentConnection() {
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);
  const [disconnecting, setDisconnecting] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/freeagent/status');
      const data = await res.json();
      setStatus(data);
    } catch {
      setStatus(null);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleConnect = () => {
    window.location.href = '/api/freeagent/auth';
  };

  const handleDisconnect = async () => {
    setDisconnecting(true);
    try {
      await fetch('/api/freeagent/disconnect', { method: 'POST' });
      await fetchStatus();
    } catch {
      // Ignore
    }
    setDisconnecting(false);
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const res = await fetch('/api/freeagent/sync', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSyncResult(`Synced successfully at ${new Date(data.lastUpdated).toLocaleString('en-GB')}`);
      } else {
        setSyncResult(`Sync failed: ${data.error}`);
      }
    } catch (err) {
      setSyncResult(`Sync failed: ${err instanceof Error ? err.message : 'Network error'}`);
    }
    setSyncing(false);
  };

  if (loading) {
    return (
      <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-6">
        <p className="text-[#8888aa]">Checking FreeAgent connection...</p>
      </div>
    );
  }

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-[#00875a] flex items-center justify-center text-white font-bold text-sm">
          FA
        </div>
        <div>
          <h3 className="text-[#e8e8f0] font-semibold">FreeAgent Integration</h3>
          <p className="text-[#8888aa] text-xs">
            Connect your FreeAgent account to automatically sync actual figures
          </p>
        </div>
      </div>

      {!status?.configured && (
        <div className="bg-[#ffd93d]/10 border border-[#ffd93d]/30 rounded-lg px-4 py-3">
          <p className="text-[#ffd93d] text-sm font-medium mb-1">Configuration Required</p>
          <p className="text-[#8888aa] text-xs">
            Add the following to your <code className="text-[#e8e8f0] bg-[#0d0d1a] px-1.5 py-0.5 rounded text-xs font-mono">.env.local</code> file:
          </p>
          <pre className="mt-2 bg-[#0d0d1a] rounded p-3 text-xs font-mono text-[#8888aa] overflow-x-auto">
{`FREEAGENT_CLIENT_ID=your_oauth_identifier
FREEAGENT_CLIENT_SECRET=your_oauth_secret
FREEAGENT_REDIRECT_URI=http://localhost:3000/api/freeagent/callback
NEXT_PUBLIC_BASE_URL=http://localhost:3000

# Optional: use sandbox for testing
# FREEAGENT_SANDBOX=true`}
          </pre>
          <p className="text-[#8888aa] text-xs mt-2">
            Register your app at{' '}
            <a
              href="https://dev.freeagent.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#4a7dff] hover:underline"
            >
              dev.freeagent.com
            </a>
            {' '}to get your credentials.
          </p>
        </div>
      )}

      {status?.configured && !status?.connected && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#8888aa]" />
            <span className="text-[#8888aa] text-sm">Not connected</span>
          </div>
          <button
            onClick={handleConnect}
            className="px-5 py-2.5 bg-[#00875a] text-white rounded-lg text-sm font-semibold hover:bg-[#00875a]/80 transition-colors"
          >
            Connect to FreeAgent
          </button>
        </div>
      )}

      {status?.connected && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${status.tokenValid ? 'bg-[#00d4aa]' : 'bg-[#ff6b6b]'}`} />
            <span className="text-[#e8e8f0] text-sm">
              Connected to <strong>{status.companyName}</strong>
            </span>
            {status.sandbox && (
              <span className="px-2 py-0.5 bg-[#ffd93d]/20 text-[#ffd93d] text-xs rounded font-medium">
                Sandbox
              </span>
            )}
          </div>

          {status.connectedAt && (
            <p className="text-[#8888aa] text-xs">
              Connected since {new Date(status.connectedAt).toLocaleDateString('en-GB')}
              {!status.tokenValid && ' — token expired, reconnection needed'}
            </p>
          )}

          <div className="flex gap-3 flex-wrap">
            <button
              onClick={handleSync}
              disabled={syncing || !status.tokenValid}
              className="px-5 py-2 bg-[#00d4aa] text-[#0d0d1a] rounded-lg text-sm font-semibold disabled:opacity-50 hover:bg-[#00d4aa]/80 transition-colors"
            >
              {syncing ? 'Syncing...' : 'Sync Now'}
            </button>

            {!status.tokenValid && (
              <button
                onClick={handleConnect}
                className="px-5 py-2 bg-[#4a7dff] text-white rounded-lg text-sm font-semibold hover:bg-[#4a7dff]/80 transition-colors"
              >
                Reconnect
              </button>
            )}

            <button
              onClick={handleDisconnect}
              disabled={disconnecting}
              className="px-5 py-2 bg-[#1e1e3a] text-[#ff6b6b] border border-[#ff6b6b]/30 rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-[#ff6b6b]/10 transition-colors"
            >
              {disconnecting ? 'Disconnecting...' : 'Disconnect'}
            </button>
          </div>

          {syncResult && (
            <p className={`text-xs ${syncResult.includes('success') ? 'text-[#00d4aa]' : 'text-[#ff6b6b]'}`}>
              {syncResult}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
