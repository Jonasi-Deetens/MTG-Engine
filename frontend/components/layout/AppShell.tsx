'use client';

// frontend/components/layout/AppShell.tsx

import { usePathname } from 'next/navigation';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const isDeckBuilder = pathname === '/decks/builder';
  const isPlay = pathname === '/play';

  const containerClassName = isDeckBuilder || isPlay
    ? 'w-full px-4 sm:px-6 lg:px-8 py-8'
    : 'max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8';

  return (
    <main className="min-h-screen relative z-10">
      <div className={containerClassName}>
        {children}
      </div>
    </main>
  );
}

