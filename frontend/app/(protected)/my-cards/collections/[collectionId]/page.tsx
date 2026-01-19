'use client';

// frontend/app/(protected)/my-cards/collections/[collectionId]/page.tsx

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { collections, CollectionDetailResponse, CollectionCardResponse } from '@/lib/collections';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { CardPreview } from '@/components/cards/CardPreview';
import { isEditableTarget } from '@/context/ShortcutContext';

export default function CollectionDetailPage() {
  const params = useParams();
  const collectionId = parseInt(params.collectionId as string);
  
  const [collection, setCollection] = useState<CollectionDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [focusedCardId, setFocusedCardId] = useState<string | null>(null);

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

  const handleUpdateQuantity = async (cardId: string, quantity: number) => {
    try {
      await collections.updateCollectionCardQuantity(collectionId, cardId, quantity);
      if (!collection) return;
      const existing = collection.cards.find((card) => card.card_id === cardId);
      const existingQuantity = existing?.quantity ?? 0;
      if (quantity <= 0) {
        setCollection({
          ...collection,
          cards: collection.cards.filter((card) => card.card_id !== cardId),
          card_count: Math.max(0, collection.card_count - existingQuantity),
        });
        return;
      }
      setCollection({
        ...collection,
        cards: collection.cards.map((card) =>
          card.card_id === cardId ? { ...card, quantity } : card
        ),
        card_count: collection.cards.reduce((sum, card) => {
          if (card.card_id === cardId) return sum + quantity;
          return sum + card.quantity;
        }, 0),
      });
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to update quantity');
    }
  };

  const handleRemoveCard = async (cardId: string) => {
    if (!confirm('Remove this card from the collection?')) return;
    await handleUpdateQuantity(cardId, 0);
  };

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.isComposing) return;
      if (isEditableTarget(e.target)) return;
      if (!focusedCardId || !collection) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      const focused = collection.cards.find((card) => card.card_id === focusedCardId);
      if (!focused) return;

      const key = e.key.toLowerCase();
      if (key === 'o') {
        e.preventDefault();
        e.stopPropagation();
        handleUpdateQuantity(focused.card_id, focused.quantity > 0 ? 0 : 1);
        return;
      }

      if (key === '+' || key === '=') {
        e.preventDefault();
        e.stopPropagation();
        handleUpdateQuantity(focused.card_id, focused.quantity + 1);
        return;
      }

      if (key === '-' || key === '_') {
        e.preventDefault();
        e.stopPropagation();
        handleUpdateQuantity(focused.card_id, Math.max(0, focused.quantity - 1));
      }
    };

    window.addEventListener('keydown', onKeyDown, { passive: false });
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [collection, focusedCardId, collectionId]);

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
              {collection.card_count} card{collection.card_count !== 1 ? 's' : ''} owned
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
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {collection.cards.map((entry: CollectionCardResponse) => (
            <div
              key={entry.card_id}
              className="group relative"
              onMouseEnter={() => setFocusedCardId(entry.card_id)}
              onMouseLeave={() => setFocusedCardId((prev) => (prev === entry.card_id ? null : prev))}
            >
              <CardPreview card={entry.card} />
              <div className="absolute top-2 left-2 rounded bg-[color:var(--theme-bg-secondary)]/90 px-2 py-0.5 text-xs text-[color:var(--theme-text-primary)] shadow">
                {entry.quantity}x
              </div>
              <div className="absolute bottom-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleUpdateQuantity(entry.card_id, entry.quantity - 1)}
                  disabled={entry.quantity <= 0}
                  className="w-7 h-7 rounded bg-[color:var(--theme-bg-secondary)]/90 text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)] disabled:opacity-50"
                  title="Decrease quantity"
                >
                  −
                </button>
                <button
                  onClick={() => handleUpdateQuantity(entry.card_id, entry.quantity + 1)}
                  className="w-7 h-7 rounded bg-[color:var(--theme-bg-secondary)]/90 text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)]"
                  title="Increase quantity"
                >
                  +
                </button>
                <button
                  onClick={() => handleRemoveCard(entry.card_id)}
                  className="w-7 h-7 rounded bg-[color:var(--theme-status-error)]/80 text-white hover:bg-[color:var(--theme-status-error)]"
                  title="Remove from collection"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

