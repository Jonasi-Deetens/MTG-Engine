'use client';

// frontend/components/collections/AddToCollectionButton.tsx

import { useState, useEffect } from 'react';
import { collections, CollectionResponse } from '@/lib/collections';
import { Button } from '@/components/ui/Button';

interface AddToCollectionButtonProps {
  cardId: string;
  onAdded?: () => void;
}

export function AddToCollectionButton({ cardId, onAdded }: AddToCollectionButtonProps) {
  const [collectionsList, setCollectionsList] = useState<CollectionResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [adding, setAdding] = useState<number | null>(null);

  useEffect(() => {
    const loadCollections = async () => {
      try {
        const response = await collections.getCollections();
        setCollectionsList(response);
      } catch (err) {
        console.error('Failed to load collections:', err);
      }
    };
    loadCollections();
  }, []);

  const handleAdd = async (collectionId: number) => {
    setAdding(collectionId);
    try {
      await collections.addCardToCollection(collectionId, cardId);
      setShowMenu(false);
      onAdded?.();
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to add card to collection');
    } finally {
      setAdding(null);
    }
  };

  if (collectionsList.length === 0) {
    return (
      <Button
        onClick={() => window.location.href = '/my-cards/collections'}
        variant="outline"
        size="sm"
      >
        Create Collection
      </Button>
    );
  }

  return (
    <div className="relative">
      <Button
        onClick={() => setShowMenu(!showMenu)}
        variant="outline"
        size="sm"
      >
        Add to Collection
      </Button>
      
      {showMenu && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowMenu(false)}
          />
          <div className="absolute top-full mt-2 right-0 bg-slate-800 border border-slate-600 rounded-lg shadow-xl z-20 min-w-[200px]">
            <div className="p-2 max-h-64 overflow-y-auto">
              {collectionsList.map((collection) => (
                <button
                  key={collection.id}
                  onClick={() => handleAdd(collection.id)}
                  disabled={adding === collection.id}
                  className="w-full text-left px-3 py-2 text-sm text-white hover:bg-slate-700 rounded transition-colors disabled:opacity-50"
                >
                  {adding === collection.id ? 'Adding...' : collection.name}
                  <span className="text-slate-500 text-xs ml-2">
                    ({collection.card_count})
                  </span>
                </button>
              ))}
            </div>
            <div className="border-t border-slate-700 p-2">
              <button
                onClick={() => {
                  setShowMenu(false);
                  window.location.href = '/my-cards/collections';
                }}
                className="w-full text-left px-3 py-2 text-sm text-amber-400 hover:bg-slate-700 rounded transition-colors"
              >
                + New Collection
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

