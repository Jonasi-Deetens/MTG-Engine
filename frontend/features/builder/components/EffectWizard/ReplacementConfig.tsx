import type { UnifiedEffect } from '@/lib/unifiedEffect';

interface ReplacementConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
  kind: 'replacement' | 'prevention';
}

export function ReplacementConfig({ effect, onChange, kind }: ReplacementConfigProps) {
  const body = effect.effect.kind === kind ? effect.effect : null;
  if (!body) {
    return null;
  }

  if (kind === 'replacement') {
    const replaces = body.replaces as Record<string, unknown>;
    const withPayload = (body as any).with as Record<string, unknown>;
    return (
      <div className="space-y-4">
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Replaces Event
          </label>
          <input
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
            placeholder="replace_destroy, replace_draw..."
            value={(replaces?.event as string) ?? ''}
            onChange={(e) =>
              onChange({
                ...effect,
                effect: {
                  ...body,
                  replaces: { ...replaces, event: e.target.value },
                },
              })
            }
          />
        </div>
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Replacement Payload (JSON)
          </label>
          <textarea
            className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-xs"
            rows={4}
            value={JSON.stringify(withPayload ?? {}, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                onChange({ ...effect, effect: { ...body, with: parsed } as any });
              } catch {
                return;
              }
            }}
          />
        </div>
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
        <input
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          placeholder="damage, combat_damage..."
          value={(prevents?.event as string) ?? ''}
          onChange={(e) =>
            onChange({
              ...effect,
              effect: {
                ...body,
                prevents: { ...prevents, event: e.target.value },
              } as any,
            })
          }
        />
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
