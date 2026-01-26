import type { UnifiedEffect } from '@/lib/unifiedEffect';
import { ZONE_OPTIONS } from '@/lib/effectTypes';
import { Select } from '@/components/ui/Select';

interface ReplacementConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
  kind: 'replacement' | 'prevention';
}

const REPLACEMENT_EVENT_OPTIONS = [
  { value: 'replace_destroy', label: 'Replace Destroy' },
  { value: 'replace_draw', label: 'Replace Draw' },
  { value: 'replace_discard', label: 'Replace Discard' },
  { value: 'replace_life_loss', label: 'Replace Life Loss' },
  { value: 'replace_life_gain', label: 'Replace Life Gain' },
  { value: 'replace_sacrifice', label: 'Replace Sacrifice' },
  { value: 'replace_zone_change', label: 'Replace Zone Change' },
  { value: 'replace_damage', label: 'Replace Damage' },
  { value: 'replace_counter', label: 'Replace Counter (being added)' },
  { value: 'replace_enter_battlefield', label: 'Replace Enter Battlefield' },
];

const PREVENTION_EVENT_OPTIONS = [
  { value: 'damage', label: 'Damage' },
  { value: 'combat_damage', label: 'Combat Damage' },
  { value: 'noncombat_damage', label: 'Noncombat Damage' },
  { value: 'destroy', label: 'Destroy' },
  { value: 'exile', label: 'Exile' },
  { value: 'sacrifice', label: 'Sacrifice' },
  { value: 'discard', label: 'Discard' },
  { value: 'life_loss', label: 'Life Loss' },
];

export function ReplacementConfig({ effect, onChange, kind }: ReplacementConfigProps) {
  const body = effect.effect.kind === kind ? effect.effect : null;
  if (!body) {
    return null;
  }

  if (kind === 'replacement') {
    const replaces = body.replaces as Record<string, unknown>;
    const withPayload = (body as any).with as Record<string, unknown>;
    const eventType = (replaces?.event as string) ?? 'replace_destroy';
    return (
      <div className="space-y-4">
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Replaces Event
          </label>
          <Select
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            value={eventType}
            onChange={(e) =>
              onChange({
                ...effect,
                effect: {
                  ...body,
                  replaces: { ...replaces, event: e.target.value },
                },
              })
            }
          >
            {REPLACEMENT_EVENT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </Select>
        </div>
        {eventType === 'replace_zone_change' && (
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                From Zone
              </label>
              <Select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={(withPayload?.fromZone as string) ?? 'battlefield'}
                onChange={(e) =>
                  onChange({
                    ...effect,
                    effect: { ...body, with: { ...withPayload, fromZone: e.target.value } } as any,
                  })
                }
              >
                {ZONE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
                To Zone
              </label>
              <Select
                className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
                value={(withPayload?.toZone as string) ?? 'exile'}
                onChange={(e) =>
                  onChange({
                    ...effect,
                    effect: { ...body, with: { ...withPayload, toZone: e.target.value } } as any,
                  })
                }
              >
                {ZONE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>
        )}
        {(eventType === 'replace_damage' || eventType === 'replace_life_loss') && (
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              New Amount
            </label>
            <input
              type="number"
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={(withPayload?.amount as number) ?? 0}
              onChange={(e) =>
                onChange({
                  ...effect,
                  effect: { ...body, with: { ...withPayload, amount: Number(e.target.value) } } as any,
                })
              }
            />
          </div>
        )}
      </div>
    );
  }

  const prevents = (body as any).prevents as Record<string, unknown>;
  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Prevents Event
        </label>
        <Select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={(prevents?.event as string) ?? 'damage'}
          onChange={(e) =>
            onChange({
              ...effect,
              effect: {
                ...body,
                prevents: { ...prevents, event: e.target.value },
              } as any,
            })
          }
        >
          {PREVENTION_EVENT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      </div>
      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Amount
        </label>
        <input
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          type="number"
          value={(body as any).amount ?? 1}
          onChange={(e) =>
            onChange({
              ...effect,
              effect: { ...body, amount: Number(e.target.value) } as any,
            })
          }
        />
      </div>
    </div>
  );
}
