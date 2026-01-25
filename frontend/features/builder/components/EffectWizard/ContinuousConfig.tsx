import type { UnifiedEffect } from '@/lib/unifiedEffect';
import { COLOR_OPTIONS, ZONE_OPTIONS } from '@/lib/effectTypes';
import { KEYWORD_OPTIONS, PERMANENT_TYPES } from '@/lib/conditionTypes';

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
  { value: 'legendary_creatures_you_control', label: 'Legendary Creatures You Control' },
  { value: 'nontoken_creatures_you_control', label: 'Nontoken Creatures You Control' },
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
  { value: 'modify_power_toughness_by_same_name', label: 'PT +X/+X per Same Name' },
  { value: 'add_type', label: 'Add Type' },
  { value: 'remove_type', label: 'Remove Type' },
  { value: 'set_types', label: 'Set Types' },
  { value: 'add_color', label: 'Add Color' },
  { value: 'remove_color', label: 'Remove Color' },
  { value: 'set_colors', label: 'Set Colors' },
  { value: 'change_control', label: 'Change Control' },
  { value: 'ignore_legend_rule', label: 'Ignore Legend Rule' },
  { value: 'cant_attack', label: "Can't Attack" },
  { value: 'cant_block', label: "Can't Block" },
  { value: 'cant_be_blocked', label: "Can't Be Blocked" },
];

const PT_STEP_OPTIONS = Array.from({ length: 11 }, (_, index) => index - 5);

const MODIFIER_LAYER_MAP: Record<string, number | undefined> = {
  add_keyword: 6,
  remove_keyword: 6,
  cant_attack: 6,
  cant_block: 6,
  cant_be_blocked: 6,
  change_power_toughness: 7,
  set_power_toughness: 7,
  modify_power_toughness_by_same_name: 7,
  add_type: 4,
  remove_type: 4,
  set_types: 4,
  add_color: 5,
  remove_color: 5,
  set_colors: 5,
  change_control: 2,
  ignore_legend_rule: 6,
};

const TYPE_OPTIONS = PERMANENT_TYPES.filter((opt) => opt.value !== 'any');

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
  const modifierType = (body.modifier as any)?.type ?? 'add_keyword';
  const derivedLayer = MODIFIER_LAYER_MAP[modifierType] ?? body.layer ?? 6;
  const derivedLayerLabel = LAYER_OPTIONS.find((opt) => opt.value === derivedLayer)?.label ?? `Layer ${derivedLayer}`;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Layer
          </label>
          <div className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-[color:var(--theme-card-bg)] px-2 py-1 text-sm text-[color:var(--theme-text-secondary)]">
            {derivedLayerLabel}
          </div>
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
          value={modifierType}
          onChange={(e) => {
            const nextType = e.target.value;
            const nextLayer = MODIFIER_LAYER_MAP[nextType] ?? derivedLayer;
            updateBody({
              layer: nextLayer,
              modifier: { ...(body.modifier as any), type: nextType },
            });
          }}
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

      {((body.modifier as any)?.type === 'add_type' || (body.modifier as any)?.type === 'remove_type') && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Type
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={(body.modifier as any)?.typeName ?? 'creature'}
            onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), typeName: e.target.value } })}
          >
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {(body.modifier as any)?.type === 'set_types' && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Types
          </label>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {TYPE_OPTIONS.map((opt) => {
              const selected = Array.isArray((body.modifier as any)?.types)
                ? (body.modifier as any).types.includes(opt.value)
                : false;
              return (
                <label key={opt.value} className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={(e) => {
                      const current = Array.isArray((body.modifier as any)?.types) ? [...(body.modifier as any).types] : [];
                      const next = e.target.checked
                        ? [...current, opt.value]
                        : current.filter((value) => value !== opt.value);
                      updateBody({ modifier: { ...(body.modifier as any), types: next } });
                    }}
                  />
                  {opt.label}
                </label>
              );
            })}
          </div>
        </div>
      )}

      {((body.modifier as any)?.type === 'add_color' || (body.modifier as any)?.type === 'remove_color') && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Color
          </label>
          <select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={(body.modifier as any)?.color ?? 'W'}
            onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), color: e.target.value } })}
          >
            {COLOR_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {(body.modifier as any)?.type === 'set_colors' && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Colors
          </label>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {COLOR_OPTIONS.map((opt) => {
              const selected = Array.isArray((body.modifier as any)?.colors)
                ? (body.modifier as any).colors.includes(opt.value)
                : false;
              return (
                <label key={opt.value} className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={(e) => {
                      const current = Array.isArray((body.modifier as any)?.colors) ? [...(body.modifier as any).colors] : [];
                      const next = e.target.checked
                        ? [...current, opt.value]
                        : current.filter((value) => value !== opt.value);
                      updateBody({ modifier: { ...(body.modifier as any), colors: next } });
                    }}
                  />
                  {opt.label}
                </label>
              );
            })}
          </div>
        </div>
      )}

      {(body.modifier as any)?.type === 'modify_power_toughness_by_same_name' && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Power per Match
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={(body.modifier as any)?.powerPer ?? 1}
                onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), powerPer: Number(e.target.value) } })}
              >
                {PT_STEP_OPTIONS.map((value) => (
                  <option key={`pt-power-${value}`} value={value}>
                    {value >= 0 ? `+${value}` : value}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                Toughness per Match
              </label>
              <select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={(body.modifier as any)?.toughnessPer ?? 1}
                onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), toughnessPer: Number(e.target.value) } })}
              >
                {PT_STEP_OPTIONS.map((value) => (
                  <option key={`pt-toughness-${value}`} value={value}>
                    {value >= 0 ? `+${value}` : value}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              id="countOther"
              type="checkbox"
              checked={(body.modifier as any)?.countOther ?? true}
              onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), countOther: e.target.checked } })}
            />
            <label htmlFor="countOther" className="text-xs text-[color:var(--theme-text-secondary)]">
              Count other creatures only
            </label>
          </div>
          <div className="flex items-center gap-2">
            <input
              id="excludeTargetTokens"
              type="checkbox"
              checked={(body.modifier as any)?.excludeTargetTokens ?? true}
              onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), excludeTargetTokens: e.target.checked } })}
            />
            <label htmlFor="excludeTargetTokens" className="text-xs text-[color:var(--theme-text-secondary)]">
              Exclude token creatures as targets
            </label>
          </div>
          <div className="text-xs text-[color:var(--theme-text-muted)]">
            Uses the target creature's name to count matching creatures you control.
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
