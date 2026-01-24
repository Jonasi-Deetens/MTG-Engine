import type { UnifiedEffect } from '@/lib/unifiedEffect';
import { ZONE_OPTIONS } from '@/lib/effectTypes';
import { KEYWORD_OPTIONS } from '@/lib/conditionTypes';

interface ContinuousConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

const LAYER_OPTIONS = [
  { value: 6, label: 'Layer 6 (Abilities/Keywords)' },
  { value: 7, label: 'Layer 7 (Power/Toughness)' },
  { value: 4, label: 'Layer 4 (Types)' },
  { value: 5, label: 'Layer 5 (Colors)' },
  { value: 2, label: 'Layer 2 (Control)' },
];

const APPLIES_TO_OPTIONS = [
  { value: 'self', label: 'This Permanent' },
  { value: 'creatures_you_control', label: 'Creatures You Control' },
  { value: 'all_creatures', label: 'All Creatures' },
  { value: 'all_permanents', label: 'All Permanents' },
  { value: 'permanents_you_control', label: 'Permanents You Control' },
  { value: 'opponents_creatures', label: "Opponents' Creatures" },
];

const DURATION_OPTIONS = [
  { value: 'while_in_zone', label: 'While in zone' },
  { value: 'until_end_of_turn', label: 'Until end of turn' },
  { value: 'until_end_of_combat', label: 'Until end of combat' },
  { value: 'until_your_next_turn', label: 'Until your next turn' },
];

const MODIFIER_TYPE_OPTIONS = [
  { value: 'add_keyword', label: 'Add Keyword' },
  { value: 'remove_keyword', label: 'Remove Keyword' },
  { value: 'change_power_toughness', label: 'Change Power/Toughness' },
  { value: 'set_power_toughness', label: 'Set Power/Toughness' },
  { value: 'add_type', label: 'Add Type' },
  { value: 'remove_type', label: 'Remove Type' },
  { value: 'set_types', label: 'Set Types' },
  { value: 'add_color', label: 'Add Color' },
  { value: 'remove_color', label: 'Remove Color' },
  { value: 'set_colors', label: 'Set Colors' },
  { value: 'change_control', label: 'Change Control' },
  { value: 'cant_attack', label: "Can't Attack" },
  { value: 'cant_block', label: "Can't Block" },
  { value: 'cant_be_blocked', label: "Can't Be Blocked" },
];

export function ContinuousConfig({ effect, onChange }: ContinuousConfigProps) {
  const body = effect.effect.kind === 'continuous' ? effect.effect : null;
  if (!body) {
    return null;
  }

  const updateBody = (updates: Record<string, unknown>) => {
    onChange({
      ...effect,
      effect: { ...body, ...updates },
    });
  };

  const durationType = body.duration?.type ?? 'while_in_zone';

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Layer
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={body.layer}
            onChange={(e) => updateBody({ layer: Number(e.target.value) })}
          >
            {LAYER_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Applies To
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={typeof body.appliesTo === 'string' ? body.appliesTo : (body.appliesTo as any)?.type ?? 'self'}
            onChange={(e) => updateBody({ appliesTo: { type: e.target.value } })}
          >
            {APPLIES_TO_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Modifier Type
        </label>
        <select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={(body.modifier as any)?.type ?? 'add_keyword'}
          onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), type: e.target.value } })}
        >
          {MODIFIER_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {((body.modifier as any)?.type === 'add_keyword' || (body.modifier as any)?.type === 'remove_keyword') && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Keyword
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={(body.modifier as any)?.keyword ?? ''}
            onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), keyword: e.target.value } })}
          >
            <option value="">Select keyword</option>
            {KEYWORD_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {((body.modifier as any)?.type === 'change_power_toughness' || (body.modifier as any)?.type === 'set_power_toughness') && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Power
            </label>
            <input
              type="number"
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={(body.modifier as any)?.power ?? 0}
              onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), power: Number(e.target.value) } })}
            />
          </div>
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Toughness
            </label>
            <input
              type="number"
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={(body.modifier as any)?.toughness ?? 0}
              onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), toughness: Number(e.target.value) } })}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Duration
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={durationType}
            onChange={(e) => {
              const type = e.target.value;
              if (type === 'while_in_zone') {
                updateBody({ duration: { type, zone: 'battlefield' } });
              } else {
                updateBody({ duration: { type } });
              }
            }}
          >
            {DURATION_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        {durationType === 'while_in_zone' && (
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Zone
            </label>
            <select
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={(body.duration as any)?.zone ?? 'battlefield'}
              onChange={(e) => updateBody({ duration: { type: 'while_in_zone', zone: e.target.value } })}
            >
              {ZONE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>
    </div>
  );
}
