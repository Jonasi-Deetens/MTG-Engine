'use client';

// frontend/app/cards/[card_id]/page.tsx

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { cards } from '@/lib/api';
import { abilities } from '@/lib/abilities';
import { CardData } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import { CardVersionSelector } from '@/components/cards/CardVersionSelector';
import { FavoriteButton } from '@/components/collections/FavoriteButton';
import { AddToCollectionButton } from '@/components/collections/AddToCollectionButton';
import { useBuilderStore } from '@/store/builderStore';
import { AbilityTreeView } from '@/components/builder/AbilityTreeView';
import { RarityBadge } from '@/components/ui/RarityBadge';
import { LegalityDisplay } from '@/components/cards/LegalityDisplay';
import { useAuth } from '@/context/AuthContext';

export default function CardDetailPage() {
  const params = useParams();
  const router = useRouter();
  const cardId = params.card_id as string;
  const { loadFromGraph } = useBuilderStore();
  const { isAuthenticated } = useAuth();
  
  const [card, setCard] = useState<CardData | null>(null);
  const [allVersions, setAllVersions] = useState<CardData[]>([]);
  const [abilityGraph, setAbilityGraph] = useState<any>(null);
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
            const graph = await abilities.getCardGraph(cardId);
            if (graph && graph.ability_graph) {
              setAbilityGraph(graph.ability_graph);
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
    if (abilityGraph) {
      const json = JSON.stringify(abilityGraph, null, 2);
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
    return (
      <div className="min-h-screen bg-angel-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  if (error || !card) {
    return (
      <div className="min-h-screen bg-angel-white p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-900/50 border border-red-600 rounded-lg p-6 text-red-200">
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
        <div className="flex items-center justify-between">
          <Link href="/search" className="text-slate-600 hover:text-amber-600 transition-colors">
            ← Back to Search
          </Link>
          <div className="flex items-center gap-2">
            <Button onClick={handleShare} variant="outline" size="sm">
              Share
            </Button>
            {isAuthenticated && (
              <>
                <AddToCollectionButton cardId={card.card_id} />
                <Button onClick={handleEditInBuilder} variant="primary" size="sm">
                  Edit in Builder
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Main Card Info */}
        <div className="bg-white border border-amber-200/50 rounded-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card Image */}
            <div className="md:col-span-1">
              {imageUrl ? (
                <div className="aspect-[63/88] relative rounded-xl overflow-hidden">
                  <Image
                    src={imageUrl}
                    alt={card.name}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, 33vw"
                    unoptimized
                  />
                </div>
              ) : (
                <div className="aspect-[63/88] flex items-center justify-center bg-amber-50 border border-amber-200/50 rounded-xl text-slate-500">
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
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-2">
                    <h1 className="text-3xl font-bold text-slate-900">{card.name}</h1>
                    {card.rarity && <RarityBadge rarity={card.rarity} />}
                  </div>
                  {card.mana_cost && (
                    <p className="text-xl font-mono text-amber-400">{card.mana_cost}</p>
                  )}
                </div>
                {isAuthenticated && <FavoriteButton cardId={card.card_id} size="lg" />}
              </div>

              {card.type_line && (
                <div>
                  <span className="text-xs text-slate-600 uppercase tracking-wide">Type</span>
                  <p className="text-base text-slate-900 mt-1">{card.type_line}</p>
                </div>
              )}

              {(card.power && card.toughness) && (
                <div>
                  <span className="text-xs text-slate-600 uppercase tracking-wide">Power / Toughness</span>
                  <p className="text-base text-slate-900 mt-1 font-mono">
                    {card.power} / {card.toughness}
                  </p>
                </div>
              )}

              {card.colors && card.colors.length > 0 && (
                <div>
                  <span className="text-xs text-slate-600 uppercase tracking-wide">Colors</span>
                  <div className="flex gap-2 mt-1">
                    {card.colors.map((color, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 rounded text-sm font-medium bg-amber-100 text-slate-900 capitalize border border-amber-200/50"
                      >
                        {color}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {card.oracle_text && (
                <div>
                  <span className="text-xs text-slate-600 uppercase tracking-wide">Oracle Text</span>
                  <p className="text-base text-slate-800 mt-1 whitespace-pre-wrap leading-relaxed">
                    {card.oracle_text}
                  </p>
                </div>
              )}

              {card.flavor_text && (
                <div>
                  <span className="text-xs text-slate-600 uppercase tracking-wide">Flavor Text</span>
                  <p className="text-base text-slate-700 mt-1 italic leading-relaxed">
                    {card.flavor_text}
                  </p>
                </div>
              )}

              {card.prices && (card.prices.usd || card.prices.eur || card.prices.usd_foil) && (
                <div>
                  <span className="text-xs text-slate-600 uppercase tracking-wide">Prices</span>
                  <div className="flex flex-wrap gap-4 mt-1">
                    {card.prices.usd && (
                      <div>
                        <span className="text-sm text-slate-600">USD:</span>{' '}
                        <span className="text-base text-amber-600 font-semibold">
                          ${parseFloat(card.prices.usd).toFixed(2)}
                        </span>
                      </div>
                    )}
                    {card.prices.usd_foil && (
                      <div>
                        <span className="text-sm text-slate-600">USD Foil:</span>{' '}
                        <span className="text-base text-amber-600 font-semibold">
                          ${parseFloat(card.prices.usd_foil).toFixed(2)}
                        </span>
                      </div>
                    )}
                    {card.prices.eur && (
                      <div>
                        <span className="text-sm text-slate-600">EUR:</span>{' '}
                        <span className="text-base text-amber-600 font-semibold">
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
                  <span className="text-xs text-slate-600 uppercase tracking-wide">Artist</span>
                  <p className="text-base text-slate-700 mt-1">{card.artist}</p>
                </div>
              )}

              {(card.set_code || card.collector_number) && (
                <div className="flex gap-4 text-sm text-slate-600">
                  {card.set_code && (
                    <div>
                      <span className="uppercase tracking-wide">Set:</span>{' '}
                      <span className="text-slate-800">{card.set_code.toUpperCase()}</span>
                    </div>
                  )}
                  {card.collector_number && (
                    <div>
                      <span className="uppercase tracking-wide">#:</span>{' '}
                      <span className="text-slate-800">{card.collector_number}</span>
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
              <div className="bg-white border border-amber-200/50 rounded-lg p-6">
                <div className="text-center text-slate-600">Loading ability graph...</div>
              </div>
            ) : abilityGraph ? (
              <div className="bg-white border border-amber-200/50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-slate-900">Saved Ability Graph</h2>
                  <div className="flex items-center gap-2">
                    <Button onClick={handleExportGraph} variant="outline" size="sm">
                      Export JSON
                    </Button>
                    <Button onClick={handleEditInBuilder} variant="secondary" size="sm">
                      Edit Graph
                    </Button>
                  </div>
                </div>
                <div className="bg-amber-50 border border-amber-200/50 rounded-lg p-4">
                  <AbilityTreeView />
                </div>
              </div>
            ) : (
              <div className="bg-white border border-amber-200/50 rounded-lg p-6">
                <div className="text-center space-y-4">
                  <p className="text-slate-600">No ability graph saved for this card yet.</p>
                  <Button onClick={handleEditInBuilder} variant="primary">
                    Create Ability Graph
                  </Button>
                </div>
              </div>
            )}
          </>
        )}

        {/* All Versions Section */}
        {allVersions.length > 1 && (
          <div className="bg-white border border-amber-200/50 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">
              All Printings ({allVersions.length})
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {allVersions.map((version) => (
                <Link
                  key={version.card_id}
                  href={`/cards/${version.card_id}`}
                  className={`aspect-[63/88] relative rounded-lg overflow-hidden transition-all ${
                    version.card_id === card.card_id
                      ? 'ring-2 ring-amber-500'
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
                    <div className="w-full h-full flex items-center justify-center bg-amber-50 border border-amber-200/50 text-slate-500 text-xs">
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

