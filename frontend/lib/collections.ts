// frontend/lib/collections.ts

import { api } from './api';
import { CardData } from '@/components/cards/CardPreview';

export interface FavoriteResponse {
  card_id: string;
  card: CardData;
  created_at: string;
}

export interface CollectionResponse {
  id: number;
  name: string;
  description?: string;
  card_count: number;
  created_at: string;
  updated_at: string;
}

export interface CollectionDetailResponse extends CollectionResponse {
  cards: CardData[];
}

export interface CollectionCreate {
  name: string;
  description?: string;
}

export interface CollectionUpdate {
  name?: string;
  description?: string;
}

export const collections = {
  // Favorites
  getFavorites: async (page: number = 1, pageSize: number = 20): Promise<FavoriteResponse[]> => {
    return api.get<FavoriteResponse[]>(`/api/collections/favorites?page=${page}&page_size=${pageSize}`);
  },

  addFavorite: async (cardId: string): Promise<{ message: string; card_id: string }> => {
    return api.post<{ message: string; card_id: string }>('/api/collections/favorites', {
      card_id: cardId,
    });
  },

  removeFavorite: async (cardId: string): Promise<{ message: string }> => {
    return api.delete<{ message: string }>(`/api/collections/favorites/${encodeURIComponent(cardId)}`);
  },

  checkFavorite: async (cardId: string): Promise<{ is_favorite: boolean }> => {
    return api.get<{ is_favorite: boolean }>(`/api/collections/favorites/${encodeURIComponent(cardId)}/check`);
  },

  // Collections
  getCollections: async (): Promise<CollectionResponse[]> => {
    return api.get<CollectionResponse[]>('/api/collections');
  },

  getCollection: async (collectionId: number): Promise<CollectionDetailResponse> => {
    return api.get<CollectionDetailResponse>(`/api/collections/${collectionId}`);
  },

  createCollection: async (collection: CollectionCreate): Promise<CollectionResponse> => {
    return api.post<CollectionResponse>('/api/collections', collection);
  },

  updateCollection: async (collectionId: number, collection: CollectionUpdate): Promise<CollectionResponse> => {
    return api.put<CollectionResponse>(`/api/collections/${collectionId}`, collection);
  },

  deleteCollection: async (collectionId: number): Promise<{ message: string }> => {
    return api.delete<{ message: string }>(`/api/collections/${collectionId}`);
  },

  addCardToCollection: async (collectionId: number, cardId: string): Promise<{ message: string; card_id: string }> => {
    return api.post<{ message: string; card_id: string }>(`/api/collections/${collectionId}/cards`, {
      card_id: cardId,
    });
  },

  removeCardFromCollection: async (collectionId: number, cardId: string): Promise<{ message: string }> => {
    return api.delete<{ message: string }>(`/api/collections/${collectionId}/cards/${encodeURIComponent(cardId)}`);
  },
};

