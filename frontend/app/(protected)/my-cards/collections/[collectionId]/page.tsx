'use client';

// frontend/app/(protected)/my-cards/collections/[collectionId]/page.tsx

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { collections, CollectionDetailResponse } from '@/lib/collections';
import { CardGrid } from '@/components/cards/CardGrid';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { CardData } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

export default function CollectionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const collectionId = parseInt(params.collectionId as string);
  
  const [collection, setCollection] = useState<CollectionDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadCollection = async () => {
      if (isNaN(collectionId)) return;
      
      setLoading(true);
      setError('');
      try {
        const data = await collections.getCollection(collectionId);
        setCollection(data);
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Failed to load collection');
      } finally {
        setLoading(false);
      }
    };

    loadCollection();
  }, [collectionId]);

  const handleRemoveCard = async (cardId: string) => {
    if (!confirm('Remove this card from the collection?')) return;

    try {
      await collections.removeCardFromCollection(collectionId, cardId);
      if (collection) {
        setCollection({
          ...collection,
          cards: collection.cards.filter(c => c.card_id !== cardId),
          card_count: collection.card_count - 1,
        });
      }
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to remove card');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[color:var(--theme-bg-primary)] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--theme-accent-primary)]"></div>
      </div>
    );
  }

  if (error || !collection) {
    return (
      <div className="min-h-screen bg-[color:var(--theme-bg-primary)] p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg p-6 text-[color:var(--theme-status-error)]">
            <h1 className="text-2xl font-bold mb-2">Error</h1>
            <p>{error || 'Collection not found'}</p>
            <Link href="/my-cards/collections">
              <Button variant="outline" className="mt-4">
                Back to Collections
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/my-cards/collections" className="text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-accent-primary)] transition-colors mb-2 inline-block">
          ← Back to Collections
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
              {collection.name}
            </h1>
            {collection.description && (
              <p className="text-[color:var(--theme-text-secondary)] mb-2">{collection.description}</p>
            )}
            <p className="text-[color:var(--theme-text-muted)] text-sm">
              {collection.card_count} card{collection.card_count !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      </div>

      {collection.cards.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-[color:var(--theme-text-secondary)] text-lg">This collection is empty</p>
          <p className="text-[color:var(--theme-text-muted)] text-sm mt-2">
            Add cards to this collection from card detail pages
          </p>
        </div>
      ) : (
        <CardGrid cards={collection.cards} />
      )}
    </div>
  );
}

