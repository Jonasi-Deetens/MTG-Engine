'use client';

// frontend/app/page.tsx

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { LandingSearchBar } from '@/components/landing/LandingSearchBar';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleSearch = (query: string) => {
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div className="h-screen flex flex-col relative overflow-hidden">
      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Search Bar - Centered */}
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="text-center mb-8">
            <h1
              className="font-heading text-4xl sm:text-5xl font-bold text-[color:var(--theme-text-primary)] mb-3 nier-glitch"
              data-text="MTG Simulator"
            >
              MTG Simulator
            </h1>
            <p className="text-lg text-[color:var(--theme-text-secondary)] drop-shadow">
              Search and explore Magic: The Gathering cards
            </p>
          </div>
          <LandingSearchBar 
            searchQuery={searchQuery} 
            onSearchChange={setSearchQuery}
            onSearch={handleSearch}
          />
        </div>
      </div>
    </div>
  );
}
