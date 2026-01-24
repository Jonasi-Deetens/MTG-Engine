// frontend/hooks/search/useSearchFilters.ts

import { useState, useMemo } from 'react';
import { COLORS, COLOR_NAMES, RARITY_OPTIONS, LANGUAGE_OPTIONS } from '@/lib/constants/search';

export function useSearchFilters() {
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState('');
  const [setFilter, setSetFilter] = useState('');
  const [rarityFilter, setRarityFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [keywordFilter, setKeywordFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const hasActiveFilters = useMemo(() => 
    selectedColors.length > 0 || typeFilter || setFilter || rarityFilter || languageFilter || keywordFilter,
    [selectedColors, typeFilter, setFilter, rarityFilter, languageFilter, keywordFilter]
  );

  const toggleColor = (color: string) => {
    setSelectedColors(prev => 
      prev.includes(color) 
        ? prev.filter(c => c !== color)
        : [...prev, color]
    );
  };

  const clearFilters = () => {
    setSelectedColors([]);
    setTypeFilter('');
    setSetFilter('');
    setRarityFilter('');
    setLanguageFilter('');
    setKeywordFilter('');
  };

  return {
    selectedColors,
    setSelectedColors,
    typeFilter,
    setTypeFilter,
    setFilter,
    setSetFilter,
    rarityFilter,
    setRarityFilter,
    languageFilter,
    setLanguageFilter,
    keywordFilter,
    setKeywordFilter,
    showFilters,
    setShowFilters,
    hasActiveFilters,
    toggleColor,
    clearFilters,
    COLORS,
    COLOR_NAMES,
    RARITY_OPTIONS,
    LANGUAGE_OPTIONS,
  };
}

