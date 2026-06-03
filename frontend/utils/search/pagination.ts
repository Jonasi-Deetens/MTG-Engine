// frontend/utils/search/pagination.ts

import { PAGE_SIZE } from '@/lib/constants/search';

/**
 * Calculate pagination info for filtered results
 */
export function calculatePagination(filteredCount: number, currentPage: number) {
  const totalPages = Math.ceil(filteredCount / PAGE_SIZE);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const endIndex = startIndex + PAGE_SIZE;
  const paginatedCards = filteredCount > 0 ? filteredCount : 0;
  const hasMore = endIndex < filteredCount;

  return {
    totalPages,
    startIndex,
    endIndex,
    paginatedCards,
    hasMore,
  };
}

