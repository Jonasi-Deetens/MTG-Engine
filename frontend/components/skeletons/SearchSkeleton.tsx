// frontend/components/skeletons/SearchSkeleton.tsx

export function SearchSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-12 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse"></div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="bg-[color:var(--theme-card-bg)] rounded-lg p-4">
            <div className="aspect-[63/88] bg-[color:var(--theme-bg-secondary)] rounded mb-3 animate-pulse"></div>
            <div className="h-4 bg-[color:var(--theme-bg-secondary)] rounded w-3/4 mb-2 animate-pulse"></div>
            <div className="h-3 bg-[color:var(--theme-bg-secondary)] rounded w-1/2 animate-pulse"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

