import type { UnifiedEffect } from '@/lib/unifiedEffect';
import {
  CARD_TYPE_FILTERS,
  CREATURE_TYPE_OPTIONS,
  EFFECT_TYPE_OPTIONS,
  MANA_TYPE_OPTIONS,
  TARGET_OPTIONS,
  SEARCH_ZONE_OPTIONS,
  SEARCH_CARD_TYPE_FILTERS,
} from '@/lib/effectTypes';

interface EffectBodyStepProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
  previousSteps?: Array<{ index: number; label: string }>;
}

export function EffectBodyStep({ effect, onChange, previousSteps = [] }: EffectBodyStepProps) {
  if (effect.effect.kind !== 'one_shot') {
    return (
      <div className="text-sm text-[color:var(--theme-text-secondary)]">
        This intent uses a non-one-shot effect body configured in the previous step.
      </div>
    );
  }

  const action = effect.effect.action as Record<string, any>;
  const effectType = action.type ?? 'damage';
  const supportsFromEffect =
    effectType === 'put_onto_battlefield' ||
    effectType === 'attach' ||
    effectType === 'put_on_bottom_of_library';
  const supportsKickerAmount = [
    'damage',
    'draw',
    'draw_each',
    'token',
    'counters',
    'life',
    'lose_life',
    'add_poison',
    'mana',
    'mill',
    'discard',
    'scry',
    'look_at',
  ].includes(effectType);
  const supportsLookAtPick = effectType === 'look_at_pick_and_bottom';
  const supportsTokenConfig = effectType === 'token';
  const colorOptions = ['W', 'U', 'B', 'R', 'G'];

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

      <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
        <input
          type="checkbox"
          checked={!!action.optional}
          onChange={(e) => updateAction({ optional: e.target.checked })}
        />
        Optional effect ("may")
      </label>

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
          {supportsTokenConfig && action.target === 'controller_of_target' && (
            <div className="mt-1 text-xs text-[color:var(--theme-text-muted)]">
              Uses the controller of the selected target from a previous step.
            </div>
          )}
        </div>
      </div>
      {supportsTokenConfig && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Power
              </label>
              <input
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                type="number"
                value={action.power ?? 1}
                onChange={(e) => updateAction({ power: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Toughness
              </label>
              <input
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                type="number"
                value={action.toughness ?? 1}
                onChange={(e) => updateAction({ toughness: Number(e.target.value) })}
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Token Types
            </label>
            <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
              {CARD_TYPE_FILTERS.filter((entry) => entry.value !== 'any').map((entry) => {
                const types = Array.isArray(action.tokenTypes) ? action.tokenTypes : [];
                const checked = types.includes(entry.value);
                return (
                  <label
                    key={entry.value}
                    className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]"
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => {
                        const next = checked
                          ? types.filter((type: string) => type !== entry.value)
                          : [...types, entry.value];
                        updateAction({ tokenTypes: next });
                      }}
                    />
                    {entry.label}
                  </label>
                );
              })}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Creature Subtype
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={action.tokenSubtype ?? ''}
                onChange={(e) => updateAction({ tokenSubtype: e.target.value || undefined })}
              >
                <option value="">None</option>
                {CREATURE_TYPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Colors
              </label>
              <div className="mt-2 grid grid-cols-3 gap-2 text-sm">
                {colorOptions.map((color) => {
                  const colors = Array.isArray(action.tokenColors) ? action.tokenColors : [];
                  const checked = colors.includes(color);
                  return (
                    <label key={color} className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => {
                          const next = checked
                            ? colors.filter((entry: string) => entry !== color)
                            : [...colors, color];
                          updateAction({ tokenColors: next });
                        }}
                      />
                      {color}
                    </label>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
      {supportsLookAtPick && (
        <div className="space-y-3">
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Allowed Card Types
            </label>
            <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
              {CARD_TYPE_FILTERS.filter((entry) => entry.value !== 'any').map((entry) => {
                const types = Array.isArray(action.pickTypes) ? action.pickTypes : [];
                const checked = types.includes(entry.value);
                return (
                  <label key={entry.value} className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => {
                        const next = checked
                          ? types.filter((type: string) => type !== entry.value)
                          : [...types, entry.value];
                        updateAction({ pickTypes: next });
                      }}
                    />
                    {entry.label}
                  </label>
                );
              })}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Max Picks
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={action.pickMax ?? 1}
                onChange={(e) => updateAction({ pickMax: Number(e.target.value) })}
              >
                {Array.from({ length: Math.max(1, (action.amount ?? 1) + 1) }, (_, index) => (
                  <option key={index} value={index}>
                    {index}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Destination
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={action.pickDestination ?? 'hand'}
                onChange={(e) => updateAction({ pickDestination: e.target.value })}
              >
                <option value="hand">Hand</option>
                <option value="battlefield">Battlefield</option>
                <option value="graveyard">Graveyard</option>
                <option value="exile">Exile</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
              <input
                type="checkbox"
                checked={action.revealChosen !== false}
                onChange={(e) => updateAction({ revealChosen: e.target.checked })}
              />
              Reveal chosen card
            </label>
            <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
              <input
                type="checkbox"
                checked={action.orderBottom !== false}
                onChange={(e) => updateAction({ orderBottom: e.target.checked })}
              />
              Order rest on bottom
            </label>
          </div>
          <div className="text-xs text-[color:var(--theme-text-muted)]">
            If ordering is off, the rest go to the bottom in current order.
          </div>
        </div>
      )}
      {supportsKickerAmount && (
        <div className="grid grid-cols-2 gap-3">
          <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
            <input
              type="checkbox"
              checked={Number(action.amountPerKicker || 0) > 0}
              onChange={(e) => updateAction({ amountPerKicker: e.target.checked ? 1 : 0 })}
            />
            Scale by kicker count
          </label>
          {Number(action.amountPerKicker || 0) > 0 && (
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Per Kicker
              </label>
              <input
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                type="number"
                value={action.amountPerKicker ?? 1}
                onChange={(e) => updateAction({ amountPerKicker: Number(e.target.value) })}
              />
            </div>
          )}
        </div>
      )}

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
        <div className="space-y-3">
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
              {SEARCH_CARD_TYPE_FILTERS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Put Found Into
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={action.putFoundTo ?? ''}
                onChange={(e) =>
                  updateAction({ putFoundTo: e.target.value === '' ? undefined : e.target.value })
                }
              >
                <option value="">No auto-move</option>
                <option value="hand">Hand</option>
                <option value="battlefield">Battlefield</option>
                <option value="graveyard">Graveyard</option>
                <option value="exile">Exile</option>
              </select>
            </div>
            <div className="flex flex-col justify-end gap-2 text-xs text-[color:var(--theme-text-secondary)]">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={!!action.revealFound}
                  onChange={(e) => updateAction({ revealFound: e.target.checked })}
                />
                Reveal found cards
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={!!action.shuffleAfter}
                  onChange={(e) => updateAction({ shuffleAfter: e.target.checked })}
                />
                Shuffle after search
              </label>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Min Cards
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={action.min ?? 0}
                onChange={(e) => {
                  const min = Number(e.target.value);
                  const max = typeof action.max === 'number' ? action.max : 1;
                  updateAction({ min, ...(min > max ? { max: min } : {}) });
                }}
              >
                {Array.from({ length: 6 }, (_, index) => (
                  <option key={index} value={index}>
                    {index}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Max Cards
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={action.max ?? 1}
                onChange={(e) => {
                  const max = Number(e.target.value);
                  const min = typeof action.min === 'number' ? action.min : 0;
                  updateAction({ max, ...(max < min ? { min: max } : {}) });
                }}
              >
                {Array.from({ length: 6 }, (_, index) => (
                  <option key={index} value={index}>
                    {index}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {supportsFromEffect && previousSteps.length > 0 && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Use Results From
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={action.fromEffect ?? ''}
            onChange={(e) =>
              updateAction({ fromEffect: e.target.value === '' ? undefined : Number(e.target.value) })
            }
          >
            <option value="">No previous step</option>
            {previousSteps.map((step) => (
              <option key={step.index} value={step.index}>
                Step {step.index + 1}: {step.label}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
