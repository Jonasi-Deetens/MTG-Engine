"use client";

import { useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, EngineActionRequest } from '@/lib/engine';
import { Card } from '@/components/ui/Card';
import { DeckSetupPanel } from '@/components/engine/DeckSetupPanel';
import { PlayerZone } from '@/components/engine/PlayerZone';
import { StackView } from '@/components/engine/StackView';
import { TurnStatusCard } from '@/components/engine/TurnStatusCard';
import { ActionsPanel } from '@/components/engine/ActionsPanel';
import { CombatDamagePanel } from '@/components/engine/CombatDamagePanel';
import { ReplacementChoicePanel } from '@/components/engine/ReplacementChoicePanel';
import { useAbilityGraphs } from '@/hooks/useAbilityGraphs';
import { useTargeting } from '@/hooks/useTargeting';
import { useCasting } from '@/hooks/useCasting';
import { useCombatSelection } from '@/hooks/useCombatSelection';
import { useEngineActions } from '@/hooks/useEngineActions';
import { useGameSetup } from '@/hooks/useGameSetup';
import { useTurnReset } from '@/hooks/useTurnReset';
import { useReplacementConflicts } from '@/hooks/useReplacementConflicts';
import { useCastContext } from '@/hooks/useCastContext';
import { useTurnState } from '@/hooks/useTurnState';
import {
  buildDefaultCombatAssignments,
  hasFirstStrikeCombat as computeHasFirstStrikeCombat,
  isEligibleForCombatPass,
} from '@/lib/combatDamage';
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
  const [highlightedReplacementKey, setHighlightedReplacementKey] = useState<string | null>(null);
  const [combatDamageAssignments, setCombatDamageAssignments] = useState<Record<string, Record<string, number>>>({});
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


  const replacementConflicts = useReplacementConflicts(gameState);
  const hasUnresolvedDamageReplacements = useMemo(
    () =>
      replacementConflicts.some(
        (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
      ),
    [replacementConflicts, replacementChoices]
  );
  const unresolvedDamageReplacements = useMemo(
    () =>
      replacementConflicts.filter(
        (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
      ),
    [replacementConflicts, replacementChoices]
  );

  const hasFirstStrikeCombat = useMemo(() => computeHasFirstStrikeCombat(gameState), [gameState]);
  const combatDamagePass = useMemo(() => {
    if (!hasFirstStrikeCombat) return null;
    const resolved = gameState?.turn?.combat_state?.first_strike_resolved;
    return resolved ? 'regular' : 'first_strike';
  }, [gameState, hasFirstStrikeCombat]);
  const hasManualCombatChoices = useMemo(() => {
    if (!gameState?.turn?.combat_state) return false;
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    return gameState.turn.combat_state.attackers.some((attackerId) => {
      const attacker = objectMap.get(attackerId);
      if (!isEligibleForCombatPass(attacker?.keywords, combatDamagePass ?? undefined)) return false;
      const blockers = gameState.turn.combat_state?.blockers?.[attackerId] ?? [];
      if (blockers.length > 1) return true;
      if (blockers.length > 0 && attacker?.keywords?.includes('Trample')) return true;
      return false;
    });
  }, [combatDamagePass, gameState]);
  useEffect(() => {
    if (unresolvedDamageReplacements.length === 0) {
      setHighlightedReplacementKey(null);
      return;
    }
    if (!highlightedReplacementKey || !unresolvedDamageReplacements.some((entry) => entry.key === highlightedReplacementKey)) {
      setHighlightedReplacementKey(unresolvedDamageReplacements[0].key);
    }
  }, [highlightedReplacementKey, unresolvedDamageReplacements]);



  const { runEngineAction } = useEngineActions({
    gameState,
    replacementChoices,
    setGameState,
    setPriorityPlayer,
    setLoading,
    setError,
  });

  const {
    currentPriority,
    activePlayerIndex,
    isMainPhase,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    combatState,
    isPriorityActivePlayer,
    isPriorityDefender,
  } = useTurnState({ gameState, priorityPlayer });
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
  const defendingPlayerId = combatState?.defending_player_id ?? selectedDefenderId;

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

  useEffect(() => {
    if (!gameState) return;
    if (gameState.turn.step === 'combat_damage') {
      setCombatDamageAssignments(buildDefaultCombatAssignments(gameState, combatDamagePass ?? undefined));
      return;
    }
    if (Object.keys(combatDamageAssignments).length > 0) {
      setCombatDamageAssignments({});
    }
  }, [combatDamagePass, gameState?.turn.step, gameState?.turn.turn_number]);

  const { buildCastContext } = useCastContext({
    currentPriority,
    selectedHandId,
    selectedTargetObjectIds,
    selectedTargetPlayerIds,
    maxObjectTargets: targetHints.maxObjectTargets ?? undefined,
    maxPlayerTargets: targetHints.maxPlayerTargets ?? undefined,
    enterChoices,
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
                context: buildCastContext(selectedBattlefieldId ?? undefined),
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
            onAssignCombatDamage={() =>
              runEngineAction('assign_combat_damage', {
                player_id: currentPriority,
                ...(hasManualCombatChoices ? { damage_assignments: combatDamageAssignments } : {}),
                ...(combatDamagePass ? { combat_damage_pass: combatDamagePass } : {}),
              })
            }
            hasUnresolvedDamageReplacements={hasUnresolvedDamageReplacements}
            unresolvedDamageReplacements={unresolvedDamageReplacements}
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

          <CombatDamagePanel
            active={isCombatDamage}
            combatState={combatState}
            objects={gameState.objects}
            cardMap={cardMap}
            defendingPlayerId={defendingPlayerId ?? null}
            assignments={combatDamageAssignments}
            damagePass={combatDamagePass}
            onUpdateAssignment={(attackerId, targetId, value) =>
              setCombatDamageAssignments((prev) => ({
                ...prev,
                [attackerId]: { ...(prev[attackerId] ?? {}), [targetId]: value },
              }))
            }
          />

          <ReplacementChoicePanel
            conflicts={replacementConflicts}
            replacementChoices={replacementChoices}
            highlightKey={highlightedReplacementKey}
            onNextHighlight={() => {
              if (unresolvedDamageReplacements.length === 0) return;
              const keys = unresolvedDamageReplacements.map((entry) => entry.key);
              const currentIndex = highlightedReplacementKey ? keys.indexOf(highlightedReplacementKey) : -1;
              const nextIndex = (currentIndex + 1) % keys.length;
              setHighlightedReplacementKey(keys[nextIndex]);
            }}
            onSelectChoice={(key, value) =>
              {
                setReplacementChoices((prev) => ({
                  ...prev,
                  [key]: value,
                }));
                const remaining = unresolvedDamageReplacements
                  .map((entry) => entry.key)
                  .filter((entryKey) => entryKey !== key);
                setHighlightedReplacementKey(remaining[0] ?? null);
              }
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
