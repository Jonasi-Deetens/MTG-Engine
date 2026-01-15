'use client';

// frontend/components/navigation/NavbarWrapper.tsx

import { usePathname } from 'next/navigation';
import { TopNavbar } from './TopNavbar';
import { PageBackground } from './PageBackground';

export function NavbarWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Landing page uses landing variant, all others use app variant
  const variant = pathname === '/' ? 'landing' : 'app';
  // Landing, login, and register pages don't need spacer since navbar overlays content
  const showSpacer = pathname !== '/' && pathname !== '/login' && pathname !== '/register';

  return (
    <PageBackground>
      <TopNavbar variant={variant} showSpacer={showSpacer} />
      {children}
    </PageBackground>
  );
}

