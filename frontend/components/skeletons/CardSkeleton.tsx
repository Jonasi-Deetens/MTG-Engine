// frontend/components/skeletons/CardSkeleton.tsx

export function CardSkeleton() {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 animate-pulse">
      <div className="aspect-[63/88] bg-slate-700 rounded mb-3"></div>
      <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
      <div className="h-3 bg-slate-700 rounded w-1/2"></div>
    </div>
  );
}

export function CardGridSkeleton({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

