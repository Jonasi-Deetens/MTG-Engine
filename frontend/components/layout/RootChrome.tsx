'use client';

// frontend/components/layout/RootChrome.tsx

import { usePathname } from 'next/navigation';
import { AppShell } from '@/components/layout/AppShell';
import { PageBackground } from '@/components/navigation/PageBackground';
import { TopNavbar } from '@/components/navigation/TopNavbar';
import { NierHeader } from '@/components/navigation/NierHeader';
import { useTheme } from '@/context/ThemeContext';

interface RootChromeProps {
  children: React.ReactNode;
}

export function RootChrome({ children }: RootChromeProps) {
  const pathname = usePathname();
  const { currentTheme } = useTheme();
  const isRootPage = pathname === '/';
  const isAuthPage = pathname === '/login' || pathname === '/register';
  const isPlayPage = pathname?.startsWith('/play');
  const isSpacerHidden = isRootPage || isAuthPage;
  const shouldUseAppShell = !isRootPage && !isAuthPage;
  const showNierHeader = currentTheme === 'nier';

  return (
    <PageBackground>
      {!isPlayPage &&
        (showNierHeader ? (
          <NierHeader showSpacer={!isSpacerHidden} />
        ) : (
          <TopNavbar variant="app" showSpacer={!isSpacerHidden} />
        ))}
      {shouldUseAppShell ? <AppShell>{children}</AppShell> : children}
    </PageBackground>
  );
}

