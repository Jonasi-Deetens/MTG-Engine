'use client';

// frontend/app/(protected)/my-cards/collections/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { collections, CollectionResponse } from '@/lib/collections';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Folder } from 'lucide-react';
import Link from 'next/link';

export default function CollectionsPage() {
  const router = useRouter();
  const [collectionsList, setCollectionsList] = useState<CollectionResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDesc, setNewCollectionDesc] = useState('');
  const [creating, setCreating] = useState(false);

  const loadCollections = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await collections.getCollections();
      setCollectionsList(response);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to load collections');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCollections();
  }, []);

  const handleCreate = async () => {
    if (!newCollectionName.trim()) {
      alert('Please enter a collection name');
      return;
    }

    setCreating(true);
    try {
      const newCollection = await collections.createCollection({
        name: newCollectionName,
        description: newCollectionDesc || undefined,
      });
      setCollectionsList([...collectionsList, newCollection]);
      setNewCollectionName('');
      setNewCollectionDesc('');
      setShowCreateForm(false);
      router.push(`/my-cards/collections/${newCollection.id}`);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to create collection');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await collections.deleteCollection(id);
      setCollectionsList(collectionsList.filter(c => c.id !== id));
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to delete collection');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/my-cards" className="text-[color:var(--theme-text-secondary)] hover:text-amber-600 transition-colors mb-2 inline-block">
            ← Back to My Cards
          </Link>
          <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
            Collections
          </h1>
          <p className="text-[color:var(--theme-text-secondary)]">
            Organize your cards into collections
          </p>
        </div>
        <Button
          onClick={() => setShowCreateForm(!showCreateForm)}
          variant="primary"
        >
          {showCreateForm ? 'Cancel' : 'New Collection'}
        </Button>
      </div>

      {showCreateForm && (
        <Card variant="elevated">
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Collection Name *
              </label>
              <input
                type="text"
                value={newCollectionName}
                onChange={(e) => setNewCollectionName(e.target.value)}
                placeholder="e.g., My Commander Deck"
                className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Description (optional)
              </label>
              <textarea
                value={newCollectionDesc}
                onChange={(e) => setNewCollectionDesc(e.target.value)}
                placeholder="Describe this collection..."
                rows={3}
                className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
            </div>
            <Button
              onClick={handleCreate}
              disabled={creating || !newCollectionName.trim()}
              variant="primary"
            >
              {creating ? 'Creating...' : 'Create Collection'}
            </Button>
          </div>
        </Card>
      )}

      {error && (
        <div className="p-4 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)]">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto"></div>
        </div>
      ) : collectionsList.length === 0 && !showCreateForm ? (
        <Card variant="elevated">
          <EmptyState
            icon={Folder}
            title="No collections yet"
            description="Create collections to organize your cards into groups. Perfect for organizing by format, theme, or any other category you prefer."
            actionLabel="Create Collection"
            onAction={() => setShowCreateForm(true)}
          />
        </Card>
      ) : collectionsList.length === 0 ? null : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {collectionsList.map((collection) => (
            <Card key={collection.id} variant="elevated">
              <div className="p-6 space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-[color:var(--theme-text-primary)] mb-1">
                    {collection.name}
                  </h3>
                  {collection.description && (
                    <p className="text-[color:var(--theme-text-secondary)] text-sm">
                      {collection.description}
                    </p>
                  )}
                  <p className="text-[color:var(--theme-text-muted)] text-sm mt-2">
                    {collection.card_count} card{collection.card_count !== 1 ? 's' : ''}
                  </p>
                </div>
                <div className="flex gap-2 pt-4 border-t border-[color:var(--theme-border-default)]">
                  <Link href={`/my-cards/collections/${collection.id}`} className="flex-1">
                    <Button variant="primary" size="sm" className="w-full">
                      View
                    </Button>
                  </Link>
                  <Button
                    onClick={() => handleDelete(collection.id, collection.name)}
                    variant="outline"
                    size="sm"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

