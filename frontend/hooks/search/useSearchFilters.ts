// frontend/hooks/search/useSearchFilters.ts

import { useState, useMemo } from 'react';
import { COLORS, COLOR_NAMES } from '@/lib/constants/search';

export function useSearchFilters() {
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState('');
  const [setFilter, setSetFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const hasActiveFilters = useMemo(() => 
    selectedColors.length > 0 || typeFilter || setFilter,
    [selectedColors, typeFilter, setFilter]
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
  };

  return {
    selectedColors,
    setSelectedColors,
    typeFilter,
    setTypeFilter,
    setFilter,
    setSetFilter,
    showFilters,
    setShowFilters,
    hasActiveFilters,
    toggleColor,
    clearFilters,
    COLORS,
    COLOR_NAMES,
  };
}

