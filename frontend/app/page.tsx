'use client';

// frontend/app/page.tsx

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { LandingSearchBar } from '@/components/landing/LandingSearchBar';
import { LandingActionCards } from '@/components/landing/LandingActionCards';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleSearch = (query: string) => {
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };


  return (
    <div
      className="h-screen flex flex-col overflow-hidden relative"
      style={{
        backgroundImage: "url('/home.png')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Dark overlay for readability */}
      <div className="absolute inset-0 bg-black/40" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Top Section: Search Bar */}
        <div className="flex-1 flex flex-col items-center justify-center pt-6 pb-4">
          <div className="text-center mb-6">
            <h1 className="font-heading text-4xl sm:text-5xl font-bold text-white mb-2 drop-shadow-lg">
              MTG Engine
            </h1>
            <p className="text-lg text-white/90 drop-shadow">
              Search and explore Magic: The Gathering cards
            </p>
          </div>
          <LandingSearchBar 
            searchQuery={searchQuery} 
            onSearchChange={setSearchQuery}
            onSearch={handleSearch}
          />
        </div>

        {/* Bottom Section: Action Cards */}
        <div className="flex-shrink-0 pt-4">
          <LandingActionCards />
        </div>
      </div>
    </div>
  );
}
