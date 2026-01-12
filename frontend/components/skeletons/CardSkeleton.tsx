// frontend/components/skeletons/CardSkeleton.tsx

export function CardSkeleton() {
  return (
    <div className="aspect-[63/88] bg-[color:var(--theme-bg-secondary)] rounded-xl animate-pulse overflow-hidden">
      <div className="w-full h-full bg-[color:var(--theme-bg-secondary)] rounded-xl"></div>
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

