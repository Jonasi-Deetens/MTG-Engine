'use client';

// frontend/components/navigation/PageBackground.tsx

import { usePathname } from 'next/navigation';
import { useThemeImage } from '@/hooks/useThemeImage';

export function PageBackground({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  // Landing page handles its own background, skip it here
  const isLandingPage = pathname === '/';
  
  // Determine which background image to use based on route
  const isDashboard = pathname === '/dashboard';
  const isDecksPage = pathname?.startsWith('/decks') ?? false;
  const isMyCardsPage = pathname?.startsWith('/my-cards') ?? false;
  const isBuilderPage = pathname === '/builder';
  const isTemplatesPage = pathname === '/templates';
  const isSearchPage = pathname === '/search';
  const isLoginPage = pathname === '/login';
  const isRegisterPage = pathname === '/register';
  
  const dashboardBackgroundImage = useThemeImage('dashboard');
  const decksBackgroundImage = useThemeImage('decks');
  const collectionBackgroundImage = useThemeImage('collection');
  const builderBackgroundImage = useThemeImage('builder');
  const templatesBackgroundImage = useThemeImage('templates');
  const searchBackgroundImage = useThemeImage('search');
  const loginBackgroundImage = useThemeImage('login');
  const registerBackgroundImage = useThemeImage('register');
  
  const getBackgroundStyle = (): React.CSSProperties => {
    // Landing page handles its own background
    if (isLandingPage) {
      return {
        backgroundColor: 'transparent',
      };
    }
    if (isDashboard) {
      return {
        backgroundImage: `url('${dashboardBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isDecksPage) {
      return {
        backgroundImage: `url('${decksBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isMyCardsPage) {
      return {
        backgroundImage: `url('${collectionBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isBuilderPage) {
      return {
        backgroundImage: `url('${builderBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isTemplatesPage) {
      return {
        backgroundImage: `url('${templatesBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isSearchPage) {
      return {
        backgroundImage: `url('${searchBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isLoginPage) {
      return {
        backgroundImage: `url('${loginBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isRegisterPage) {
      return {
        backgroundImage: `url('${registerBackgroundImage}')`,
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
  
  // Login and register pages should be fixed height like landing page
  const isFixedHeightPage = isLandingPage || isLoginPage || isRegisterPage;
  
  return (
    <div 
      className={`${isFixedHeightPage ? 'h-screen overflow-hidden' : 'min-h-screen overflow-x-hidden'} relative`}
      style={getBackgroundStyle()}
    >
      {children}
    </div>
  );
}

