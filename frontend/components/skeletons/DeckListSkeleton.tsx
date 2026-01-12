// frontend/components/skeletons/DeckListSkeleton.tsx

export function DeckListSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="bg-[color:var(--theme-card-bg)] rounded-lg p-4">
          <div className="flex gap-4">
            <div className="w-20 h-28 bg-[color:var(--theme-bg-secondary)] rounded-lg animate-pulse flex-shrink-0"></div>
            <div className="flex-1 space-y-2">
              <div className="h-6 w-3/4 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="h-4 w-1/2 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="h-4 w-full bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="h-4 w-2/3 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              <div className="flex gap-2 mt-3">
                <div className="h-8 flex-1 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
                <div className="h-8 flex-1 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
                <div className="h-8 w-16 bg-[color:var(--theme-bg-secondary)] rounded animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

