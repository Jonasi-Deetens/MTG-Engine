import { EngineCardMap, EngineGameStateSnapshot } from '@/lib/engine';
import { CHOICE_TYPE_OPTIONS } from '@/lib/effectTypes';
import type { EffectGraph, EffectStep } from '@/lib/unifiedEffect';

export type EnterChoiceConfig = { choiceType: string; choiceValue?: string };

const getStepAction = (step: EffectStep | undefined) => {
  if (!step?.effect?.effect) return null;
  if (step.effect.effect.kind !== 'one_shot') return null;
  return step.effect.effect.action;
};

export const buildEnterChoiceConfig = (graph: EffectGraph | null): EnterChoiceConfig[] => {
  if (!graph?.steps?.length) return [];
  const configs: EnterChoiceConfig[] = [];
  graph.steps.forEach((step) => {
    const action = getStepAction(step);
    if (action?.type === 'enter_choice' && action?.choice) {
      configs.push({ choiceType: action.choice as string, choiceValue: action.choiceValue as string | undefined });
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

