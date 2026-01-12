'use client';

// frontend/app/(app)/layout.tsx

import { usePathname } from 'next/navigation';
import { useThemeImage } from '@/hooks/useThemeImage';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isSearchPage = pathname === '/search';
  const searchBackgroundImage = useThemeImage('search');
  
  const getBackgroundStyle = () => {
    if (isSearchPage) {
      return {
        backgroundImage: `url('${searchBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    return {
      backgroundColor: 'var(--theme-bg-primary)',
    };
  };

  return (
    <div 
      className="min-h-screen overflow-x-hidden relative"
      style={getBackgroundStyle()}
    >
      {/* Main Content - Navbar is handled by NavbarWrapper in root layout */}
      <main className="min-h-screen relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}

