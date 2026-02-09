'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import FreeAgentConnection from '@/components/Settings/FreeAgentConnection';
import CategoryMappingEditor from '@/components/Settings/CategoryMappingEditor';

function SettingsContent() {
  const searchParams = useSearchParams();
  const connected = searchParams.get('connected');
  const error = searchParams.get('error');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#e8e8f0]">Settings</h1>
        <p className="text-[#8888aa] text-sm">Manage your FreeAgent connection and data sync</p>
      </div>

      {connected === 'true' && (
        <div className="bg-[#00d4aa]/10 border border-[#00d4aa]/30 rounded-lg px-4 py-3">
          <p className="text-[#00d4aa] text-sm font-medium">
            Successfully connected to FreeAgent! You can now sync your actual figures.
          </p>
        </div>
      )}

      {error && (
        <div className="bg-[#ff6b6b]/10 border border-[#ff6b6b]/30 rounded-lg px-4 py-3">
          <p className="text-[#ff6b6b] text-sm font-medium">
            Connection failed: {error === 'no_code' ? 'No authorization code received' : error === 'token_exchange_failed' ? 'Token exchange failed' : error}
          </p>
        </div>
      )}

      <FreeAgentConnection />
      <CategoryMappingEditor />
    </div>
  );
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="text-[#8888aa]">Loading settings...</div>}>
      <SettingsContent />
    </Suspense>
  );
}
