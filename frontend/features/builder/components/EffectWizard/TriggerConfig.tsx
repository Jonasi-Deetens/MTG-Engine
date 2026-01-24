import type { UnifiedEffect } from '@/lib/unifiedEffect';

interface TriggerConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

const TRIGGER_EVENTS = [
  'enters_battlefield',
  'dies',
  'attacks',
  'blocks',
  'card_enters',
  'upkeep',
  'draw_step',
];

const TRIGGER_SCOPES = ['self', 'any', 'you_control', 'opponent_control', 'you', 'opponent'];

export function TriggerConfig({ effect, onChange }: TriggerConfigProps) {
  const trigger = effect.trigger ?? { event: 'enters_battlefield', scope: 'self' };

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Trigger Event
        </label>
        <select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={trigger.event}
          onChange={(e) => onChange({ ...effect, trigger: { ...trigger, event: e.target.value } })}
        >
          {TRIGGER_EVENTS.map((evt) => (
            <option key={evt} value={evt}>
              {evt.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Scope
        </label>
        <select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={trigger.scope ?? 'self'}
          onChange={(e) => onChange({ ...effect, trigger: { ...trigger, scope: e.target.value } })}
        >
          {TRIGGER_SCOPES.map((scope) => (
            <option key={scope} value={scope}>
              {scope.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Card Type Filter (optional)
        </label>
        <input
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          placeholder="creature, aura, land..."
          value={trigger.cardType ?? ''}
          onChange={(e) =>
            onChange({ ...effect, trigger: { ...trigger, cardType: e.target.value || undefined } })
          }
        />
      </div>
    </div>
  );
}
