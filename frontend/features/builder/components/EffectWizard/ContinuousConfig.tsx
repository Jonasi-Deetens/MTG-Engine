import type { UnifiedEffect } from '@/lib/unifiedEffect';

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

const APPLIES_TO_OPTIONS = ['self', 'creatures_you_control', 'all_creatures', 'all_permanents'];

const DURATION_OPTIONS = [
  { value: 'while_in_zone', label: 'While in zone' },
  { value: 'until_end_of_turn', label: 'Until end of turn' },
  { value: 'until_end_of_combat', label: 'Until end of combat' },
  { value: 'until_your_next_turn', label: 'Until your next turn' },
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
              <option key={opt} value={opt}>
                {opt.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Modifier Type
        </label>
        <input
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          placeholder="add_keyword, change_power_toughness, set_types..."
          value={(body.modifier as any)?.type ?? ''}
          onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), type: e.target.value } })}
        />
      </div>

      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Modifier Value
        </label>
        <input
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          placeholder="keyword, power, toughness..."
          value={(body.modifier as any)?.keyword ?? ''}
          onChange={(e) => updateBody({ modifier: { ...(body.modifier as any), keyword: e.target.value } })}
        />
      </div>

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
            <input
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={(body.duration as any)?.zone ?? 'battlefield'}
              onChange={(e) => updateBody({ duration: { type: 'while_in_zone', zone: e.target.value } })}
            />
          </div>
        )}
      </div>
    </div>
  );
}
