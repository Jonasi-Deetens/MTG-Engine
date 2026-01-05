// frontend/lib/abilities.ts

import { api } from './api';
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

export const abilities = {
  // Validate an ability graph
  validate: async (graph: AbilityGraph, cardColors?: string[]): Promise<ValidationResponse> => {
    return api.post<ValidationResponse>('/api/abilities/validate', {
      ...graph,
      card_colors: cardColors,
    });
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
};

