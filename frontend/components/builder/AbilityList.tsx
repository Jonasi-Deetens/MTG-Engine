'use client';

// frontend/components/builder/AbilityList.tsx

import { useBuilderStore, TriggeredAbility, ActivatedAbility, StaticAbility, ContinuousAbility, KeywordAbility } from '@/store/builderStore';
import { AbilityCard } from './AbilityCard';
import { Button } from '@/components/ui/Button';

interface AbilityListProps {
  type: 'triggered' | 'activated' | 'static' | 'continuous' | 'keyword';
  onAdd: () => void;
  onEdit: (id: string) => void;
}

export function AbilityList({ type, onAdd, onEdit }: AbilityListProps) {
  const store = useBuilderStore();
  
  let abilities: any[] = [];
  let removeFunction: (id: string) => void;
  
  switch (type) {
    case 'triggered':
      abilities = store.triggeredAbilities;
      removeFunction = store.removeTriggeredAbility;
      break;
    case 'activated':
      abilities = store.activatedAbilities;
      removeFunction = store.removeActivatedAbility;
      break;
    case 'static':
      abilities = store.staticAbilities;
      removeFunction = store.removeStaticAbility;
      break;
    case 'continuous':
      abilities = store.continuousAbilities;
      removeFunction = store.removeContinuousAbility;
      break;
    case 'keyword':
      abilities = store.keywords;
      removeFunction = store.removeKeyword;
      break;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[color:var(--theme-text-primary)] capitalize">
          {type === 'continuous' ? 'Continuous Abilities' : `${type.charAt(0).toUpperCase() + type.slice(1)} Abilities`}
        </h3>
        <Button
          onClick={onAdd}
          variant="primary"
          size="sm"
        >
          + Add {type === 'continuous' ? 'Continuous' : type.charAt(0).toUpperCase() + type.slice(1)}
        </Button>
      </div>
      
      {abilities.length === 0 ? (
        <div className="text-center py-12 text-[color:var(--theme-text-secondary)]">
          <p className="text-sm">No {type} abilities added yet</p>
          <p className="text-xs mt-1">Click "Add" to create one</p>
        </div>
      ) : (
        <div className="space-y-3">
          {abilities.map((ability) => (
            <AbilityCard
              key={ability.id}
              ability={ability}
              type={type}
              onEdit={() => onEdit(ability.id)}
              onDelete={() => removeFunction(ability.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

