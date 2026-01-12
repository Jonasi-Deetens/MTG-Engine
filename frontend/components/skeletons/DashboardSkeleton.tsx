// frontend/components/skeletons/DashboardSkeleton.tsx

export function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      {/* Welcome Section Skeleton */}
      <div>
        <div className="h-10 w-64 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse mb-2"></div>
        <div className="h-6 w-96 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse"></div>
      </div>

      {/* Quick Stats Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="bg-[color:var(--theme-card-bg)] rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="h-4 w-20 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="w-10 h-10 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse"></div>
            </div>
            <div className="h-10 w-16 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-4"></div>
            <div className="space-y-2">
              <div className="h-9 w-full bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="h-9 w-full bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions Skeleton */}
      <div>
        <div className="h-8 w-32 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse mb-4"></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-[color:var(--theme-card-bg)] rounded-lg p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse"></div>
                <div className="flex-1">
                  <div className="h-5 w-24 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse mb-2"></div>
                  <div className="h-4 w-32 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Decks Skeleton */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="h-8 w-32 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse"></div>
          <div className="h-9 w-24 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-[color:var(--theme-card-bg)] rounded-lg p-4">
              <div className="flex gap-4">
                <div className="w-20 h-28 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse flex-shrink-0"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-6 w-3/4 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
                  <div className="h-4 w-1/2 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
                  <div className="h-4 w-full bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
                  <div className="h-4 w-2/3 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Featured Cards Skeleton */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="h-8 w-40 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse"></div>
          <div className="h-9 w-28 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex justify-center">
              <div className="w-48 aspect-[63/88] bg-[color:var(--theme-bg-secondary)] rounded-xl animate-pulse"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

