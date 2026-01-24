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
}

const intents: Array<{ id: IntentType; label: string; description: string }> = [
  { id: 'triggered', label: 'Triggered', description: 'When/Whenever/At...' },
  { id: 'activated', label: 'Activated', description: 'Pay a cost to...' },
  { id: 'always_on', label: 'Always On', description: 'Static/continuous modifier' },
  { id: 'spell', label: 'Spell Effect', description: 'Resolves when a spell resolves' },
  { id: 'replacement', label: 'Replacement', description: 'Instead of...' },
  { id: 'prevention', label: 'Prevention', description: 'Prevent damage or events' },
  { id: 'keyword', label: 'Keyword', description: 'Add keyword ability' },
];

export function IntentStep({ onSelect }: IntentStepProps) {
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
            className="flex flex-col items-start gap-1"
            onClick={() => onSelect(intent.id)}
          >
            <span className="text-sm font-medium">{intent.label}</span>
            <span className="text-xs text-[color:var(--theme-text-secondary)]">
              {intent.description}
            </span>
          </Button>
        ))}
      </div>
    </div>
  );
}
