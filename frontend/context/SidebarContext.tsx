'use client';

// frontend/context/SidebarContext.tsx

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SidebarContextType {
  isCollapsed: boolean;
  isExpanded: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export function SidebarProvider({ children }: { children: ReactNode }) {
  // Always start collapsed for hover-based expansion
  const [isCollapsed, setIsCollapsed] = useState(true);

  // Clear any saved state since we want hover-only behavior
  useEffect(() => {
    sessionStorage.removeItem('sidebar-collapsed');
  }, []);

  const handleSetCollapsed = (collapsed: boolean) => {
    // Always keep it collapsed (hover will handle expansion)
    setIsCollapsed(true);
  };

  return (
    <SidebarContext.Provider
      value={{
        isCollapsed,
        isExpanded: !isCollapsed,
        setIsCollapsed: handleSetCollapsed,
      }}
    >
      {children}
    </SidebarContext.Provider>
  );
}

export function useSidebar() {
  const context = useContext(SidebarContext);
  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
}

