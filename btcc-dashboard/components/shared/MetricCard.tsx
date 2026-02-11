'use client';

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  variance?: string;
  varianceType?: 'positive' | 'negative' | 'neutral';
  progress?: number;
}

export default function MetricCard({ title, value, subtitle, variance, varianceType = 'neutral', progress }: MetricCardProps) {
  const varianceColors = {
    positive: 'text-[#00d4aa]',
    negative: 'text-[#ff6b6b]',
    neutral: 'text-[#8888aa]',
  };

  return (
    <div className="bg-[#141428] border border-[#2a2a4a] rounded-xl p-5">
      <p className="text-[#8888aa] text-xs uppercase tracking-wider mb-1">{title}</p>
      <p className="text-[#e8e8f0] text-2xl font-mono font-bold">{value}</p>
      {subtitle && <p className="text-[#8888aa] text-xs mt-1">{subtitle}</p>}
      {variance && (
        <p className={`text-sm font-mono mt-1 ${varianceColors[varianceType]}`}>
          {variance}
        </p>
      )}
      {progress !== undefined && (
        <div className="mt-3">
          <div className="w-full bg-[#1e1e3a] rounded-full h-2">
            <div
              className="bg-[#00d4aa] h-2 rounded-full transition-all"
              style={{ width: `${Math.min(100, progress)}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
