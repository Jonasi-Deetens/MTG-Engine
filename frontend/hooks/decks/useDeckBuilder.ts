// frontend/hooks/decks/useDeckBuilder.ts

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useDeckStore } from '@/store/deckStore';
import { CardData } from '@/components/cards/CardPreview';
import { DeckDetailResponse, DeckCardResponse } from '@/lib/decks';

export function useDeckBuilder() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const deckIdParam = searchParams.get('deck');
  
  const {
    currentDeck,
    validation,
    loading,
    error,
    loadDeck,
    createDeck,
    updateDeck,
    updateCardQuantity,
    removeCard,
    addCommander,
    removeCommander,
    clearDeck,
    refreshDeck,
  } = useDeckStore();

  const [deckName, setDeckName] = useState('');
  const [deckDescription, setDeckDescription] = useState('');
  const [deckFormat, setDeckFormat] = useState('Commander');
  const [isPublic, setIsPublic] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [previewCard, setPreviewCard] = useState<DeckCardResponse | null>(null);
  const [modalCard, setModalCard] = useState<CardData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Load existing deck if deckId is provided
  useEffect(() => {
    if (deckIdParam) {
      const id = parseInt(deckIdParam);
      if (!isNaN(id)) {
        loadDeck(id);
      }
    }
    return () => clearDeck();
  }, [deckIdParam, loadDeck, clearDeck]);

  // Update form when deck loads
  useEffect(() => {
    if (currentDeck) {
      setDeckName(currentDeck.name);
      setDeckDescription(currentDeck.description || '');
      setDeckFormat(currentDeck.format);
      setIsPublic(currentDeck.is_public);
    }
  }, [currentDeck]);

  const handleSave = async () => {
    if (!deckName.trim()) {
      alert('Please enter a deck name');
      return;
    }

    setSaving(true);
    try {
      if (currentDeck) {
        await updateDeck(currentDeck.id, {
          name: deckName,
          description: deckDescription || undefined,
          format: deckFormat,
          is_public: isPublic,
        });
      } else {
        const newDeckId = await createDeck(deckName, deckFormat, deckDescription);
        router.push(`/decks/builder?deck=${newDeckId}`);
      }
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to save deck');
    } finally {
      setSaving(false);
    }
  };

  const handleQuantityChange = async (cardId: string, quantity: number) => {
    if (!currentDeck) return;
    try {
      await updateCardQuantity(currentDeck.id, cardId, quantity);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to update quantity');
    }
  };

  const handleRemoveCard = async (cardId: string) => {
    if (!currentDeck) return;
    try {
      await removeCard(currentDeck.id, cardId);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to remove card');
    }
  };

  const handleRemoveCommander = async (cardId: string) => {
    if (!currentDeck) return;
    try {
      await removeCommander(currentDeck.id, cardId);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to remove commander');
    }
  };

  const handleCardHover = (card: DeckCardResponse | null) => {
    if (card) setPreviewCard(card);
  };

  return {
    // State
    currentDeck,
    validation,
    loading,
    error,
    deckName,
    deckDescription,
    deckFormat,
    isPublic,
    saving,
    showImport,
    previewCard,
    modalCard,
    isModalOpen,
    
    // Setters
    setDeckName,
    setDeckDescription,
    setDeckFormat,
    setIsPublic,
    setShowImport,
    setModalCard,
    setIsModalOpen,
    
    // Handlers
    handleSave,
    handleQuantityChange,
    handleRemoveCard,
    handleRemoveCommander,
    handleCardHover,
    addCommander,
    refreshDeck,
    router,
  };
}

