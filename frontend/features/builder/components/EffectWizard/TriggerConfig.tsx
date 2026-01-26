import type { UnifiedEffect } from '@/lib/unifiedEffect';
import { CARD_TYPE_FILTERS } from '@/lib/effectTypes';
import { Select } from '@/components/ui/Select';

interface TriggerConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

const TRIGGER_EVENTS = [
  'enters_battlefield',
  'leaves_battlefield',
  'dies',
  'attacks',
  'blocks',
  'card_enters',
  'spell_cast',
  'upkeep',
  'draw_step',
  'end_step',
];

const TRIGGER_SCOPES = ['self', 'any', 'you_control', 'opponent_control', 'you', 'opponent'];

/** Scopes where card type filter makes sense (object-based, not self/player) */
const SCOPES_WITH_CARD_TYPE_FILTER = new Set(['any', 'you_control', 'opponent_control']);

/** Events that are phase-based (no object involved, card type irrelevant) */
const PHASE_BASED_EVENTS = new Set(['upkeep', 'draw_step']);

function shouldShowCardTypeFilter(scope: string, event: string): boolean {
  if (PHASE_BASED_EVENTS.has(event)) return false;
  return SCOPES_WITH_CARD_TYPE_FILTER.has(scope);
}

export function TriggerConfig({ effect, onChange }: TriggerConfigProps) {
  const trigger = effect.trigger ?? { event: 'enters_battlefield', scope: 'self' };
  const scope = trigger.scope ?? 'self';
  const event = trigger.event ?? 'enters_battlefield';
  const rawCardTypes = trigger.cardType;
  const selectedCardTypes = Array.isArray(rawCardTypes)
    ? rawCardTypes
    : typeof rawCardTypes === 'string' && rawCardTypes.trim().length > 0
      ? rawCardTypes.split(',').map((value) => value.trim()).filter(Boolean)
      : [];
  const cardTypeOptions = CARD_TYPE_FILTERS.filter((opt) => opt.value !== 'any');
  const showCardTypeFilter = shouldShowCardTypeFilter(scope, event);

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Trigger Event
        </label>
        <Select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={event}
          onChange={(e) => {
            const nextEvent = e.target.value;
            const clearCardType = !shouldShowCardTypeFilter(scope, nextEvent);
            onChange({
              ...effect,
              trigger: {
                ...trigger,
                event: nextEvent,
                cardType: clearCardType ? undefined : trigger.cardType,
              },
            });
          }}
        >
          {TRIGGER_EVENTS.map((evt) => (
            <option key={evt} value={evt}>
              {evt.replace(/_/g, ' ')}
            </option>
          ))}
        </Select>
      </div>

      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Scope
        </label>
        <Select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={scope}
          onChange={(e) => {
            const nextScope = e.target.value;
            const clearCardType = !shouldShowCardTypeFilter(nextScope, event);
            onChange({
              ...effect,
              trigger: {
                ...trigger,
                scope: nextScope,
                cardType: clearCardType ? undefined : trigger.cardType,
              },
            });
          }}
        >
          {TRIGGER_SCOPES.map((scope) => (
            <option key={scope} value={scope}>
              {scope.replace(/_/g, ' ')}
            </option>
          ))}
        </Select>
      </div>

      {showCardTypeFilter && (
        <div>
          <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
            Card Type Filter (optional)
          </label>
          <div className="mt-2 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() =>
                onChange({ ...effect, trigger: { ...trigger, cardType: undefined } })
              }
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                selectedCardTypes.length === 0
                  ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
                  : 'bg-[color:var(--theme-card-hover)] text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] border border-[color:var(--theme-card-border)]'
              }`}
            >
              Any
            </button>
            {cardTypeOptions.map((option) => {
              const isSelected = selectedCardTypes.includes(option.value);
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => {
                    const next = isSelected
                      ? selectedCardTypes.filter((value) => value !== option.value)
                      : [...selectedCardTypes, option.value];
                    onChange({
                      ...effect,
                      trigger: {
                        ...trigger,
                        cardType: next.length ? next : undefined,
                      },
                    });
                  }}
                  className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                    isSelected
                      ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
                      : 'bg-[color:var(--theme-card-hover)] text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] border border-[color:var(--theme-card-border)]'
                  }`}
                >
                  {option.label}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
