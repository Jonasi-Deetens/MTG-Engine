import { api } from './api';
import { DeckDetailResponse } from './decks';
import { CardData } from '@/components/cards/CardPreview';

export interface EngineGameObjectSnapshot {
  id: string;
  name: string;
  owner_id: number;
  controller_id: number;
  types: string[];
  zone: string;
  mana_value?: number | null;
  power?: number | null;
  toughness?: number | null;
  tapped: boolean;
  damage: number;
  counters: Record<string, number>;
  keywords: string[];
  protections: string[];
  attached_to?: string | null;
  is_token: boolean;
  was_cast: boolean;
  is_attacking: boolean;
  is_blocking: boolean;
  phased_out: boolean;
  transformed: boolean;
  regenerate_shield: boolean;
}

export interface EnginePlayerSnapshot {
  id: number;
  life: number;
  mana_pool: Record<string, number>;
  library: string[];
  hand: string[];
  graveyard: string[];
  exile: string[];
  command: string[];
  battlefield: string[];
  commander_id?: string | null;
  commander_tax: number;
  commander_damage_taken: Record<string, number>;
}

export interface EngineTurnSnapshot {
  turn_number: number;
  active_player_index: number;
  phase: string;
  step: string;
}

export interface EngineStackItemSnapshot {
  kind: 'spell' | 'activated_ability' | 'triggered_ability' | 'ability_graph';
  payload: Record<string, any>;
  controller_id?: number | null;
}

export interface EngineGameStateSnapshot {
  players: EnginePlayerSnapshot[];
  objects: EngineGameObjectSnapshot[];
  stack: EngineStackItemSnapshot[];
  turn: EngineTurnSnapshot;
  debug_log: string[];
}

export interface EngineResolveContextSnapshot {
  source_id?: string | null;
  controller_id?: number | null;
  triggering_source_id?: string | null;
  triggering_aura_id?: string | null;
  triggering_spell_id?: string | null;
  targets?: Record<string, any>;
  choices?: Record<string, any>;
  previous_results?: Array<Record<string, any>>;
}

export interface EngineActionRequest {
  action: 'resolve_graph' | 'advance_turn' | 'pass_priority';
  game_state: EngineGameStateSnapshot;
  ability_graph?: Record<string, any>;
  context?: EngineResolveContextSnapshot;
  player_id?: number;
}

export interface EngineActionResponse {
  game_state: EngineGameStateSnapshot;
  result: Record<string, any>;
  debug_log: string[];
}

export const engineApi = {
  execute: async (payload: EngineActionRequest): Promise<EngineActionResponse> => {
    return api.post<EngineActionResponse>('/api/engine/execute', payload);
  },
};

export interface EngineCardMap {
  [objectId: string]: CardData | undefined;
}

const parseTypes = (typeLine?: string): string[] => {
  if (!typeLine) return [];
  const parts = typeLine.split('—');
  return parts[0].trim().split(/\s+/).filter(Boolean);
};

const parseStat = (value?: string): number | null => {
  if (!value) return null;
  const numeric = parseInt(value, 10);
  return Number.isNaN(numeric) ? null : numeric;
};

const expandDeckCards = (deck: DeckDetailResponse, playerId: number) => {
  const objects: EngineGameObjectSnapshot[] = [];
  const zones = {
    library: [] as string[],
    hand: [] as string[],
    graveyard: [] as string[],
    exile: [] as string[],
    command: [] as string[],
    battlefield: [] as string[],
  };
  const cardMap: EngineCardMap = {};

  deck.cards.forEach((entry, index) => {
    const quantity = entry.quantity || 1;
    for (let copy = 0; copy < quantity; copy += 1) {
      const objectId = `${entry.card_id}-${playerId}-${index}-${copy}`;
      objects.push({
        id: objectId,
        name: entry.card.name,
        owner_id: playerId,
        controller_id: playerId,
        types: parseTypes(entry.card.type_line),
        zone: 'library',
        mana_value: entry.card.mana_value ?? null,
        power: parseStat(entry.card.power),
        toughness: parseStat(entry.card.toughness),
        tapped: false,
        damage: 0,
        counters: {},
        keywords: [],
        protections: [],
        attached_to: null,
        is_token: false,
        was_cast: false,
        is_attacking: false,
        is_blocking: false,
        phased_out: false,
        transformed: false,
        regenerate_shield: false,
      });
      zones.library.push(objectId);
      cardMap[objectId] = entry.card;
    }
  });

  deck.commanders.forEach((commander, index) => {
    const objectId = `${commander.card_id}-commander-${playerId}-${index}`;
    objects.push({
      id: objectId,
      name: commander.card.name,
      owner_id: playerId,
      controller_id: playerId,
      types: parseTypes(commander.card.type_line),
      zone: 'command',
      mana_value: commander.card.mana_value ?? null,
      power: parseStat(commander.card.power),
      toughness: parseStat(commander.card.toughness),
      tapped: false,
      damage: 0,
      counters: {},
      keywords: [],
      protections: [],
      attached_to: null,
      is_token: false,
      was_cast: false,
      is_attacking: false,
      is_blocking: false,
      phased_out: false,
      transformed: false,
      regenerate_shield: false,
    });
    zones.command.push(objectId);
    cardMap[objectId] = commander.card;
  });

  return { objects, zones, cardMap };
};

export const buildGameSnapshot = (decks: DeckDetailResponse[], handSize: number = 7) => {
  const objects: EngineGameObjectSnapshot[] = [];
  const players: EnginePlayerSnapshot[] = [];
  const cardMap: EngineCardMap = {};

  decks.forEach((deck, playerId) => {
    const { objects: deckObjects, zones, cardMap: deckCardMap } = expandDeckCards(deck, playerId);
    objects.push(...deckObjects);
    Object.assign(cardMap, deckCardMap);

    const library = [...zones.library];
    const hand = library.splice(0, handSize);

    players.push({
      id: playerId,
      life: 40,
      mana_pool: {},
      library,
      hand,
      graveyard: zones.graveyard,
      exile: zones.exile,
      command: zones.command,
      battlefield: zones.battlefield,
      commander_id: zones.command[0] || null,
      commander_tax: 0,
      commander_damage_taken: {},
    });

    hand.forEach((objectId) => {
      const obj = objects.find((entry) => entry.id === objectId);
      if (obj) {
        obj.zone = 'hand';
      }
    });
  });

  return {
    snapshot: {
      players,
      objects,
      stack: [],
      turn: {
        turn_number: 1,
        active_player_index: 0,
        phase: 'beginning',
        step: 'untap',
      },
      debug_log: [],
    } as EngineGameStateSnapshot,
    cardMap,
  };
};
