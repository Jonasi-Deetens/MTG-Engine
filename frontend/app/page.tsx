'use client';

// frontend/app/page.tsx

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { LandingSearchBar } from '@/components/landing/LandingSearchBar';
import { useThemeImage } from '@/hooks/useThemeImage';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const backgroundImage = useThemeImage('home');

  const handleSearch = (query: string) => {
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div
      className="h-screen flex flex-col relative overflow-hidden"
      style={{
        backgroundImage: `url('${backgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Light overlay for readability */}
      <div className="absolute inset-0 bg-black/10" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Search Bar - Centered */}
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="text-center mb-8">
            <h1 className="font-heading text-4xl sm:text-5xl font-bold text-white mb-3 drop-shadow-lg">
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
      </div>
    </div>
  );
}
