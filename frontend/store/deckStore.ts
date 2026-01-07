// frontend/store/deckStore.ts

import { create } from 'zustand';
import { decks, DeckDetailResponse, DeckCardResponse, DeckCommanderResponse, DeckValidationResponse } from '@/lib/decks';

interface DeckState {
  // Current deck being edited
  currentDeck: DeckDetailResponse | null;
  validation: DeckValidationResponse | null;
  
  // Loading and error states
  loading: boolean;
  error: string | null;
  
  // Actions
  loadDeck: (deckId: number) => Promise<void>;
  createDeck: (name: string, format: string, description?: string) => Promise<number>;
  updateDeck: (deckId: number, updates: { name?: string; description?: string; format?: string; is_public?: boolean }) => Promise<void>;
  deleteDeck: (deckId: number) => Promise<void>;
  
  // Card management
  addCard: (deckId: number, cardId: string, quantity?: number) => Promise<void>;
  updateCardQuantity: (deckId: number, cardId: string, quantity: number) => Promise<void>;
  removeCard: (deckId: number, cardId: string) => Promise<void>;
  
  // Commander management
  addCommander: (deckId: number, cardId: string, position?: number) => Promise<void>;
  removeCommander: (deckId: number, cardId: string) => Promise<void>;
  
  // Validation
  validateDeck: (deckId: number) => Promise<void>;
  
  // Utility
  clearDeck: () => void;
  refreshDeck: (deckId: number) => Promise<void>;
}

export const useDeckStore = create<DeckState>((set, get) => ({
  currentDeck: null,
  validation: null,
  loading: false,
  error: null,

  loadDeck: async (deckId: number) => {
    set({ loading: true, error: null });
    try {
      const deck = await decks.getDeck(deckId);
      set({ currentDeck: deck, loading: false });
      // Auto-validate on load
      await get().validateDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to load deck', loading: false });
    }
  },

  createDeck: async (name: string, format: string, description?: string) => {
    set({ loading: true, error: null });
    try {
      const newDeck = await decks.createDeck({ name, format, description, is_public: false });
      // Load the full deck details
      await get().loadDeck(newDeck.id);
      return newDeck.id;
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to create deck', loading: false });
      throw err;
    }
  },

  updateDeck: async (deckId: number, updates: { name?: string; description?: string; format?: string; is_public?: boolean }) => {
    set({ loading: true, error: null });
    try {
      await decks.updateDeck(deckId, updates);
      await get().refreshDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to update deck', loading: false });
      throw err;
    }
  },

  deleteDeck: async (deckId: number) => {
    set({ loading: true, error: null });
    try {
      await decks.deleteDeck(deckId);
      set({ currentDeck: null, validation: null, loading: false });
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to delete deck', loading: false });
      throw err;
    }
  },

  addCard: async (deckId: number, cardId: string, quantity: number = 1) => {
    set({ loading: true, error: null });
    try {
      await decks.addCard(deckId, { card_id: cardId, quantity });
      await get().refreshDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to add card', loading: false });
      throw err;
    }
  },

  updateCardQuantity: async (deckId: number, cardId: string, quantity: number) => {
    set({ loading: true, error: null });
    try {
      await decks.updateCardQuantity(deckId, cardId, { quantity });
      await get().refreshDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to update card quantity', loading: false });
      throw err;
    }
  },

  removeCard: async (deckId: number, cardId: string) => {
    set({ loading: true, error: null });
    try {
      await decks.removeCard(deckId, cardId);
      await get().refreshDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to remove card', loading: false });
      throw err;
    }
  },

  addCommander: async (deckId: number, cardId: string, position: number = 0) => {
    set({ loading: true, error: null });
    try {
      await decks.addCommander(deckId, { card_id: cardId, position });
      await get().refreshDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to add commander', loading: false });
      throw err;
    }
  },

  removeCommander: async (deckId: number, cardId: string) => {
    set({ loading: true, error: null });
    try {
      await decks.removeCommander(deckId, cardId);
      await get().refreshDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to remove commander', loading: false });
      throw err;
    }
  },

  validateDeck: async (deckId: number) => {
    try {
      const validation = await decks.validateDeck(deckId);
      set({ validation });
    } catch (err: any) {
      console.error('Failed to validate deck:', err);
    }
  },

  clearDeck: () => {
    set({ currentDeck: null, validation: null, error: null });
  },

  refreshDeck: async (deckId: number) => {
    try {
      const deck = await decks.getDeck(deckId);
      set({ currentDeck: deck, loading: false });
      // Re-validate after refresh
      await get().validateDeck(deckId);
    } catch (err: any) {
      set({ error: err?.data?.detail || err?.message || 'Failed to refresh deck', loading: false });
    }
  },
}));

