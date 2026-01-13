'use client';

// frontend/components/ui/Pagination.tsx

import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';
import { cn } from '@/lib/utils';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  pageSize?: number;
  total?: number;
  showPageNumbers?: boolean;
  maxVisiblePages?: number;
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  pageSize = 24,
  total,
  showPageNumbers = true,
  maxVisiblePages = 7,
  className,
}: PaginationProps) {
  if (totalPages <= 1) {
    return null;
  }

  // Calculate page range to display
  const getPageNumbers = () => {
    const pages: (number | 'ellipsis')[] = [];
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is less than max
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      // Calculate start and end of middle range
      const halfVisible = Math.floor(maxVisiblePages / 2);
      let start = Math.max(2, currentPage - halfVisible);
      let end = Math.min(totalPages - 1, currentPage + halfVisible);
      
      // Adjust if we're near the start
      if (currentPage <= halfVisible + 1) {
        end = Math.min(totalPages - 1, maxVisiblePages - 1);
      }
      
      // Adjust if we're near the end
      if (currentPage >= totalPages - halfVisible) {
        start = Math.max(2, totalPages - maxVisiblePages + 2);
      }
      
      // Add ellipsis before middle range if needed
      if (start > 2) {
        pages.push('ellipsis');
      }
      
      // Add middle range
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      // Add ellipsis after middle range if needed
      if (end < totalPages - 1) {
        pages.push('ellipsis');
      }
      
      // Always show last page
      if (totalPages > 1) {
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  const pageNumbers = getPageNumbers();
  
  // Calculate "Showing X-Y of Z" text
  const startItem = total ? (currentPage - 1) * pageSize + 1 : undefined;
  const endItem = total ? Math.min(currentPage * pageSize, total) : undefined;

  return (
    <div className={cn('flex flex-col items-center gap-4', className)}>
      {/* Results info */}
      {total && startItem !== undefined && endItem !== undefined && (
        <div className="text-sm text-[color:var(--theme-text-secondary)]">
          Showing {startItem.toLocaleString()}-{endItem.toLocaleString()} of {total.toLocaleString()} cards
        </div>
      )}
      
      {/* Pagination controls */}
      <div className="flex items-center gap-2">
        {/* Previous button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="flex items-center gap-1"
        >
          <ChevronLeft className="w-4 h-4" />
          <span className="hidden sm:inline">Previous</span>
        </Button>

        {/* Page numbers */}
        {showPageNumbers && (
          <div className="flex items-center gap-1">
            {pageNumbers.map((page, index) => {
              if (page === 'ellipsis') {
                return (
                  <span
                    key={`ellipsis-${index}`}
                    className="px-2 text-[color:var(--theme-text-secondary)]"
                  >
                    ...
                  </span>
                );
              }

              const isActive = page === currentPage;
              
              return (
                <button
                  key={page}
                  onClick={() => onPageChange(page)}
                  className={cn(
                    'min-w-[2.5rem] px-3 py-1.5 text-sm font-medium rounded-lg transition-all duration-200',
                    isActive
                      ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
                      : 'bg-[color:var(--theme-card-bg)] text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] hover:text-[color:var(--theme-text-primary)] border border-[color:var(--theme-card-border)]'
                  )}
                  aria-label={`Go to page ${page}`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {page}
                </button>
              );
            })}
          </div>
        )}

        {/* Next button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="flex items-center gap-1"
        >
          <span className="hidden sm:inline">Next</span>
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}


