'use client';

// frontend/app/cards/[card_id]/page.tsx

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { cards } from '@/lib/api';
import { effects } from '@/lib/effects';
import { CardData } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import { CardVersionSelector } from '@/components/cards/CardVersionSelector';
import { FavoriteButton } from '@/features/collections/components/FavoriteButton';
import { AddToCollectionButton } from '@/features/collections/components/AddToCollectionButton';
import { EffectGraphPreview } from '@/features/builder/components/EffectGraphPreview';
import { RarityBadge } from '@/components/ui/RarityBadge';
import { LegalityDisplay } from '@/components/cards/LegalityDisplay';
import { useAuth } from '@/context/AuthContext';
import { isEditableTarget } from '@/context/ShortcutContext';
import { ArchiveSectionHeader } from '@/components/ui/ArchiveSectionHeader';
import { LoadingState } from '@/components/ui/LoadingState';

export default function CardDetailPage() {
  const params = useParams();
  const router = useRouter();
  const cardId = params.card_id as string;
  const { isAuthenticated } = useAuth();
  
  const [card, setCard] = useState<CardData | null>(null);
  const [allVersions, setAllVersions] = useState<CardData[]>([]);
  const [effectGraph, setEffectGraph] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [loadingGraph, setLoadingGraph] = useState(false);

  useEffect(() => {
    const fetchCard = async () => {
      if (!cardId) return;
      
      setLoading(true);
      setError('');
      
      try {
        // Fetch card details
        const cardData = await cards.getById(cardId);
        setCard(cardData);
        
        // Fetch all versions
        try {
          const versions = await cards.getVersions(cardId);
          setAllVersions(versions || [cardData]);
        } catch (err) {
          console.error('Failed to fetch versions:', err);
          setAllVersions([cardData]);
        }
        
        // Try to fetch saved ability graph (only if authenticated)
        if (isAuthenticated) {
          setLoadingGraph(true);
          try {
            const graph = await effects.getCardEffectGraph(cardId);
            if (graph && graph.effect_graph) {
              setEffectGraph(graph.effect_graph);
            }
          } catch (err: any) {
            // 404 is fine - no graph saved yet
            if (err.status !== 404) {
              console.error('Failed to fetch ability graph:', err);
            }
          } finally {
            setLoadingGraph(false);
          }
        }
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Failed to load card');
      } finally {
        setLoading(false);
      }
    };

    fetchCard();
  }, [cardId, isAuthenticated]);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.isComposing) return;
      if (isEditableTarget(e.target)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      if (e.key.toLowerCase() === 'g' && card) {
        e.preventDefault();
        e.stopPropagation();
        router.push(`/builder?card=${encodeURIComponent(card.card_id)}`);
      }
    };

    window.addEventListener('keydown', onKeyDown, { passive: false });
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [card, router]);

  const handleVersionChange = async (newCard: CardData) => {
    router.push(`/cards/${newCard.card_id}`);
  };

  const handleEditInBuilder = () => {
    if (card) {
      router.push(`/builder?card=${encodeURIComponent(card.card_id)}`);
    }
  };

  const handleShare = async () => {
    if (card) {
      const url = `${window.location.origin}/cards/${card.card_id}`;
      try {
        await navigator.clipboard.writeText(url);
        alert('Card link copied to clipboard!');
      } catch (err) {
        // Fallback for browsers that don't support clipboard API
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Card link copied to clipboard!');
      }
    }
  };

  const handleExportGraph = () => {
    if (effectGraph) {
      const json = JSON.stringify(effectGraph, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${card?.name || 'ability-graph'}-graph.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  if (loading) {
    return <LoadingState />;
  }

  if (error || !card) {
    return (
      <div className="min-h-screen bg-[color:var(--theme-bg-primary)] p-4">
        <div className="mx-auto">
          <div className="bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg p-6 text-[color:var(--theme-status-error)]">
            <h1 className="text-2xl font-bold mb-2">Error</h1>
            <p>{error || 'Card not found'}</p>
            <Link href="/search">
              <Button variant="outline" className="mt-4">
                Back to Search
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const imageUrl = card.image_uris?.large || card.image_uris?.normal || card.image_uris?.small;

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <Link href="/search" className="w-full sm:w-auto">
            <Button variant="outline" size="sm" className="w-full sm:w-auto">
              ← Back to Search
            </Button>
          </Link>
          <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row">
            <Button onClick={handleShare} variant="outline" size="sm" className="w-full sm:w-auto">
              Share
            </Button>
            {isAuthenticated && (
              <>
                <AddToCollectionButton cardId={card.card_id} />
                <Button onClick={handleEditInBuilder} variant="primary" size="sm" className="w-full sm:w-auto">
                  Edit in Builder
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Main Card Info */}
        <div className="ui-card border border-[color:var(--theme-card-border)] rounded-none p-4 sm:p-6" data-variant="default">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card Image */}
            <div className="md:col-span-1">
              {imageUrl ? (
                <div className="relative w-full aspect-[63/88] bg-[color:var(--theme-card-bg)] p-2">
                  <div className="card-modal-overlay" />
                  <div className="relative w-full h-full overflow-hidden">
                    <Image
                      src={imageUrl}
                      alt={card.name}
                      fill
                      className="object-cover"
                      sizes="(max-width: 768px) 100vw, 33vw"
                      unoptimized
                    />
                  </div>
                </div>
              ) : (
                <div className="aspect-[63/88] flex items-center justify-center bg-[color:var(--theme-card-hover)] border border-[color:var(--theme-card-border)] rounded-none text-[color:var(--theme-text-muted)]">
                  No Image
                </div>
              )}
              
              {/* Version Selector */}
              {allVersions.length > 1 && (
                <div className="mt-4">
                  <CardVersionSelector
                    currentCard={card}
                    allVersions={allVersions}
                    onVersionChange={handleVersionChange}
                    loading={false}
                  />
                </div>
              )}
            </div>

            {/* Card Details */}
            <div className="md:col-span-2 space-y-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-2">
                    <h1
                      className="text-3xl font-bold text-[color:var(--theme-text-primary)] nier-glitch"
                      data-text={card.name}
                    >
                      {card.name}
                    </h1>
                    {card.rarity && <RarityBadge rarity={card.rarity} />}
                  </div>
                  {card.mana_cost && (
                    <p className="text-xl font-mono text-[color:var(--theme-accent-secondary)]">{card.mana_cost}</p>
                  )}
                </div>
                {isAuthenticated && <FavoriteButton cardId={card.card_id} size="lg" />}
              </div>

              {card.type_line && (
                <div>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">Type</span>
                  <p className="text-base text-[color:var(--theme-text-primary)] mt-1">{card.type_line}</p>
                </div>
              )}

              {(card.power && card.toughness) && (
                <div>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">Power / Toughness</span>
                  <p className="text-base text-[color:var(--theme-text-primary)] mt-1 font-mono">
                    {card.power} / {card.toughness}
                  </p>
                </div>
              )}

              {card.colors && card.colors.length > 0 && (
                <div>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">Colors</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {card.colors.map((color, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 rounded-none text-xs font-mono uppercase tracking-[0.2em] bg-[color:var(--theme-card-hover)] text-[color:var(--theme-text-primary)] border border-[color:var(--theme-card-border)]"
                      >
                        {color}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {card.oracle_text && (
                <div>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">Oracle Text</span>
                  <p className="text-base text-[color:var(--theme-text-primary)] mt-1 whitespace-pre-wrap leading-relaxed">
                    {card.oracle_text}
                  </p>
                </div>
              )}

              {card.flavor_text && (
                <div>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">Flavor Text</span>
                  <p className="text-base text-[color:var(--theme-text-secondary)] mt-1 italic leading-relaxed">
                    {card.flavor_text}
                  </p>
                </div>
              )}

              {card.prices && (card.prices.usd || card.prices.eur || card.prices.usd_foil) && (
                <div>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">Prices</span>
                  <div className="flex flex-wrap gap-4 mt-1">
                    {card.prices.usd && (
                      <div>
                        <span className="text-sm text-[color:var(--theme-text-secondary)]">USD:</span>{' '}
                        <span className="text-base text-[color:var(--theme-accent-primary)] font-semibold">
                          ${parseFloat(card.prices.usd).toFixed(2)}
                        </span>
                      </div>
                    )}
                    {card.prices.usd_foil && (
                      <div>
                        <span className="text-sm text-[color:var(--theme-text-secondary)]">USD Foil:</span>{' '}
                        <span className="text-base text-[color:var(--theme-accent-primary)] font-semibold">
                          ${parseFloat(card.prices.usd_foil).toFixed(2)}
                        </span>
                      </div>
                    )}
                    {card.prices.eur && (
                      <div>
                        <span className="text-sm text-[color:var(--theme-text-secondary)]">EUR:</span>{' '}
                        <span className="text-base text-[color:var(--theme-accent-primary)] font-semibold">
                          €{parseFloat(card.prices.eur).toFixed(2)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {card.legalities && Object.keys(card.legalities).length > 0 && (
                <div>
                  <LegalityDisplay legalities={card.legalities} />
                </div>
              )}

              {card.artist && (
                <div>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">Artist</span>
                  <p className="text-base text-[color:var(--theme-text-secondary)] mt-1">{card.artist}</p>
                </div>
              )}

              {(card.set_code || card.collector_number) && (
                <div className="flex flex-wrap gap-4 text-sm text-[color:var(--theme-text-secondary)]">
                  {card.set_code && (
                    <div>
                      <span className="uppercase tracking-wide">Set:</span>{' '}
                      <span className="text-[color:var(--theme-text-primary)]">{card.set_code.toUpperCase()}</span>
                    </div>
                  )}
                  {card.collector_number && (
                    <div>
                      <span className="uppercase tracking-wide">#:</span>{' '}
                      <span className="text-[color:var(--theme-text-primary)]">{card.collector_number}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Ability Graph Section - Only show if authenticated */}
        {isAuthenticated && (
          <>
            {loadingGraph ? (
              <div className="ui-card border border-[color:var(--theme-card-border)] rounded-none p-6" data-variant="default">
                <div className="text-center text-[color:var(--theme-text-secondary)]">Loading ability graph...</div>
              </div>
            ) : effectGraph ? (
              <div className="ui-card border border-[color:var(--theme-card-border)] rounded-none p-6" data-variant="default">
                <ArchiveSectionHeader
                  title="Saved Effect Graph"
                  status="GRAPH_ARCHIVE: READY"
                  className="mb-4"
                  titleClassName="text-2xl"
                  action={
                    <>
                      <Button onClick={handleExportGraph} variant="outline" size="sm">
                        Export JSON
                      </Button>
                      <Button onClick={handleEditInBuilder} variant="secondary" size="sm">
                        Edit Effects
                      </Button>
                    </>
                  }
                />
                <div className="bg-[color:var(--theme-card-hover)] border border-[color:var(--theme-card-border)] rounded-none p-4">
                  <EffectGraphPreview graph={effectGraph} />
                </div>
              </div>
            ) : (
              <div className="ui-card border border-[color:var(--theme-card-border)] rounded-none p-6" data-variant="default">
                <div className="text-center space-y-4">
                  <p className="text-[color:var(--theme-text-secondary)]">No effect graph saved for this card yet.</p>
                  <Button onClick={handleEditInBuilder} variant="primary" size="sm" className="w-full sm:w-auto">
                    Create Effect Graph
                  </Button>
                </div>
              </div>
            )}
          </>
        )}

        {/* All Versions Section */}
        {allVersions.length > 1 && (
          <div className="ui-card border border-[color:var(--theme-card-border)] rounded-none p-6" data-variant="default">
            <ArchiveSectionHeader
              title={`All Printings (${allVersions.length})`}
              status="PRINTINGS_INDEX: READY"
              titleClassName="text-2xl"
            />
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {allVersions.map((version) => (
                <Link
                  key={version.card_id}
                  href={`/cards/${version.card_id}`}
                  className={`aspect-[63/88] relative rounded-none overflow-hidden transition-all ${
                    version.card_id === card.card_id
                      ? 'ring-2 ring-[color:var(--theme-accent-primary)]'
                      : 'hover:scale-105 hover:shadow-lg'
                  }`}
                >
                  {version.image_uris?.small ? (
                    <Image
                      src={version.image_uris.small}
                      alt={version.name}
                      fill
                      className="object-cover"
                      sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 16vw"
                      unoptimized
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-[color:var(--theme-card-hover)] border border-[color:var(--theme-card-border)] text-[color:var(--theme-text-muted)] text-xs">
                      {version.set_code?.toUpperCase()}
                    </div>
                  )}
                </Link>
              ))}
            </div>
          </div>
        )}
    </div>
  );
}

