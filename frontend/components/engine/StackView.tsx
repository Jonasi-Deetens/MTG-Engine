'use client';

import { Card } from '@/components/ui/Card';
import { EngineCardMap, EngineGameObjectSnapshot, EngineStackItemSnapshot } from '@/lib/engine';

interface StackViewProps {
  stack: EngineStackItemSnapshot[];
  objects: EngineGameObjectSnapshot[];
  cardMap: EngineCardMap;
  targetChecks?: Record<number, { legal: boolean; issues: string[] }>;
}

export function StackView({ stack, objects, cardMap, targetChecks }: StackViewProps) {
  const objectMap = new Map(objects.map((obj) => [obj.id, obj]));

  const getStackLabel = (item: EngineStackItemSnapshot) => {
    if (item.kind === 'spell') {
      const objectId = item.payload?.object_id as string | undefined;
      if (objectId) {
        const card = cardMap[objectId];
        const obj = objectMap.get(objectId);
        return card?.name || obj?.name || objectId;
      }
    }
    return item.kind;
  };

  const getTargetSummary = (item: EngineStackItemSnapshot) => {
    const context = item.payload?.context as Record<string, any> | undefined;
    if (!context?.targets) return null;
    const targets = context.targets as Record<string, any>;
    const objectIds = Array.isArray(targets.targets) ? targets.targets : targets.target ? [targets.target] : [];
    const playerIds = Array.isArray(targets.target_players)
      ? targets.target_players
      : targets.target_player !== undefined
        ? [targets.target_player]
        : [];
    const spellIds = Array.isArray(targets.spell_targets)
      ? targets.spell_targets
      : targets.spell_target
        ? [targets.spell_target]
        : [];
    const objectLabels = objectIds.map((id) => cardMap[id]?.name || objectMap.get(id)?.name || id);
    const playerLabels = playerIds.map((id) => `Player ${Number(id) + 1}`);
    const spellLabels = spellIds.map((id) => cardMap[id]?.name || objectMap.get(id)?.name || id);
    const parts = [
      objectLabels.length > 0 ? `Objects: ${objectLabels.join(', ')}` : null,
      playerLabels.length > 0 ? `Players: ${playerLabels.join(', ')}` : null,
      spellLabels.length > 0 ? `Spells: ${spellLabels.join(', ')}` : null,
    ].filter(Boolean);
    return parts.length > 0 ? parts.join(' · ') : null;
  };

  const getTargetStatus = (item: EngineStackItemSnapshot, index: number) => {
    if (targetChecks && targetChecks[index]) {
      return { isLegal: targetChecks[index].legal, invalidCount: null, issues: targetChecks[index].issues };
    }
    const context = item.payload?.context as Record<string, any> | undefined;
    if (!context?.targets) return null;
    const targets = context.targets as Record<string, any>;
    const objectIds = Array.isArray(targets.targets) ? targets.targets : targets.target ? [targets.target] : [];
    const playerIds = Array.isArray(targets.target_players)
      ? targets.target_players
      : targets.target_player !== undefined
        ? [targets.target_player]
        : [];
    const spellIds = Array.isArray(targets.spell_targets)
      ? targets.spell_targets
      : targets.spell_target
        ? [targets.spell_target]
        : [];

    const validObjectTargets = objectIds.filter((id) => {
      const obj = objectMap.get(id);
      return !!obj && obj.zone === 'battlefield';
    });
    const validPlayerTargets = playerIds.filter((id) => Number.isFinite(id) && id >= 0 && id < objects.length);
    const stackSpellIds = new Set(
      stack
        .filter((entry) => entry.kind === 'spell')
        .map((entry) => entry.payload?.object_id)
        .filter((id): id is string => Boolean(id))
    );
    const validSpellTargets = spellIds.filter((id) => stackSpellIds.has(id));

    const hasAnyTargets = objectIds.length + playerIds.length + spellIds.length > 0;
    if (!hasAnyTargets) return null;

    const hasLegalTarget =
      validObjectTargets.length > 0 ||
      validPlayerTargets.length > 0 ||
      validSpellTargets.length > 0;

    return {
      isLegal: hasLegalTarget,
      invalidCount:
        objectIds.length +
        playerIds.length +
        spellIds.length -
        (validObjectTargets.length + validPlayerTargets.length + validSpellTargets.length),
      issues: [],
    };
  };

  return (
    <Card variant="bordered" className="p-4 space-y-2">
      <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Stack</div>
      {stack.length === 0 && (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">Stack is empty</div>
      )}
      {stack.map((item, index) => (
        <div key={`${item.kind}-${index}`} className="text-xs text-[color:var(--theme-text-secondary)] space-y-1">
          <div>
          {getStackLabel(item)} · controller {item.controller_id ?? 'N/A'}
          </div>
          {getTargetSummary(item) && (
            <div className="text-[color:var(--theme-text-secondary)]">{getTargetSummary(item)}</div>
          )}
          {getTargetStatus(item, index) && (
            <div
              className={
                getTargetStatus(item, index)?.isLegal
                  ? 'text-[color:var(--theme-status-success)]'
                  : 'text-[color:var(--theme-status-error)]'
              }
            >
              {getTargetStatus(item, index)?.isLegal
                ? 'Targets legal'
                : `Targets illegal${getTargetStatus(item, index)?.invalidCount ? ' (some invalid)' : ''}`}
            </div>
          )}
          {getTargetStatus(item, index)?.issues?.length > 0 && (
            <div className="text-[color:var(--theme-text-secondary)]">
              {getTargetStatus(item, index)?.issues
                .map((issue) => {
                  const [maybeId, rest] = issue.split(':');
                  const id = maybeId?.trim();
                  if (id && objectMap.has(id)) {
                    const label = cardMap[id]?.name || objectMap.get(id)?.name || id;
                    return `${label}:${rest ? rest : ''}`;
                  }
                  if (id && id.startsWith('Player')) {
                    return issue;
                  }
                  if (id && !Number.isNaN(Number(id))) {
                    const playerIndex = Number(id) + 1;
                    return `Player ${playerIndex}:${rest ? rest : ''}`;
                  }
                  if (id && stack.some((entry) => entry.payload?.object_id === id)) {
                    const label = cardMap[id]?.name || objectMap.get(id)?.name || id;
                    return `${label}:${rest ? rest : ''}`;
                  }
                  return issue;
                })
                .join(' ')}
            </div>
          )}
        </div>
      ))}
    </Card>
  );
}
