'use client';

import { useMemo } from 'react';
import { ActionsPanel } from '@/features/game/components/LegacyActionsPanel';
import { CombatDamagePanel } from '@/features/game/components/CombatDamagePanel';
import { ReplacementChoicePanel } from '@/features/game/components/ReplacementChoicePanel';
import { StackView } from '@/features/game/components/StackView';
import { TurnStatusCard } from '@/features/game/components/TurnStatusCard';
import {
  usePlayGame,
  usePlayCombat,
  usePlayChoices,
  usePlaySelection,
  usePlayTurn,
  usePlayTargeting,
  usePlayCasting,
} from '@/app/(protected)/play/PlayProviders';

export function PlayActionsPanel() {
  // Game state
  const { gameState, loading, cardMap, runEngineAction } = usePlayGame();

  // Turn state
  const {
    currentPriority,
    isMainPhase,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    isPriorityActivePlayer,
    isPriorityDefender,
    objectMap,
  } = usePlayTurn();

  // Selection state
  const {
    selectedHandId,
    selectedCommandId,
    selectedBattlefieldId,
    selectedStackIndex,
    setSelectedStackIndex,
  } = usePlaySelection();

  // Combat state
  const {
    selectedAttackers,
    activeAttackerId,
    activeBlockerOrder,
    selectedDefenderId,
    defenderOptions,
    combatState,
    blockersPayload,
    hasManualCombatChoices,
    combatDamageAssignments,
    setCombatDamageAssignments,
    combatDamagePass,
    blockerErrors,
    blockerErrorMap,
    setSelectedDefenderId,
    setActiveAttackerId,
    setSelectedBlockerOrder,
    defendingPlayerId,
    defendingObjectId,
  } = usePlayCombat();

  // Choices state
  const {
    enterChoiceConfig,
    enterChoices,
    enterChoiceErrors,
    enterChoiceTargetOptions,
    setEnterChoices,
    modalChoiceConfig,
    selectedModalModes,
    modalChoiceErrors,
    handleToggleModalMode,
    entwineSelected,
    replacementConflicts,
    replacementChoices,
    highlightedReplacementKey,
    setHighlightedReplacementKey,
    setReplacementChoices,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
    autoPayWard,
    setAutoPayWard,
    wardTargets,
    wardPayments,
    wardPaymentDetails,
    wardPaymentErrors,
    hasWardPaymentErrors,
    wardPaymentsPayload,
    setWardPayments,
    setWardPaymentDetails,
  } = usePlayChoices();

  // Targeting state
  const {
    targetHints,
    shouldUseStackTargets,
    stackSpellObjects,
    filteredTargetableObjects,
    filteredTargetPlayers,
    resolvedTargetObjectIds,
    resolvedTargetPlayerIds,
    objectTargetStatus,
    playerTargetStatus,
    setSelectedTargetObjectIds,
    setSelectedTargetPlayerIds,
    effectTargetGroups,
    hasEffectTargets,
    copyTargetsByEffectCount,
    copyEffectTargetGroups,
    targetSelectionErrors,
    copyTargetSelections,
    searchEntries,
    searchErrors,
    searchTargetsByEffect,
    hasPendingSearchChoices,
    setCopyTargetSelections,
    stackTargetChecks,
    copySpellConfig,
  } = usePlayTargeting();

  // Casting state
  const {
    preparedCast,
    manaPool,
    manaPayment,
    manaPaymentDetail,
    manaPaymentStatus,
    costLabel,
    autoPayMana,
    isComplexCost,
    handlePrepareCast,
    handleFinalizeCast,
    setManaPayment,
    setManaPaymentDetail,
    setAutoPayMana,
    buildCastContext,
    activationCosts,
    activationPayments,
    activationPaymentDetails,
    activationCostErrors,
    hasActivationCostErrors,
    activationCostPaymentsPayload,
    setActivationPayments,
    setActivationPaymentDetails,
    additionalCastCosts,
    additionalCastPayments,
    additionalCastPaymentDetails,
    additionalCastCostErrors,
    hasAdditionalCastCostErrors,
    setAdditionalCastPayments,
    setAdditionalCastPaymentDetails,
    alternativeCostOptions,
    selectedAlternativeCostTag,
    alternativeExtraCostEntries,
    alternativeExtraPayments,
    alternativeExtraPaymentDetails,
    alternativeExtraCostErrors,
    hasAlternativeExtraCostErrors,
    setSelectedAlternativeCostTag,
    setAlternativeExtraPayments,
    setAlternativeExtraPaymentDetails,
    optionalCostOptions,
    optionalCostSelections,
    optionalCostEntries,
    optionalCostPayments,
    optionalCostPaymentDetails,
    optionalCostErrors,
    optionalCostPaymentErrors,
    hasOptionalCostErrors,
    handleToggleOptionalCost,
    handleUpdateOptionalCostCount,
    setOptionalCostPayments,
    setOptionalCostPaymentDetails,
    conspireSelected,
    conspireOptions,
    conspireTaps,
    conspireError,
    handleToggleConspireTap,
    spliceOptions,
    spliceSelections,
    spliceCosts,
    splicePayments,
    splicePaymentDetails,
    spliceCostErrors,
    handleToggleSpliceCard,
    setSplicePayments,
    setSplicePaymentDetails,
  } = usePlayCasting();

  // Derive copyTargetsEnabled from copySpellConfig or optional costs
  const copyTargetsEnabled = useMemo(() => {
    return copySpellConfig?.enabled || Object.values(optionalCostSelections).some((v) => v > 0);
  }, [copySpellConfig?.enabled, optionalCostSelections]);

  // Derive hasActivatedAbility
  const selectedBattlefieldObject = gameState?.objects.find((obj) => obj.id === selectedBattlefieldId);
  const hasActivatedAbility = selectedBattlefieldObject?.ability_graphs && selectedBattlefieldObject.ability_graphs.length > 0;

  if (!gameState) return null;

  const normalizedCombatDamagePass =
    combatDamagePass === 'first_strike' || combatDamagePass === 'regular' ? combatDamagePass : undefined;
  const priorityPlayer = gameState.players.find((player) => player.id === currentPriority);
  const commanderTax = priorityPlayer?.commander_tax ?? 0;
  const showCommanderTax = !!selectedCommandId && priorityPlayer?.commander_id === selectedCommandId;

  return (
    <div className="space-y-6">
      <TurnStatusCard
        turnNumber={gameState.turn.turn_number}
        phase={gameState.turn.phase}
        step={gameState.turn.step}
        activePlayerIndex={gameState.turn.active_player_index}
        currentPriority={currentPriority}
        loading={loading}
        onPassPriority={() => {
          // Include search selections when there are any search entries (pending or from graph)
          const payload: Record<string, any> = { player_id: currentPriority };
          if (Object.keys(searchTargetsByEffect).length > 0) {
            payload.targets_by_effect = searchTargetsByEffect;
          }
          runEngineAction('pass_priority', payload);
        }}
        onAdvanceStep={() => runEngineAction('advance_turn')}
      />

      <ActionsPanel
        loading={loading}
        selectedHandId={selectedHandId}
        selectedCommandId={selectedCommandId}
        selectedBattlefieldId={selectedBattlefieldId}
        preparedCast={preparedCast}
        enterChoiceErrors={enterChoiceErrors}
        manaPaymentErrors={manaPaymentStatus.errors}
        hasWardPaymentErrors={hasWardPaymentErrors}
        hasActivationCostErrors={hasActivationCostErrors}
        hasAdditionalCastCostErrors={hasAdditionalCastCostErrors}
        hasAlternativeExtraCostErrors={hasAlternativeExtraCostErrors}
        hasOptionalCastCostErrors={hasOptionalCostErrors}
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
        selectedDefenderId={selectedDefenderId}
        defenderOptions={defenderOptions}
        combatState={combatState}
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
            ability_type: 'activated',  // New: support type+index lookup
            context: buildCastContext(selectedBattlefieldId ?? undefined, {
              wardAutoPay: autoPayWard,
              wardPayments: wardPaymentsPayload,
              costPayments: activationCostPaymentsPayload,
            }),
          })
        }
        onDeclareAttackers={() => {
          const payload: any = {
            player_id: currentPriority,
            attackers: Array.from(selectedAttackers),
          };
          if (selectedDefenderId?.startsWith('player:')) {
            const raw = selectedDefenderId.split(':')[1];
            payload.defending_player_id = raw ? Number(raw) : undefined;
          } else if (selectedDefenderId?.startsWith('planeswalker:')) {
            const objId = selectedDefenderId.split(':')[1];
            payload.defending_object_id = objId || undefined;
            const obj = objId ? objectMap.get(objId) : undefined;
            if (obj) {
              payload.defending_player_id = obj.controller_id;
            }
          }
          runEngineAction('declare_attackers', payload);
        }}
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
            ...(normalizedCombatDamagePass ? { combat_damage_pass: normalizedCombatDamagePass } : {}),
          })
        }
        hasUnresolvedDamageReplacements={hasUnresolvedDamageReplacements}
        unresolvedDamageReplacements={unresolvedDamageReplacements}
        blockerErrors={blockerErrors}
        blockerErrorMap={blockerErrorMap}
        onSelectDefender={(value) => setSelectedDefenderId(value)}
        onSelectActiveAttacker={setActiveAttackerId}
        onReorderBlockerUp={(index) =>
          setSelectedBlockerOrder((prev: Record<string, string[]>) => {
            if (!activeAttackerId) return prev;
            const order = prev[activeAttackerId] ?? [];
            if (index <= 0) return prev;
            const next = [...order];
            [next[index - 1], next[index]] = [next[index], next[index - 1]];
            return { ...prev, [activeAttackerId]: next };
          })
        }
        onReorderBlockerDown={(index) =>
          setSelectedBlockerOrder((prev: Record<string, string[]>) => {
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
          setEnterChoices((prev: Record<string, string>) => ({ ...prev, [choiceType]: value }))
        }
        modalChoiceConfig={modalChoiceConfig}
        selectedModalModes={selectedModalModes}
        modalChoiceErrors={modalChoiceErrors}
        onToggleModalMode={handleToggleModalMode}
        modalChoiceDisabled={entwineSelected}
        isComplexCost={isComplexCost}
        manaPool={manaPool}
        manaPayment={manaPayment}
        manaPaymentDetail={manaPaymentDetail}
        costLabel={costLabel}
        commanderTax={commanderTax}
        showCommanderTax={showCommanderTax}
        autoPayMana={autoPayMana}
        onToggleAutoPay={setAutoPayMana}
        onUpdatePaymentDetail={setManaPaymentDetail}
        onUpdateManaPayment={setManaPayment}
        activationCosts={activationCosts}
        activationPayments={activationPayments}
        activationPaymentDetails={activationPaymentDetails}
        activationCostErrors={activationCostErrors}
        onUpdateActivationPayment={(index, updater) =>
          setActivationPayments((prev: any[]) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateActivationPaymentDetail={(index, updater) =>
          setActivationPaymentDetails((prev: Record<number, any>) => ({
            ...prev,
            [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
          }))
        }
        additionalCastCosts={additionalCastCosts}
        additionalCastPayments={additionalCastPayments}
        additionalCastPaymentDetails={additionalCastPaymentDetails}
        additionalCastCostErrors={additionalCastCostErrors}
        onUpdateAdditionalCastPayment={(index, updater) =>
          setAdditionalCastPayments((prev: any[]) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateAdditionalCastPaymentDetail={(index, updater) =>
          setAdditionalCastPaymentDetails((prev: Record<number, any>) => ({
            ...prev,
            [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
          }))
        }
        alternativeExtraCosts={alternativeExtraCostEntries}
        alternativeExtraPayments={alternativeExtraPayments}
        alternativeExtraPaymentDetails={alternativeExtraPaymentDetails}
        alternativeExtraCostErrors={alternativeExtraCostErrors}
        onUpdateAlternativeExtraPayment={(index, updater) =>
          setAlternativeExtraPayments((prev: any[]) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateAlternativeExtraPaymentDetail={(index, updater) =>
          setAlternativeExtraPaymentDetails((prev: Record<number, any>) => ({
            ...prev,
            [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
          }))
        }
        alternativeCostOptions={alternativeCostOptions}
        selectedAlternativeCostTag={selectedAlternativeCostTag}
        onSelectAlternativeCost={setSelectedAlternativeCostTag}
        optionalCostOptions={optionalCostOptions}
        optionalCostSelections={optionalCostSelections}
        optionalCostErrors={optionalCostErrors}
        onToggleOptionalCost={handleToggleOptionalCost}
        onUpdateOptionalCostCount={handleUpdateOptionalCostCount}
        optionalCostEntries={optionalCostEntries}
        optionalCostPayments={optionalCostPayments}
        optionalCostPaymentDetails={optionalCostPaymentDetails}
        optionalCostPaymentErrors={optionalCostPaymentErrors}
        onUpdateOptionalCostPayment={(index, updater) =>
          setOptionalCostPayments((prev: any[]) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateOptionalCostPaymentDetail={(index, updater) =>
          setOptionalCostPaymentDetails((prev: Record<number, any>) => ({
            ...prev,
            [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
          }))
        }
        conspireEnabled={conspireSelected}
        conspireOptions={conspireOptions}
        conspireSelections={conspireTaps}
        conspireError={conspireError}
        onToggleConspire={handleToggleConspireTap}
        spliceOptions={spliceOptions}
        spliceSelections={spliceSelections}
        onToggleSpliceCard={handleToggleSpliceCard}
        spliceCosts={spliceCosts}
        splicePayments={splicePayments}
        splicePaymentDetails={splicePaymentDetails}
        spliceCostErrors={spliceCostErrors}
        onUpdateSplicePayment={(index, updater) =>
          setSplicePayments((prev: any[]) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateSplicePaymentDetail={(index, updater) =>
          setSplicePaymentDetails((prev: Record<number, any>) => ({
            ...prev,
            [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
          }))
        }
        autoPayWard={autoPayWard}
        onToggleAutoPayWard={setAutoPayWard}
        wardTargets={wardTargets}
        wardPayments={wardPayments}
        wardPaymentDetails={wardPaymentDetails}
        wardPaymentErrors={wardPaymentErrors}
        onUpdateWardPayment={(objectId, index, updater) =>
          setWardPayments((prev: Record<string, any>) => ({
            ...prev,
            [objectId]: (() => {
              const next = [...(prev[objectId] ?? [])];
              next[index] = updater(next[index] ?? {});
              return next;
            })(),
          }))
        }
        onUpdateWardPaymentDetail={(objectId, updater) =>
          setWardPaymentDetails((prev: Record<string, any>) => ({
            ...prev,
            [objectId]: updater(
              prev[objectId] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }
            ),
          }))
        }
        targetObjects={shouldUseStackTargets ? stackSpellObjects : filteredTargetableObjects}
        targetPlayers={shouldUseStackTargets ? [] : filteredTargetPlayers}
        selectedTargetObjectIds={resolvedTargetObjectIds}
        selectedTargetPlayerIds={resolvedTargetPlayerIds}
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
        effectTargetGroups={hasEffectTargets ? effectTargetGroups : undefined}
        copyEffectTargetGroups={copyTargetsByEffectCount > 0 ? copyEffectTargetGroups : undefined}
        targetSelectionErrors={targetSelectionErrors}
        copyTargetSelections={copyTargetsEnabled ? copyTargetSelections : undefined}
        searchChoiceEntries={searchEntries}
        searchChoiceErrors={searchErrors}
        onChangeCopyTarget={(index, objectIds, playerIds) =>
          setCopyTargetSelections((prev: Array<{ objectIds: string[]; playerIds: number[] }>) => {
            const next = [...prev];
            next[index] = { objectIds, playerIds };
            return next;
          })
        }
      />

      <CombatDamagePanel
        active={isCombatDamage}
        combatState={combatState}
        objects={gameState.objects}
        cardMap={cardMap}
        defendingPlayerId={defendingPlayerId ?? null}
        defendingObjectId={defendingObjectId}
        assignments={combatDamageAssignments}
        damagePass={normalizedCombatDamagePass}
        onUpdateAssignment={(attackerId, targetId, value) =>
          setCombatDamageAssignments((prev: Record<string, Record<string, number>>) => ({
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
          const keys = unresolvedDamageReplacements.map((entry: { key: string }) => entry.key);
          const currentIndex = highlightedReplacementKey ? keys.indexOf(highlightedReplacementKey) : -1;
          const nextIndex = (currentIndex + 1) % keys.length;
          setHighlightedReplacementKey(keys[nextIndex]);
        }}
        onSelectChoice={(key, value) =>
          {
            setReplacementChoices((prev: Record<string, string>) => ({
              ...prev,
              [key]: value,
            }));
            const remaining = unresolvedDamageReplacements
              .map((entry: { key: string }) => entry.key)
              .filter((entryKey: string) => entryKey !== key);
            setHighlightedReplacementKey(remaining[0] ?? null);
          }
        }
      />

      <StackView
        stack={gameState.stack}
        objects={gameState.objects}
        cardMap={cardMap}
        targetChecks={stackTargetChecks}
        selectedIndex={selectedStackIndex}
        onSelectIndex={setSelectedStackIndex}
      />
    </div>
  );
}
