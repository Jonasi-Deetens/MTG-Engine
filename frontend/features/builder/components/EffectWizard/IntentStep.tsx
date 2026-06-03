import { Button } from '@/components/ui/Button';

type IntentType =
  | 'triggered'
  | 'activated'
  | 'always_on'
  | 'spell'
  | 'replacement'
  | 'prevention'
  | 'keyword';

interface IntentStepProps {
  onSelect: (intent: IntentType) => void;
  intents?: Array<{ id: IntentType; label: string; description: string }>;
}

const defaultIntents: Array<{ id: IntentType; label: string; description: string }> = [
  { id: 'triggered', label: 'Triggered', description: 'When/Whenever/At...' },
  { id: 'activated', label: 'Activated', description: 'Pay a cost to...' },
  { id: 'always_on', label: 'Always On', description: 'Static/continuous modifier' },
  { id: 'spell', label: 'Spell Effect', description: 'Resolves when a spell resolves' },
  { id: 'replacement', label: 'Replacement', description: 'Instead of...' },
  { id: 'prevention', label: 'Prevention', description: 'Prevent damage or events' },
  { id: 'keyword', label: 'Keyword', description: 'Add keyword ability' },
];

export function IntentStep({ onSelect, intents = defaultIntents }: IntentStepProps) {
  return (
    <div className="space-y-3">
      <p className="text-sm text-[color:var(--theme-text-secondary)]">
        Choose the intent for this effect.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {intents.map((intent) => (
          <Button
            key={intent.id}
            variant="outline"
            className="flex h-auto min-h-[52px] flex-col items-start gap-0.5 text-left py-2"
            onClick={() => onSelect(intent.id)}
          >
            <span className="text-sm font-medium">{intent.label}</span>
            <span className="text-[11px] leading-tight text-[color:var(--theme-text-secondary)] line-clamp-1">
              {intent.description}
            </span>
          </Button>
        ))}
      </div>
    </div>
  );
}
