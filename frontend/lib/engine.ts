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
  mana_cost?: string | null;
  base_name?: string | null;
  base_mana_cost?: string | null;
  base_mana_value?: number | null;
  base_types?: string[];
  colors?: string[];
  base_colors?: string[];
  type_line?: string | null;
  base_type_line?: string | null;
  oracle_text?: string | null;
  base_oracle_text?: string | null;
  mana_value?: number | null;
  power?: number | null;
  toughness?: number | null;
  base_power?: number | null;
  base_toughness?: number | null;
  cda_power?: number | null;
  cda_toughness?: number | null;
  entered_turn?: number | null;
  tapped: boolean;
  damage: number;
  counters: Record<string, number>;
  keywords: string[];
  base_keywords?: string[];
  protections: string[];
  attached_to?: string | null;
  is_token: boolean;
  was_cast: boolean;
  is_attacking: boolean;
  is_blocking: boolean;
  phased_out: boolean;
  transformed: boolean;
  regenerate_shield: boolean;
  ability_graphs?: Array<Record<string, any>>;
  base_ability_graphs?: Array<Record<string, any>>;
  temporary_effects?: Array<Record<string, any>>;
  activation_limits?: Record<string, number>;
  etb_choices?: Record<string, any>;
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
  land_plays_this_turn?: number;
  combat_state?: EngineCombatStateSnapshot | null;
  priority_current_index?: number;
  priority_pass_count?: number;
  priority_last_passed_player_id?: number | null;
}

export interface EngineCombatStateSnapshot {
  attacking_player_id?: number | null;
  defending_player_id?: number | null;
  attackers: string[];
  blockers: Record<string, string[]>;
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
  replacement_effects?: Array<Record<string, any>>;
  replacement_choices?: Record<string, string>;
  prepared_casts?: Record<number, Record<string, any>>;
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
  action:
    | 'resolve_graph'
    | 'advance_turn'
    | 'pass_priority'
    | 'activate_mana_ability'
    | 'activate_ability'
    | 'play_land'
    | 'prepare_cast'
    | 'finalize_cast'
    | 'cast_spell'
    | 'check_targets'
    | 'declare_attackers'
    | 'declare_blockers'
    | 'assign_combat_damage';
  game_state: EngineGameStateSnapshot;
  ability_graph?: Record<string, any>;
  context?: EngineResolveContextSnapshot;
  player_id?: number;
  object_id?: string;
  ability_index?: number;
  attackers?: string[];
  blockers?: Record<string, string[]>;
  defending_player_id?: number | null;
  damage_assignments?: Record<string, Record<string, number>>;
  mana_payment?: Record<string, number>;
  mana_payment_detail?: {
    hybrid_choices?: string[];
    two_brid_choices?: boolean[];
    phyrexian_choices?: boolean[];
  };
  contexts?: EngineResolveContextSnapshot[];
  x_value?: number | null;
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

const parseKeywords = (oracleText?: string): string[] => {
  if (!oracleText) return [];
  const keywords = [
    'Flying',
    'First strike',
    'Double strike',
    'Trample',
    'Haste',
    'Vigilance',
    'Lifelink',
    'Deathtouch',
    'Reach',
    'Hexproof',
    'Indestructible',
    'Ward',
  ];
  const found: string[] = [];
  keywords.forEach((keyword) => {
    if (oracleText.includes(keyword)) {
      found.push(keyword);
    }
  });
  return found;
};

const parseProtections = (oracleText?: string): string[] => {
  if (!oracleText) return [];
  const matches = oracleText.match(/Protection from ([^\n]+)/gi) || [];
  return matches
    .map((match) => match.replace(/Protection from /i, '').trim())
    .flatMap((value) => value.split(/\s+and\s+|,|\s+or\s+/i))
    .map((token) => token.trim())
    .filter(Boolean);
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
        mana_cost: entry.card.mana_cost ?? null,
        base_types: parseTypes(entry.card.type_line),
        colors: entry.card.colors ?? [],
        base_colors: entry.card.colors ?? [],
        type_line: entry.card.type_line ?? null,
        base_type_line: entry.card.type_line ?? null,
        oracle_text: entry.card.oracle_text ?? null,
        base_oracle_text: entry.card.oracle_text ?? null,
        mana_value: entry.card.mana_value ?? null,
        power: parseStat(entry.card.power),
        toughness: parseStat(entry.card.toughness),
        base_power: parseStat(entry.card.power),
        base_toughness: parseStat(entry.card.toughness),
        base_name: entry.card.name ?? null,
        base_mana_cost: entry.card.mana_cost ?? null,
        base_mana_value: entry.card.mana_value ?? null,
        entered_turn: null,
        tapped: false,
        damage: 0,
        counters: {},
        keywords: parseKeywords(entry.card.oracle_text),
        base_keywords: parseKeywords(entry.card.oracle_text),
        protections: parseProtections(entry.card.oracle_text),
        attached_to: null,
        is_token: false,
        was_cast: false,
        is_attacking: false,
        is_blocking: false,
        phased_out: false,
        transformed: false,
        regenerate_shield: false,
        ability_graphs: [],
        base_ability_graphs: [],
        temporary_effects: [],
        etb_choices: {},
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
      mana_cost: commander.card.mana_cost ?? null,
      base_types: parseTypes(commander.card.type_line),
      colors: commander.card.colors ?? [],
      base_colors: commander.card.colors ?? [],
      type_line: commander.card.type_line ?? null,
      base_type_line: commander.card.type_line ?? null,
      oracle_text: commander.card.oracle_text ?? null,
      base_oracle_text: commander.card.oracle_text ?? null,
      mana_value: commander.card.mana_value ?? null,
      power: parseStat(commander.card.power),
      toughness: parseStat(commander.card.toughness),
      base_power: parseStat(commander.card.power),
      base_toughness: parseStat(commander.card.toughness),
      base_name: commander.card.name ?? null,
      base_mana_cost: commander.card.mana_cost ?? null,
      base_mana_value: commander.card.mana_value ?? null,
      entered_turn: null,
      tapped: false,
      damage: 0,
      counters: {},
      keywords: parseKeywords(commander.card.oracle_text),
      base_keywords: parseKeywords(commander.card.oracle_text),
      protections: parseProtections(commander.card.oracle_text),
      attached_to: null,
      is_token: false,
      was_cast: false,
      is_attacking: false,
      is_blocking: false,
      phased_out: false,
      transformed: false,
      regenerate_shield: false,
      ability_graphs: [],
      base_ability_graphs: [],
      temporary_effects: [],
      etb_choices: {},
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
        land_plays_this_turn: 0,
        combat_state: null,
        priority_current_index: 0,
        priority_pass_count: 0,
        priority_last_passed_player_id: null,
      },
      debug_log: [],
      prepared_casts: {},
    } as EngineGameStateSnapshot,
    cardMap,
  };
};
