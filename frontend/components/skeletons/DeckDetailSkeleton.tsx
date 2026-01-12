// frontend/components/skeletons/DeckDetailSkeleton.tsx

import { CardGridSkeleton } from './CardSkeleton';

export function DeckDetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="h-9 w-32 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-2"></div>
          <div className="h-10 w-64 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-2"></div>
          <div className="h-6 w-96 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-2"></div>
          <div className="flex gap-4">
            <div className="h-5 w-24 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
            <div className="h-5 w-20 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
          </div>
        </div>
        <div className="flex gap-2">
          <div className="h-10 w-24 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
          <div className="h-10 w-20 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Skeleton */}
        <div className="lg:col-span-2 space-y-6">
          {/* Commanders Skeleton */}
          <div className="bg-[color:var(--theme-card-bg)] rounded-lg p-6">
            <div className="h-7 w-32 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-4"></div>
            <div className="flex gap-4">
              <div className="w-48 aspect-[63/88] bg-[color:var(--theme-bg-secondary)] rounded-xl animate-pulse"></div>
              <div className="w-48 aspect-[63/88] bg-[color:var(--theme-bg-secondary)] rounded-xl animate-pulse"></div>
            </div>
          </div>

          {/* Deck List Skeleton */}
          <div className="bg-[color:var(--theme-card-bg)] rounded-lg p-6">
            <div className="h-7 w-48 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-4"></div>
            <CardGridSkeleton count={12} />
          </div>
        </div>

        {/* Sidebar Skeleton */}
        <div className="space-y-6">
          <div className="bg-[color:var(--theme-card-bg)] rounded-lg p-6">
            <div className="h-7 w-32 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-4"></div>
            <div className="space-y-3">
              <div className="h-4 w-full bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="h-4 w-3/4 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="h-4 w-5/6 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
            </div>
          </div>
          <div className="bg-[color:var(--theme-card-bg)] rounded-lg p-6">
            <div className="h-7 w-40 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-4"></div>
            <div className="h-32 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
          </div>
        </div>
      </div>
    </div>
  );
}

