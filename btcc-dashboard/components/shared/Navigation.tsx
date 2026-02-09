'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/', label: 'Dashboard' },
  { href: '/input', label: 'Data Entry' },
  { href: '/history', label: 'History' },
  { href: '/settings', label: 'Settings' },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-[#2a2a4a] bg-[#141428]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[#00d4aa] flex items-center justify-center font-bold text-[#0d0d1a] text-sm font-mono">
              BT
            </div>
            <span className="text-[#e8e8f0] font-semibold text-lg tracking-tight">
              BTCC Treasurer
            </span>
          </div>
          <div className="flex gap-1">
            {navItems.map(item => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? 'bg-[#00d4aa]/15 text-[#00d4aa]'
                      : 'text-[#8888aa] hover:text-[#e8e8f0] hover:bg-[#1e1e3a]'
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
