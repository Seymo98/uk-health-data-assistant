import type { Metadata } from "next";
import Navigation from "@/components/shared/Navigation";
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/600.css';
import '@fontsource/dm-sans/700.css';
import '@fontsource/jetbrains-mono/400.css';
import '@fontsource/jetbrains-mono/500.css';
import '@fontsource/jetbrains-mono/700.css';
import "./globals.css";

export const metadata: Metadata = {
  title: "BTCC Treasurer Dashboard",
  description: "Barrow Town Cricket Club — Budget vs Actual Financial Tracker 2025/26",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#0d0d1a] text-[#e8e8f0] min-h-screen" style={{ fontFamily: "'DM Sans', sans-serif" }}>
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
      </body>
    </html>
  );
}
