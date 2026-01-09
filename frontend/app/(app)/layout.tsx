'use client';

// frontend/app/(app)/layout.tsx

import { SidebarProvider } from '@/context/SidebarContext';
import { Sidebar } from '@/components/navigation/Sidebar';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider>
      <div className="min-h-screen bg-slate-900 overflow-x-hidden">
        {/* Sidebar - Fixed position, overlays content */}
        <Sidebar />

        {/* Main Content - Fixed margin for collapsed sidebar (expanded sidebar overlays) */}
        <main className="min-h-screen overflow-x-hidden md:ml-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-16 md:pt-8">
            {children}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}

