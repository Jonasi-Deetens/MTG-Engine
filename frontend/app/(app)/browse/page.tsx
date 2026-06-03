'use client';

// frontend/app/(app)/browse/page.tsx

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function BrowsePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/search');
  }, [router]);

  return null;
}
