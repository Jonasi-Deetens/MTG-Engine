import type { UnifiedEffect } from '@/lib/unifiedEffect';
import {
  EFFECT_TYPE_OPTIONS,
  MANA_TYPE_OPTIONS,
  TARGET_OPTIONS,
  SEARCH_ZONE_OPTIONS,
  CARD_TYPE_FILTERS,
} from '@/lib/effectTypes';

interface EffectBodyStepProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

export function EffectBodyStep({ effect, onChange }: EffectBodyStepProps) {
  if (effect.effect.kind !== 'one_shot') {
    return (
      <div className="text-sm text-[color:var(--theme-text-secondary)]">
        This intent uses a non-one-shot effect body configured in the previous step.
      </div>
    );
  }

  const action = effect.effect.action as Record<string, any>;
  const effectType = action.type ?? 'damage';

  const updateAction = (updates: Record<string, unknown>) => {
    onChange({
      ...effect,
      effect: {
        ...effect.effect,
        action: { ...action, ...updates },
      },
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Effect Type
        </label>
        <select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={effectType}
          onChange={(e) => updateAction({ type: e.target.value })}
        >
          {EFFECT_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Amount
          </label>
          <input
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            type="number"
            value={action.amount ?? 1}
            onChange={(e) => updateAction({ amount: Number(e.target.value) })}
          />
        </div>
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Target
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={action.target ?? 'any'}
            onChange={(e) => updateAction({ target: e.target.value })}
          >
            {TARGET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {effectType === 'mana' && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Mana Type
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={action.manaType ?? 'C'}
            onChange={(e) => updateAction({ manaType: e.target.value })}
          >
            {MANA_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {effectType === 'search' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Zone
            </label>
            <select
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={action.zone ?? 'library'}
              onChange={(e) => updateAction({ zone: e.target.value })}
            >
              {SEARCH_ZONE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Card Type Filter
            </label>
            <select
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={action.cardType ?? 'any'}
              onChange={(e) => updateAction({ cardType: e.target.value })}
            >
              {CARD_TYPE_FILTERS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  );
}
