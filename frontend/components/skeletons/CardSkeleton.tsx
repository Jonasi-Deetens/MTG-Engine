// frontend/components/skeletons/CardSkeleton.tsx

export function CardSkeleton() {
  return (
    <div className="aspect-[63/88] bg-slate-800/50 border border-slate-700/50 rounded-lg animate-pulse">
      <div className="w-full h-full bg-slate-700/50 rounded-lg"></div>
    </div>
  );
}

export function CardGridSkeleton({ count = 12 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </>
  );
}

