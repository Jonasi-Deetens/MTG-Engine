'use client';

// frontend/components/builder/AbilityTreeView.tsx

import { useBuilderStore } from '@/store/builderStore';
import { formatEffect } from '@/lib/effectTypes';
import { formatCondition } from '@/lib/conditionTypes';

export function AbilityTreeView() {
  const {
    triggeredAbilities,
    activatedAbilities,
    staticAbilities,
    continuousAbilities,
    keywords,
  } = useBuilderStore();

  const totalAbilities =
    triggeredAbilities.length +
    activatedAbilities.length +
    staticAbilities.length +
    continuousAbilities.length +
    keywords.length;

  if (totalAbilities === 0) {
    return (
      <div className="text-center py-8 text-[color:var(--theme-text-secondary)]">
        <p className="text-sm">No abilities added yet</p>
        <p className="text-xs mt-1">Add abilities using the tabs above to see them here</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Triggered Abilities */}
      {triggeredAbilities.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-[color:var(--theme-status-info)] mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[color:var(--theme-status-info)]"></span>
            Triggered Abilities ({triggeredAbilities.length})
          </h3>
          <div className="space-y-4 ml-4">
            {triggeredAbilities.map((ability) => (
              <div key={ability.id} className="border-l-2 border-[color:var(--theme-border-default)] pl-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[color:var(--theme-text-secondary)]">Event:</span>
                  <span className="text-sm text-[color:var(--theme-text-primary)] font-medium">
                    {ability.event === 'card_enters' 
                      ? (() => {
                          const cardTypeText = ability.cardType ? `${ability.cardType} ` : '';
                          const zoneText = ability.entersWhere || 'Zone';
                          const fromText = ability.entersFrom ? ` (from ${ability.entersFrom})` : '';
                          return `${cardTypeText}Enters ${zoneText}${fromText}`;
                        })()
                      : ability.event === 'spell_cast'
                      ? 'Spell Cast'
                      : ability.event.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                  </span>
                </div>
                {ability.condition && (
                  <div className="ml-4 border-l-2 border-[color:var(--theme-border-default)] pl-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[color:var(--theme-text-secondary)]">If:</span>
                      <span className="text-sm text-[color:var(--theme-text-secondary)]">{formatCondition(ability.condition)}</span>
                    </div>
                  </div>
                )}
                <div className="ml-4 border-l-2 border-[color:var(--theme-accent-primary)] pl-3 space-y-1">
                  <span className="text-xs text-[color:var(--theme-accent-primary)]">Effects:</span>
                  {ability.effects.map((effect, idx) => (
                    <div key={idx} className="text-sm text-[color:var(--theme-text-primary)]">
                      • {formatEffect(effect)}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activated Abilities */}
      {activatedAbilities.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-[color:var(--theme-status-warning)] mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[color:var(--theme-status-warning)]"></span>
            Activated Abilities ({activatedAbilities.length})
          </h3>
          <div className="space-y-4 ml-4">
            {activatedAbilities.map((ability) => (
              <div key={ability.id} className="border-l-2 border-[color:var(--theme-border-default)] pl-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[color:var(--theme-text-secondary)]">Cost:</span>
                  <span className="text-sm text-[color:var(--theme-text-primary)] font-mono">{ability.cost}</span>
                </div>
                <div className="ml-4 border-l-2 border-[color:var(--theme-accent-primary)] pl-3">
                  <span className="text-xs text-[color:var(--theme-accent-primary)]">Effect:</span>
                  <div className="text-sm text-[color:var(--theme-text-primary)] mt-1">{formatEffect(ability.effect)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Static Abilities */}
      {staticAbilities.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-[color:var(--theme-status-success)] mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[color:var(--theme-status-success)]"></span>
            Static Abilities ({staticAbilities.length})
          </h3>
          <div className="space-y-4 ml-4">
            {staticAbilities.map((ability) => (
              <div key={ability.id} className="border-l-2 border-[color:var(--theme-border-default)] pl-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[color:var(--theme-text-secondary)]">Applies to:</span>
                  <span className="text-sm text-[color:var(--theme-text-primary)]">
                    {ability.appliesTo.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                  </span>
                </div>
                <div className="ml-4 border-l-2 border-[color:var(--theme-status-success)] pl-3">
                  <span className="text-sm text-[color:var(--theme-text-primary)]">{ability.effect}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Continuous Abilities */}
      {continuousAbilities.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-[color:var(--theme-accent-secondary)] mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[color:var(--theme-accent-secondary)]"></span>
            Continuous Abilities ({continuousAbilities.length})
          </h3>
          <div className="space-y-4 ml-4">
            {continuousAbilities.map((ability) => (
              <div key={ability.id} className="border-l-2 border-[color:var(--theme-border-default)] pl-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[color:var(--theme-text-secondary)]">Applies to:</span>
                  <span className="text-sm text-[color:var(--theme-text-primary)]">
                    {ability.appliesTo.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                  </span>
                </div>
                <div className="ml-4 border-l-2 border-[color:var(--theme-accent-secondary)] pl-3">
                  <span className="text-sm text-[color:var(--theme-text-primary)]">{ability.effect}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Keywords */}
      {keywords.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-[color:var(--theme-accent-primary)] mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[color:var(--theme-accent-primary)]"></span>
            Keywords ({keywords.length})
          </h3>
          <div className="space-y-3 ml-4">
            {keywords.map((keyword) => (
              <div key={keyword.id} className="border-l-2 border-[color:var(--theme-accent-primary)] pl-4">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm text-[color:var(--theme-text-primary)] font-semibold capitalize">
                    {keyword.keyword}
                  </span>
                  {keyword.cost && (
                    <span className="text-xs text-[color:var(--theme-text-secondary)] font-mono">({keyword.cost})</span>
                  )}
                  {keyword.number !== undefined && (
                    <span className="text-xs text-[color:var(--theme-text-secondary)]">{keyword.number}</span>
                  )}
                  {keyword.lifeCost !== undefined && (
                    <span className="text-xs text-[color:var(--theme-text-secondary)]">Pay {keyword.lifeCost} life</span>
                  )}
                  {keyword.sacrificeCost && (
                    <span className="text-xs text-[color:var(--theme-text-secondary)]">Sacrifice</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


