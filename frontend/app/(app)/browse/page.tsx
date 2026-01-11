'use client';

// frontend/app/(app)/browse/page.tsx

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function BrowsePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to search page (which now handles browse mode)
    router.replace('/search');
  }, [router]);

  return null;
}
