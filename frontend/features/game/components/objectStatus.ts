import { EngineGameObjectSnapshot } from '@/lib/engine';

export const getTemporaryStatus = (obj: EngineGameObjectSnapshot) => {
  const durations = (obj.temporary_effects || [])
    .map((effect: any) => effect?.duration)
    .filter((duration: string | undefined) => Boolean(duration));
  if (durations.length === 0) return null;
  if (durations.includes('until_end_of_turn')) return 'Until EOT';
  if (durations.includes('until_end_of_combat')) return 'Until combat';
  if (durations.includes('until_end_of_your_next_turn')) return 'Until your next turn';
  if (durations.includes('until_your_next_upkeep')) return 'Until your next upkeep';
  return 'Temporary';
};

export const getTemporaryDetail = (obj: EngineGameObjectSnapshot) => {
  const effects = obj.temporary_effects || [];
  if (effects.length === 0) return null;
  return effects
    .map((effect: any) => {
      const type = effect?.type;
      const duration = effect?.duration ? ` (${effect.duration})` : '';
      if (type === 'add_keyword') {
        return `Gain ${effect.keyword || 'keyword'}${duration}`;
      }
      if (type === 'remove_keyword') {
        return `Lose ${effect.keyword || 'keyword'}${duration}`;
      }
      if (type === 'set_power_toughness') {
        return `Set ${effect.power ?? '?'} / ${effect.toughness ?? '?'}${duration}`;
      }
      if (type === 'modify_power_toughness') {
        const power = effect.power ?? 0;
        const toughness = effect.toughness ?? 0;
        const powerSign = power >= 0 ? '+' : '';
        const toughnessSign = toughness >= 0 ? '+' : '';
        return `Modify ${powerSign}${power}/${toughnessSign}${toughness}${duration}`;
      }
      if (effect?.prevent_damage) {
        return `Prevent ${effect.prevent_damage} damage${duration}`;
      }
      return `Temporary effect${duration}`;
    })
    .join(', ');
};

export const getEtbChoiceDetail = (obj: EngineGameObjectSnapshot) => {
  const choices = obj.etb_choices || {};
  const entries = Object.entries(choices);
  if (entries.length === 0) return null;
  const formatted = entries
    .map(([key, value]) => {
      if (typeof value === 'string') return `${key}: ${value}`;
      return `${key}: ${JSON.stringify(value)}`;
    })
    .join(', ');
  return `Choices: ${formatted}`;
};
