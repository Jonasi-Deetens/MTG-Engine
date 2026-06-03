// frontend/hooks/search/useSearchFilters.ts

import { useState, useMemo } from 'react';
import { COLORS, COLOR_NAMES, RARITY_OPTIONS, LANGUAGE_OPTIONS, CARD_TYPE_OPTIONS } from '@/lib/constants/search';

export function useSearchFilters() {
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [typeFilters, setTypeFilters] = useState<string[]>([]);
  const [setFilter, setSetFilter] = useState('');
  const [rarityFilter, setRarityFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [keywordFilter, setKeywordFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const hasActiveFilters = useMemo(() => 
    selectedColors.length > 0 || typeFilters.length > 0 || setFilter || rarityFilter || languageFilter || keywordFilter,
    [selectedColors, typeFilters, setFilter, rarityFilter, languageFilter, keywordFilter]
  );

  const toggleColor = (color: string) => {
    setSelectedColors(prev => 
      prev.includes(color) 
        ? prev.filter(c => c !== color)
        : [...prev, color]
    );
  };

  const toggleType = (type: string) => {
    setTypeFilters((prev) =>
      prev.includes(type) ? prev.filter((entry) => entry !== type) : [...prev, type]
    );
  };

  const clearFilters = () => {
    setSelectedColors([]);
    setTypeFilters([]);
    setSetFilter('');
    setRarityFilter('');
    setLanguageFilter('');
    setKeywordFilter('');
  };

  return {
    selectedColors,
    setSelectedColors,
    typeFilters,
    setTypeFilters,
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
    toggleType,
    clearFilters,
    COLORS,
    COLOR_NAMES,
    CARD_TYPE_OPTIONS,
    RARITY_OPTIONS,
    LANGUAGE_OPTIONS,
  };
}

