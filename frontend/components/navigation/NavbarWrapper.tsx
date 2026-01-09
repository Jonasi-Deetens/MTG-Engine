'use client';

// frontend/components/navigation/NavbarWrapper.tsx

import { usePathname } from 'next/navigation';
import { TopNavbar } from './TopNavbar';

export function NavbarWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Landing page uses landing variant, all others use app variant
  const variant = pathname === '/' ? 'landing' : 'app';
  // Landing page doesn't need spacer since navbar overlays content
  const showSpacer = pathname !== '/';

  return (
    <>
      <TopNavbar variant={variant} showSpacer={showSpacer} />
      {children}
    </>
  );
}

