// frontend/lib/decks.ts

import { api } from './api';
import { CardData } from '@/components/cards/CardPreview';

export interface DeckCardResponse {
  card_id: string;
  card: CardData;
  quantity: number;
  list_id?: number | null;
}

export interface DeckCommanderResponse {
  card_id: string;
  card: CardData;
  position: number;
}

export interface DeckResponse {
  id: number;
  name: string;
  description?: string;
  format: string;
  is_public: boolean;
  card_count: number;
  commander_count: number;
  created_at: string;
  updated_at: string;
}

export interface DeckDetailResponse extends DeckResponse {
  cards: DeckCardResponse[];
  commanders: DeckCommanderResponse[];
}

export interface DeckCreate {
  name: string;
  description?: string;
  format: string;
  is_public?: boolean;
}

export interface DeckUpdate {
  name?: string;
  description?: string;
  format?: string;
  is_public?: boolean;
}

export interface DeckCardAdd {
  card_id: string;
  quantity?: number;
  list_id?: number | null;
}

export interface DeckCardUpdate {
  quantity: number;
}

export interface DeckCommanderAdd {
  card_id: string;
  position?: number;
}

export interface ValidationError {
  type: 'error' | 'warning';
  message: string;
  field?: string;
}

export interface DeckValidationResponse {
  is_valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  card_count: number;
  commander_count: number;
  format: string;
}

export interface DeckImportRequest {
  format: 'text' | 'json';
  data: string;
}

export interface DeckExportResponse {
  format: string;
  data: string;
  deck_name: string;
  format_type: string;
}

export interface DeckCustomListResponse {
  id: number;
  deck_id: number;
  name: string;
  position: number;
  created_at: string;
}

export interface DeckCustomListCreate {
  name: string;
  position?: number;
}

export interface DeckCustomListUpdate {
  name?: string;
  position?: number;
}

export interface DeckCardListUpdate {
  list_id?: number | null;
}

export const decks = {
  // List decks
  getDecks: async (format?: string, isPublic?: boolean): Promise<DeckResponse[]> => {
    const params = new URLSearchParams();
    if (format) params.append('format', format);
    if (isPublic !== undefined) params.append('is_public', String(isPublic));
    const query = params.toString();
    return api.get<DeckResponse[]>(`/api/decks${query ? `?${query}` : ''}`);
  },

  // Get deck details
  getDeck: async (deckId: number): Promise<DeckDetailResponse> => {
    return api.get<DeckDetailResponse>(`/api/decks/${deckId}`);
  },

  // Create deck
  createDeck: async (deck: DeckCreate): Promise<DeckResponse> => {
    return api.post<DeckResponse>('/api/decks', deck);
  },

  // Update deck
  updateDeck: async (deckId: number, deck: DeckUpdate): Promise<DeckResponse> => {
    return api.put<DeckResponse>(`/api/decks/${deckId}`, deck);
  },

  // Delete deck
  deleteDeck: async (deckId: number): Promise<{ message: string }> => {
    return api.delete<{ message: string }>(`/api/decks/${deckId}`);
  },

  // Add card to deck
  addCard: async (deckId: number, card: DeckCardAdd): Promise<DeckCardResponse> => {
    return api.post<DeckCardResponse>(`/api/decks/${deckId}/cards`, card);
  },

  // Update card quantity
  updateCardQuantity: async (deckId: number, cardId: string, update: DeckCardUpdate): Promise<DeckCardResponse> => {
    return api.put<DeckCardResponse>(`/api/decks/${deckId}/cards/${encodeURIComponent(cardId)}`, update);
  },

  // Remove card from deck
  removeCard: async (deckId: number, cardId: string): Promise<{ message: string }> => {
    return api.delete<{ message: string }>(`/api/decks/${deckId}/cards/${encodeURIComponent(cardId)}`);
  },

  // Add commander
  addCommander: async (deckId: number, commander: DeckCommanderAdd): Promise<DeckCommanderResponse> => {
    return api.post<DeckCommanderResponse>(`/api/decks/${deckId}/commanders`, commander);
  },

  // Remove commander
  removeCommander: async (deckId: number, cardId: string): Promise<{ message: string }> => {
    return api.delete<{ message: string }>(`/api/decks/${deckId}/commanders/${encodeURIComponent(cardId)}`);
  },

  // Validate deck
  validateDeck: async (deckId: number): Promise<DeckValidationResponse> => {
    return api.get<DeckValidationResponse>(`/api/decks/${deckId}/validate`);
  },

  // Import deck
  importDeck: async (importData: DeckImportRequest): Promise<DeckDetailResponse> => {
    return api.post<DeckDetailResponse>('/api/decks/import', importData);
  },

  // Export deck
  exportDeck: async (deckId: number, format: 'text' | 'json' = 'text'): Promise<DeckExportResponse> => {
    return api.get<DeckExportResponse>(`/api/decks/${deckId}/export?format=${format}`);
  },

  // Custom Lists
  createCustomList: async (deckId: number, customList: DeckCustomListCreate): Promise<DeckCustomListResponse> => {
    return api.post<DeckCustomListResponse>(`/api/decks/${deckId}/lists`, customList);
  },

  getCustomLists: async (deckId: number): Promise<DeckCustomListResponse[]> => {
    return api.get<DeckCustomListResponse[]>(`/api/decks/${deckId}/lists`);
  },

  updateCustomList: async (deckId: number, listId: number, update: DeckCustomListUpdate): Promise<DeckCustomListResponse> => {
    return api.put<DeckCustomListResponse>(`/api/decks/${deckId}/lists/${listId}`, update);
  },

  deleteCustomList: async (deckId: number, listId: number): Promise<{ message: string }> => {
    return api.delete<{ message: string }>(`/api/decks/${deckId}/lists/${listId}`);
  },

  moveCardToList: async (deckId: number, cardId: string, update: DeckCardListUpdate): Promise<DeckCardResponse> => {
    return api.put<DeckCardResponse>(`/api/decks/${deckId}/cards/${encodeURIComponent(cardId)}/list`, update);
  },
};

