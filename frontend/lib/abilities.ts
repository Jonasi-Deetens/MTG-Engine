// frontend/lib/abilities.ts

import { api, apiRequest } from './api';
import { AbilityGraph, ValidationResponse, NormalizedAbility } from '@/store/builderStore';

export interface KeywordOption {
  has_cost: boolean;
  has_number: boolean;
  has_mana_cost: boolean;
  cost_type?: string;
  number_type?: string;
  description?: string;
}

export interface KeywordInfo {
  name: string;
  alias_of?: string;
  has_parser: boolean;
  options: KeywordOption;
}

export interface KeywordList {
  keywords: KeywordInfo[];
  total: number;
  error?: string;
  traceback?: string;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  graph: AbilityGraph;
}

export interface TemplatesResponse {
  templates: Template[];
}

export interface CardAbilityGraphResponse {
  id: number;
  card_id: string;
  ability_graph: any; // AbilityGraph type
  created_at: string;
  updated_at: string;
}

export interface CardAbilityGraphBulkRequest {
  card_ids: string[];
}

export interface CardAbilityGraphBulkResponse {
  graphs: CardAbilityGraphResponse[];
  missing: string[];
}

export const abilities = {
  // Validate an ability graph
  validate: async (graph: AbilityGraph, cardColors?: string[]): Promise<ValidationResponse> => {
    const params = new URLSearchParams();
    (cardColors || []).forEach((color) => params.append('card_colors', color));
    const query = params.toString();
    const endpoint = query ? `/api/abilities/validate?${query}` : '/api/abilities/validate';
    return api.post<ValidationResponse>(endpoint, graph);
  },

  // Normalize graph to engine format
  normalize: async (graph: AbilityGraph): Promise<NormalizedAbility> => {
    return api.post<NormalizedAbility>('/api/abilities/normalize', graph);
  },

  // List available keywords
  listKeywords: async (): Promise<KeywordList> => {
    return api.get<KeywordList>('/api/abilities/keywords');
  },

  // Get templates
  getTemplates: async (): Promise<TemplatesResponse> => {
    return api.get<TemplatesResponse>('/api/abilities/templates');
  },

  // Save template (placeholder)
  saveTemplate: async (template: Template): Promise<{ message: string; template: Template }> => {
    return api.post<{ message: string; template: Template }>('/api/abilities/templates', template);
  },

  // Save card ability graph
  saveCardGraph: async (cardId: string, abilityGraph: AbilityGraph): Promise<CardAbilityGraphResponse> => {
    return api.post<CardAbilityGraphResponse>(`/api/abilities/cards/${cardId}/graph`, abilityGraph);
  },

  // Get card ability graph
  getCardGraph: async (cardId: string): Promise<CardAbilityGraphResponse> => {
    return apiRequest<CardAbilityGraphResponse>(`/api/abilities/cards/${cardId}/graph`, {
      method: 'GET',
      timeoutMs: 20000,
    });
  },

  // Get multiple card ability graphs
  getCardGraphs: async (cardIds: string[]): Promise<CardAbilityGraphBulkResponse> => {
    return apiRequest<CardAbilityGraphBulkResponse>('/api/abilities/cards/graphs', {
      method: 'POST',
      body: JSON.stringify({
        card_ids: cardIds,
      } satisfies CardAbilityGraphBulkRequest),
      timeoutMs: 20000,
    });
  },

  // Delete card ability graph
  deleteCardGraph: async (cardId: string): Promise<void> => {
    return api.delete(`/api/abilities/cards/${cardId}/graph`);
  },
};

