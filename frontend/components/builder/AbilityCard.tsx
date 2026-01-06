'use client';

// frontend/components/builder/AbilityCard.tsx

import { TriggeredAbility, ActivatedAbility, StaticAbility, ContinuousAbility, KeywordAbility } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { formatEffect } from '@/lib/effectTypes';
import { formatCondition } from '@/lib/conditionTypes';

interface AbilityCardProps {
  ability: TriggeredAbility | ActivatedAbility | StaticAbility | ContinuousAbility | KeywordAbility;
  type: 'triggered' | 'activated' | 'static' | 'continuous' | 'keyword';
  onEdit: () => void;
  onDelete: () => void;
}

function getAbilitySummary(ability: any, type: string): string {
  switch (type) {
    case 'triggered': {
      const a = ability as TriggeredAbility;
      const eventMap: Record<string, string> = {
        enters_battlefield: 'When this enters the battlefield',
        dies: 'When this dies',
        becomes_target: 'When this becomes the target',
        attacks: 'Whenever this attacks',
        blocks: 'Whenever this blocks',
        deals_damage: 'Whenever this deals damage',
        takes_damage: 'Whenever this takes damage',
        card_enters: (() => {
          const cardTypeText = a.cardType ? `a ${a.cardType}` : 'a card';
          const zoneText = a.entersWhere || 'zone';
          const fromText = a.entersFrom ? ` from ${a.entersFrom}` : '';
          return `Whenever ${cardTypeText} enters the ${zoneText}${fromText}`;
        })(),
        spell_cast: 'Whenever you cast a spell',
      };
      const eventText = eventMap[a.event] || `When ${a.event}`;
      const effectText = a.effects.map((e) => formatEffect(e).toLowerCase()).join(', ');
      const conditionText = a.condition ? `, if ${formatCondition(a.condition).toLowerCase()}` : '';
      return `${eventText}${conditionText}, ${effectText}`;
    }
    case 'activated': {
      const a = ability as ActivatedAbility;
      const effectText = formatEffect(a.effect).toLowerCase();
      return `${a.cost}: ${effectText}`;
    }
    case 'static': {
      const a = ability as StaticAbility;
      return `${a.appliesTo}: ${a.effect}`;
    }
    case 'continuous': {
      const a = ability as ContinuousAbility;
      return `${a.appliesTo}: ${a.effect}`;
    }
    case 'keyword': {
      const a = ability as KeywordAbility;
      let text = a.keyword;
      if (a.cost) text += ` ${a.cost}`;
      if (a.number !== undefined) text += ` ${a.number}`;
      return text;
    }
    default:
      return 'Unknown ability';
  }
}

function getTypeBadgeColor(type: string): string {
  switch (type) {
    case 'triggered':
      return 'bg-blue-600';
    case 'activated':
      return 'bg-purple-600';
    case 'static':
      return 'bg-green-600';
    case 'continuous':
      return 'bg-teal-600';
    case 'keyword':
      return 'bg-amber-600';
    default:
      return 'bg-slate-600';
  }
}

export function AbilityCard({ ability, type, onEdit, onDelete }: AbilityCardProps) {
  const summary = getAbilitySummary(ability, type);
  const badgeColor = getTypeBadgeColor(type);

  return (
    <div className="bg-slate-700 rounded-lg p-4 border border-slate-600 hover:border-slate-500 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 rounded text-xs font-semibold text-white ${badgeColor}`}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </span>
          </div>
          <p className="text-sm text-slate-200 line-clamp-2">{summary}</p>
        </div>
        <div className="flex gap-2 shrink-0">
          <Button
            onClick={onEdit}
            variant="secondary"
            size="xs"
          >
            Edit
          </Button>
          <Button
            onClick={onDelete}
            variant="danger"
            size="xs"
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}

