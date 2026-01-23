'use client';

// frontend/components/layout/RootChrome.tsx

import { usePathname } from 'next/navigation';
import { AppShell } from '@/components/layout/AppShell';
import { PageBackground } from '@/components/navigation/PageBackground';
import { TopNavbar } from '@/components/navigation/TopNavbar';

interface RootChromeProps {
  children: React.ReactNode;
}

export function RootChrome({ children }: RootChromeProps) {
  const pathname = usePathname();
  const isRootPage = pathname === '/';
  const isAuthPage = pathname === '/login' || pathname === '/register';
  const isSpacerHidden = isRootPage || isAuthPage;
  const shouldUseAppShell = !isRootPage && !isAuthPage;

  return (
    <PageBackground>
      <TopNavbar variant="app" showSpacer={!isSpacerHidden} />
      {shouldUseAppShell ? <AppShell>{children}</AppShell> : children}
    </PageBackground>
  );
}

