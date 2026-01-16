"use client";

import { useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, EngineActionRequest } from '@/lib/engine';
import { Card } from '@/components/ui/Card';
import { DeckSetupPanel } from '@/components/engine/DeckSetupPanel';
import { PlayerZone } from '@/components/engine/PlayerZone';
import { StackView } from '@/components/engine/StackView';
import { TurnStatusCard } from '@/components/engine/TurnStatusCard';
import { ActionsPanel } from '@/components/engine/ActionsPanel';
import { ReplacementChoicePanel } from '@/components/engine/ReplacementChoicePanel';
import { useAbilityGraphs } from '@/hooks/useAbilityGraphs';
import { useTargeting } from '@/hooks/useTargeting';
import { useCasting } from '@/hooks/useCasting';
import { useCombatSelection } from '@/hooks/useCombatSelection';
import { useEngineActions } from '@/hooks/useEngineActions';
import { useGameSetup } from '@/hooks/useGameSetup';
import { useTurnReset } from '@/hooks/useTurnReset';
import {
  buildEnterChoiceConfig,
  buildEnterChoiceDefaults,
  buildEnterChoiceErrors,
  buildEnterChoiceTargetOptions,
} from '@/lib/enterChoices';

export default function PlayPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<EngineGameStateSnapshot | null>(null);
  const [cardMap, setCardMap] = useState<EngineCardMap>({});
  const [priorityPlayer, setPriorityPlayer] = useState<number | null>(null);
  const [selectedHandId, setSelectedHandId] = useState<string | null>(null);
  const [selectedBattlefieldId, setSelectedBattlefieldId] = useState<string | null>(null);
  const [replacementChoices, setReplacementChoices] = useState<Record<string, string>>({});
  const [enterChoices, setEnterChoices] = useState<Record<string, string>>({});
  const { abilityGraphs, loadAbilityGraphForObject } = useAbilityGraphs({
    gameState,
    cardMap,
    setGameState,
  });

  const { deckList, selectedDeckIds, loading: setupLoading, canStart, handleSelectDeck, startGame } = useGameSetup({
    setGameState,
    setCardMap,
    setPriorityPlayer,
    setError,
  });


  const {
    selectedAttackers,
    selectedBlockers,
    selectedBlockerOrder,
    activeAttackerId,
    setActiveAttackerId,
    selectedDefenderId,
    setSelectedDefenderId,
    toggleAttacker,
    toggleBlocker,
    blockersPayload,
    activeBlockerOrder,
    setSelectedBlockerOrder,
  } = useCombatSelection({ gameState });


  const replacementConflicts = useMemo(() => {
    if (!gameState) return [];
    const globalEffects = (gameState.replacement_effects ?? []).filter(
      (effect) => effect?.type === 'replace_zone_change'
    );
    const zoneLabels: Record<string, string> = {
      battlefield: 'Battlefield',
      graveyard: 'Graveyard',
      hand: 'Hand',
      library: 'Library',
      exile: 'Exile',
      command: 'Command',
      stack: 'Stack',
    };
    const getZoneLabel = (zone?: string) => (zone ? zoneLabels[zone] ?? zone : 'Any');
    return gameState.objects
      .map((obj) => {
        const localEffects = (obj as any).temporary_effects || [];
        const all = [...localEffects, ...globalEffects].filter((effect) => {
          if (effect?.type !== 'replace_zone_change') return false;
          if (effect.object_id && effect.object_id !== obj.id) return false;
          if (!effect.from_zone || !effect.to_zone) return false;
          return true;
        });
        if (all.length < 2) return null;
        const byKey = new Map<string, { key: string; fromZone: string; toZone: string; options: any[] }>();
        all.forEach((effect) => {
          const fromZone = effect.from_zone;
          const toZone = effect.to_zone;
          const key = `${obj.id}:${fromZone}:${toZone}`;
        const entry = byKey.get(key) || { key, fromZone, toZone, options: [] as any[] };
          entry.options.push(effect);
          byKey.set(key, entry);
        });
        return Array.from(byKey.values()).map((entry) => ({
          obj,
          key: entry.key,
          fromZone: entry.fromZone,
          toZone: entry.toZone,
          fromLabel: getZoneLabel(entry.fromZone),
          toLabel: getZoneLabel(entry.toZone),
          options: entry.options,
        }));
      })
      .flat()
      .filter(Boolean) as Array<{
        obj: any;
        key: string;
        fromZone: string;
        toZone: string;
        fromLabel: string;
        toLabel: string;
        options: Array<Record<string, any>>;
      }>;
  }, [gameState]);



  const { runEngineAction } = useEngineActions({
    gameState,
    replacementChoices,
    setGameState,
    setPriorityPlayer,
    setLoading,
    setError,
  });

  const currentPriority =
    gameState?.turn.priority_current_index ??
    priorityPlayer ??
    gameState?.turn.active_player_index ??
    0;
  const selectedGraph = selectedHandId ? abilityGraphs[cardMap[selectedHandId]?.card_id ?? ''] : undefined;
  const {
    targetHints,
    selectedTargetObjectIds,
    setSelectedTargetObjectIds,
    selectedTargetPlayerIds,
    setSelectedTargetPlayerIds,
    objectTargetStatus,
    playerTargetStatus,
    stackTargetChecks,
    stackSpellObjects,
    filteredTargetableObjects,
    filteredTargetPlayers,
    shouldUseStackTargets,
  } = useTargeting({
    gameState,
    selectedHandId,
    selectedGraph,
    currentPriority,
  });
  useTurnReset({
    gameState,
    setReplacementChoices,
    setSelectedHandId,
    setSelectedBattlefieldId,
    setSelectedTargetObjectIds,
    setSelectedTargetPlayerIds,
    setActiveAttackerId,
    setSelectedDefenderId,
  });
  const activePlayerIndex = gameState?.turn.active_player_index ?? 0;
  const currentStep = gameState?.turn.step ?? '';
  const isMainPhase = currentStep === 'precombat_main' || currentStep === 'postcombat_main';
  const isDeclareAttackers = currentStep === 'declare_attackers';
  const isDeclareBlockers = currentStep === 'declare_blockers';
  const isCombatDamage = currentStep === 'combat_damage';
  const combatState = gameState?.turn.combat_state;
  const defendingPlayerId = combatState?.defending_player_id ?? selectedDefenderId;
  const isPriorityActivePlayer = currentPriority === activePlayerIndex;
  const isPriorityDefender = defendingPlayerId !== null && currentPriority === defendingPlayerId;

  useEffect(() => {
    if (!gameState) return;
    if (gameState.replacement_choices) {
      setReplacementChoices(gameState.replacement_choices);
    }
    setSelectedHandId(null);
    setSelectedBattlefieldId(null);
    setSelectedTargetObjectIds([]);
    setSelectedTargetPlayerIds([]);
  }, [gameState?.turn.step, gameState?.turn.turn_number]);


  const priorityPlayerState = gameState?.players.find((player) => player.id === currentPriority);
  const manaPool = priorityPlayerState?.mana_pool ?? {};
  const enterChoiceConfig = useMemo(() => buildEnterChoiceConfig(selectedGraph), [selectedGraph]);
  const enterChoiceTargetOptions = useMemo(
    () => buildEnterChoiceTargetOptions(gameState, cardMap),
    [gameState, cardMap]
  );
  const enterChoiceErrors = useMemo(
    () => buildEnterChoiceErrors(enterChoiceConfig, enterChoices),
    [enterChoiceConfig, enterChoices]
  );
  const selectedBattlefieldObject = gameState?.objects.find((obj) => obj.id === selectedBattlefieldId);
  const hasActivatedAbility =
    selectedBattlefieldObject?.ability_graphs && selectedBattlefieldObject.ability_graphs.length > 0;

  useEffect(() => {
    if (enterChoiceConfig.length === 0) {
      setEnterChoices({});
      return;
    }
    setEnterChoices((prev) => buildEnterChoiceDefaults(enterChoiceConfig, prev));
  }, [selectedHandId, enterChoiceConfig]);

  const buildCastContext = () => ({
    controller_id: currentPriority,
    source_id: selectedHandId ?? undefined,
    targets: {
      ...(selectedTargetObjectIds.length > 0 ? { target: selectedTargetObjectIds[0] } : {}),
      ...(selectedTargetObjectIds.length > 0
        ? { targets: selectedTargetObjectIds.slice(0, targetHints.maxObjectTargets ?? selectedTargetObjectIds.length) }
        : {}),
      ...(selectedTargetPlayerIds.length > 0 ? { target_player: selectedTargetPlayerIds[0] } : {}),
      ...(selectedTargetPlayerIds.length > 0
        ? { target_players: selectedTargetPlayerIds.slice(0, targetHints.maxPlayerTargets ?? selectedTargetPlayerIds.length) }
        : {}),
      ...(selectedTargetObjectIds.length > 0 ? { spell_target: selectedTargetObjectIds[0] } : {}),
      ...(selectedTargetObjectIds.length > 0
        ? { spell_targets: selectedTargetObjectIds.slice(0, targetHints.maxObjectTargets ?? selectedTargetObjectIds.length) }
        : {}),
    },
    ...(Object.keys(enterChoices).length > 0 ? { choices: { enter_choices: enterChoices } } : {}),
  });
  const {
    preparedCast,
    manaPayment,
    setManaPayment,
    manaPaymentDetail,
    setManaPaymentDetail,
    autoPayMana,
    setAutoPayMana,
    isComplexCost,
    manaPaymentStatus,
    costLabel,
    handlePrepareCast,
    handleFinalizeCast,
  } = useCasting({
    selectedHandId,
    currentPriority,
    abilityGraphs,
    cardMap,
    manaPool,
    buildCastContext,
    runEngineAction,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
          Playtest Commander
        </h1>
        <p className="text-[color:var(--theme-text-secondary)]">
          Select four Commander decks and play using the engine rules.
        </p>
      </div>

      {error && (
        <Card variant="bordered" className="p-4 text-[color:var(--theme-status-error)]">
          {error}
        </Card>
      )}

      {!gameState && (
        <DeckSetupPanel
          deckList={deckList}
          selectedDeckIds={selectedDeckIds}
          loading={setupLoading}
          canStart={canStart}
          onSelectDeck={handleSelectDeck}
          onStart={startGame}
        />
      )}

      {gameState && (
        <div className="space-y-6">
          <TurnStatusCard
            turnNumber={gameState.turn.turn_number}
            phase={gameState.turn.phase}
            step={gameState.turn.step}
            activePlayerIndex={gameState.turn.active_player_index}
            currentPriority={currentPriority}
            loading={loading}
            onPassPriority={() => runEngineAction('pass_priority', { player_id: currentPriority })}
            onAdvanceStep={() => runEngineAction('advance_turn')}
          />

          <ActionsPanel
            loading={loading}
            selectedHandId={selectedHandId}
            selectedBattlefieldId={selectedBattlefieldId}
            preparedCast={preparedCast}
            enterChoiceErrors={enterChoiceErrors}
            manaPaymentErrors={manaPaymentStatus.errors}
            isMainPhase={isMainPhase}
            isPriorityActivePlayer={isPriorityActivePlayer}
            isDeclareAttackers={isDeclareAttackers}
            isDeclareBlockers={isDeclareBlockers}
            isCombatDamage={isCombatDamage}
            isPriorityDefender={isPriorityDefender}
            hasActivatedAbility={!!hasActivatedAbility}
            selectedAttackers={selectedAttackers}
            activeAttackerId={activeAttackerId}
            activeBlockerOrder={activeBlockerOrder}
            defendingPlayerId={defendingPlayerId}
            activePlayerIndex={activePlayerIndex}
            combatState={combatState}
            players={gameState.players}
            cardMap={cardMap}
            onPlayLand={() =>
              runEngineAction('play_land', { player_id: currentPriority, object_id: selectedHandId ?? undefined })
            }
            onPrepareCast={handlePrepareCast}
            onFinalizeCast={handleFinalizeCast}
            onTapForMana={() =>
              runEngineAction('activate_mana_ability', {
                player_id: currentPriority,
                object_id: selectedBattlefieldId ?? undefined,
              })
            }
            onActivateAbility={() =>
              runEngineAction('activate_ability', {
                player_id: currentPriority,
                object_id: selectedBattlefieldId ?? undefined,
                ability_index: 0,
              })
            }
            onDeclareAttackers={() =>
              runEngineAction('declare_attackers', {
                player_id: currentPriority,
                attackers: Array.from(selectedAttackers),
                defending_player_id: defendingPlayerId ?? undefined,
              })
            }
            onDeclareBlockers={() =>
              runEngineAction('declare_blockers', {
                player_id: currentPriority,
                blockers: blockersPayload,
              })
            }
            onAssignCombatDamage={() => runEngineAction('assign_combat_damage', { player_id: currentPriority })}
            onSelectDefender={(playerId) => setSelectedDefenderId(playerId)}
            onSelectActiveAttacker={setActiveAttackerId}
            onReorderBlockerUp={(index) =>
              setSelectedBlockerOrder((prev) => {
                if (!activeAttackerId) return prev;
                const order = prev[activeAttackerId] ?? [];
                if (index <= 0) return prev;
                const next = [...order];
                [next[index - 1], next[index]] = [next[index], next[index - 1]];
                return { ...prev, [activeAttackerId]: next };
              })
            }
            onReorderBlockerDown={(index) =>
              setSelectedBlockerOrder((prev) => {
                if (!activeAttackerId) return prev;
                const order = prev[activeAttackerId] ?? [];
                if (index >= order.length - 1) return prev;
                const next = [...order];
                [next[index], next[index + 1]] = [next[index + 1], next[index]];
                return { ...prev, [activeAttackerId]: next };
              })
            }
            enterChoiceConfig={enterChoiceConfig}
            enterChoices={enterChoices}
            enterChoiceTargetOptions={enterChoiceTargetOptions}
            onEnterChoiceChange={(choiceType, value) =>
              setEnterChoices((prev) => ({ ...prev, [choiceType]: value }))
            }
            isComplexCost={isComplexCost}
            manaPool={manaPool}
            manaPayment={manaPayment}
            manaPaymentDetail={manaPaymentDetail}
            costLabel={costLabel}
            autoPayMana={autoPayMana}
            onToggleAutoPay={setAutoPayMana}
            onUpdatePaymentDetail={setManaPaymentDetail}
            onUpdateManaPayment={setManaPayment}
            targetObjects={shouldUseStackTargets ? stackSpellObjects : filteredTargetableObjects}
            targetPlayers={shouldUseStackTargets ? [] : filteredTargetPlayers}
            selectedTargetObjectIds={selectedTargetObjectIds}
            selectedTargetPlayerIds={selectedTargetPlayerIds}
            objectLabel={shouldUseStackTargets ? 'Spells on Stack' : 'Objects'}
            maxObjectTargets={targetHints.maxObjectTargets ?? undefined}
            maxPlayerTargets={targetHints.maxPlayerTargets ?? undefined}
            objectTargetStatus={objectTargetStatus}
            playerTargetStatus={playerTargetStatus}
            onChangeTargetObjects={setSelectedTargetObjectIds}
            onChangeTargetPlayers={setSelectedTargetPlayerIds}
            onClearTargets={() => {
              setSelectedTargetObjectIds([]);
              setSelectedTargetPlayerIds([]);
            }}
          />

          <ReplacementChoicePanel
            conflicts={replacementConflicts}
            replacementChoices={replacementChoices}
            cardMap={cardMap}
            onSelectChoice={(key, value) =>
              setReplacementChoices((prev) => ({
                ...prev,
                [key]: value,
              }))
            }
          />

          <StackView
            stack={gameState.stack}
            objects={gameState.objects}
            cardMap={cardMap}
            targetChecks={stackTargetChecks}
          />

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {gameState.players.map((player, index) => (
              <PlayerZone
                key={`player-zone-${player.id}`}
                player={player}
                objects={gameState.objects}
                cardMap={cardMap}
                isActive={gameState.turn.active_player_index === index}
                selectedHandId={player.id === currentPriority ? selectedHandId : null}
                onSelectHand={
                  player.id === currentPriority
                    ? (objectId) => {
                        setSelectedHandId(objectId);
                        loadAbilityGraphForObject(objectId);
                      }
                    : undefined
                }
                selectedBattlefieldIds={
                  isDeclareAttackers && player.id === activePlayerIndex
                    ? selectedAttackers
                    : isDeclareBlockers && player.id === defendingPlayerId
                      ? selectedBlockers[activeAttackerId ?? ''] ?? new Set()
                      : undefined
                }
                onToggleBattlefield={
                  isDeclareAttackers && player.id === activePlayerIndex
                    ? toggleAttacker
                    : isDeclareBlockers && player.id === defendingPlayerId
                      ? toggleBlocker
                      : undefined
                }
                selectedBattlefieldId={
                  !isDeclareAttackers && !isDeclareBlockers && player.id === currentPriority
                    ? selectedBattlefieldId
                    : null
                }
                onSelectBattlefield={
                  !isDeclareAttackers && !isDeclareBlockers && player.id === currentPriority
                    ? (objectId) => {
                        setSelectedBattlefieldId(objectId);
                        loadAbilityGraphForObject(objectId);
                      }
                    : undefined
                }
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
