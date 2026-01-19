import { EngineCardMap, EngineGameStateSnapshot } from '@/lib/engine';
import { CHOICE_TYPE_OPTIONS } from '@/lib/effectTypes';

export type EnterChoiceConfig = { choiceType: string; choiceValue?: string };

const getNodePayload = (node: any) => {
  if (node?.type === 'ACTIVATED' && node?.data?.effect) return node.data.effect;
  return node?.data;
};

export const buildEnterChoiceConfig = (graph: any): EnterChoiceConfig[] => {
  if (!graph?.nodes) return [];
  const configs: EnterChoiceConfig[] = [];
  graph.nodes.forEach((node: any) => {
    const payload = getNodePayload(node);
    if (payload?.type === 'enter_choice' && payload?.choice) {
      configs.push({ choiceType: payload.choice, choiceValue: payload.choiceValue });
    }
  });
  const byType = new Map<string, EnterChoiceConfig>();
  configs.forEach((config) => {
    const existing = byType.get(config.choiceType);
    if (!existing || (!existing.choiceValue && config.choiceValue)) {
      byType.set(config.choiceType, config);
    }
  });
  return Array.from(byType.values());
};

export const buildEnterChoiceDefaults = (
  configs: EnterChoiceConfig[],
  previous: Record<string, string> = {}
) => {
  const next: Record<string, string> = {};
  configs.forEach((config) => {
    if (config.choiceValue) {
      next[config.choiceType] = config.choiceValue;
      return;
    }
    if (previous[config.choiceType]) {
      next[config.choiceType] = previous[config.choiceType];
      return;
    }
    if (config.choiceType === 'color') {
      next[config.choiceType] = 'W';
      return;
    }
    if (config.choiceType === 'card_type') {
      next[config.choiceType] = 'creature';
      return;
    }
    next[config.choiceType] = '';
  });
  return next;
};

export const buildEnterChoiceErrors = (
  configs: EnterChoiceConfig[],
  choices: Record<string, string>
) => {
  if (configs.length === 0) return [];
  const labels = new Map(CHOICE_TYPE_OPTIONS.map((opt) => [opt.value, opt.label]));
  return configs
    .filter((config) => !config.choiceValue)
    .map((config) => {
      const value = choices[config.choiceType];
      if (!value) {
        const label = labels.get(config.choiceType) ?? config.choiceType;
        return `Missing ${label.toLowerCase()} choice.`;
      }
      return null;
    })
    .filter(Boolean) as string[];
};

export const buildEnterChoiceTargetOptions = (
  gameState: EngineGameStateSnapshot | null,
  cardMap: EngineCardMap
) => {
  if (!gameState) return [];
  const objects = gameState.objects
    .filter((obj) => obj.zone === 'battlefield')
    .map((obj) => ({
      value: obj.id,
      label: cardMap[obj.id]?.name || obj.name || obj.id,
    }));
  const players = gameState.players.map((player) => ({
    value: `player:${player.id}`,
    label: `Player ${player.id + 1}`,
  }));
  return [...objects, ...players];
};

