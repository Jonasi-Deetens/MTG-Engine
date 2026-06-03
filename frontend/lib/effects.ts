import { api, apiRequest } from './api';
import type { EffectGraph } from '@/lib/unifiedEffect';

export interface EffectValidationResponse {
  valid: boolean;
  errors: string[];
}

export interface CardEffectGraphResponse {
  id: number;
  card_id: string;
  effect_graph: EffectGraph;
  created_at: string;
  updated_at: string;
}

export const effects = {
  validate: async (graph: EffectGraph): Promise<EffectValidationResponse> => {
    return api.post<EffectValidationResponse>('/api/effects/validate', graph);
  },
  saveCardEffectGraph: async (cardId: string, graph: EffectGraph): Promise<CardEffectGraphResponse> => {
    return api.post<CardEffectGraphResponse>(`/api/effects/cards/${cardId}/effects`, graph);
  },
  getCardEffectGraph: async (cardId: string): Promise<CardEffectGraphResponse> => {
    return apiRequest<CardEffectGraphResponse>(`/api/effects/cards/${cardId}/effects`, {
      method: 'GET',
      timeoutMs: 20000,
    });
  },
};
