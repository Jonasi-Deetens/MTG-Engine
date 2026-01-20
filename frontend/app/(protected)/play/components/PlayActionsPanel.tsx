'use client';

import { ActionsPanel } from '@/components/engine/ActionsPanel';
import { CombatDamagePanel } from '@/components/engine/CombatDamagePanel';
import { ReplacementChoicePanel } from '@/components/engine/ReplacementChoicePanel';
import { StackView } from '@/components/engine/StackView';
import { TurnStatusCard } from '@/components/engine/TurnStatusCard';
import { usePlayState } from '@/app/(protected)/play/PlayState';

export function PlayActionsPanel() {
  const {
    gameState,
    loading,
    currentPriority,
    runEngineAction,
    selectedHandId,
    selectedBattlefieldId,
    preparedCast,
    enterChoiceErrors,
    manaPaymentStatus,
    hasWardPaymentErrors,
    hasActivationCostErrors,
    hasAdditionalCastCostErrors,
    hasAlternativeExtraCostErrors,
    hasOptionalCostErrors,
    isMainPhase,
    isPriorityActivePlayer,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    isPriorityDefender,
    hasActivatedAbility,
    selectedAttackers,
    activeAttackerId,
    activeBlockerOrder,
    selectedDefenderId,
    defenderOptions,
    combatState,
    cardMap,
    objectMap,
    handlePrepareCast,
    handleFinalizeCast,
    blockersPayload,
    hasManualCombatChoices,
    combatDamageAssignments,
    combatDamagePass,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
    blockerErrors,
    blockerErrorMap,
    setSelectedDefenderId,
    setActiveAttackerId,
    setSelectedBlockerOrder,
    enterChoiceConfig,
    enterChoices,
    enterChoiceTargetOptions,
    setEnterChoices,
    modalChoiceConfig,
    selectedModalModes,
    modalChoiceErrors,
    handleToggleModalMode,
    entwineSelected,
    isComplexCost,
    manaPool,
    manaPayment,
    manaPaymentDetail,
    costLabel,
    autoPayMana,
    setAutoPayMana,
    setManaPaymentDetail,
    setManaPayment,
    activationCosts,
    activationPayments,
    activationPaymentDetails,
    activationCostErrors,
    setActivationPayments,
    setActivationPaymentDetails,
    additionalCastCosts,
    additionalCastPayments,
    additionalCastPaymentDetails,
    additionalCastCostErrors,
    setAdditionalCastPayments,
    setAdditionalCastPaymentDetails,
    alternativeExtraCostEntries,
    alternativeExtraPayments,
    alternativeExtraPaymentDetails,
    alternativeExtraCostErrors,
    setAlternativeExtraPayments,
    setAlternativeExtraPaymentDetails,
    alternativeCostOptions,
    selectedAlternativeCostTag,
    setSelectedAlternativeCostTag,
    optionalCostOptions,
    optionalCostSelections,
    optionalCostErrors,
    handleToggleOptionalCost,
    handleUpdateOptionalCostCount,
    optionalCostEntries,
    optionalCostPayments,
    optionalCostPaymentDetails,
    optionalCostPaymentErrors,
    setOptionalCostPayments,
    setOptionalCostPaymentDetails,
    conspireSelected,
    conspireOptions,
    conspireTaps,
    conspireError,
    handleToggleConspireTap,
    spliceOptions,
    spliceSelections,
    handleToggleSpliceCard,
    spliceCosts,
    splicePayments,
    splicePaymentDetails,
    spliceCostErrors,
    setSplicePayments,
    setSplicePaymentDetails,
    autoPayWard,
    setAutoPayWard,
    wardTargets,
    wardPayments,
    wardPaymentDetails,
    wardPaymentErrors,
    setWardPayments,
    setWardPaymentDetails,
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
    copyTargetsEnabled,
    copyTargetSelections,
    searchEntries,
    searchErrors,
    setCopyTargetSelections,
    replacementConflicts,
    replacementChoices,
    highlightedReplacementKey,
    setHighlightedReplacementKey,
    setReplacementChoices,
    defendingPlayerId,
    defendingObjectId,
    buildCastContext,
    wardPaymentsPayload,
    activationCostPaymentsPayload,
    stackTargetChecks,
  } = usePlayState();

  if (!gameState) return null;

  return (
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
            ...(combatDamagePass ? { combat_damage_pass: combatDamagePass } : {}),
          })
        }
        hasUnresolvedDamageReplacements={hasUnresolvedDamageReplacements}
        unresolvedDamageReplacements={unresolvedDamageReplacements}
        blockerErrors={blockerErrors}
        blockerErrorMap={blockerErrorMap}
        onSelectDefender={(value) => setSelectedDefenderId(value)}
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
        autoPayMana={autoPayMana}
        onToggleAutoPay={setAutoPayMana}
        onUpdatePaymentDetail={setManaPaymentDetail}
        onUpdateManaPayment={setManaPayment}
        activationCosts={activationCosts}
        activationPayments={activationPayments}
        activationPaymentDetails={activationPaymentDetails}
        activationCostErrors={activationCostErrors}
        onUpdateActivationPayment={(index, updater) =>
          setActivationPayments((prev) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateActivationPaymentDetail={(index, updater) =>
          setActivationPaymentDetails((prev) => ({
            ...prev,
            [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
          }))
        }
        additionalCastCosts={additionalCastCosts}
        additionalCastPayments={additionalCastPayments}
        additionalCastPaymentDetails={additionalCastPaymentDetails}
        additionalCastCostErrors={additionalCastCostErrors}
        onUpdateAdditionalCastPayment={(index, updater) =>
          setAdditionalCastPayments((prev) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateAdditionalCastPaymentDetail={(index, updater) =>
          setAdditionalCastPaymentDetails((prev) => ({
            ...prev,
            [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
          }))
        }
        alternativeExtraCosts={alternativeExtraCostEntries}
        alternativeExtraPayments={alternativeExtraPayments}
        alternativeExtraPaymentDetails={alternativeExtraPaymentDetails}
        alternativeExtraCostErrors={alternativeExtraCostErrors}
        onUpdateAlternativeExtraPayment={(index, updater) =>
          setAlternativeExtraPayments((prev) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateAlternativeExtraPaymentDetail={(index, updater) =>
          setAlternativeExtraPaymentDetails((prev) => ({
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
          setOptionalCostPayments((prev) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateOptionalCostPaymentDetail={(index, updater) =>
          setOptionalCostPaymentDetails((prev) => ({
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
          setSplicePayments((prev) => {
            const next = [...prev];
            next[index] = updater(next[index] ?? {});
            return next;
          })
        }
        onUpdateSplicePaymentDetail={(index, updater) =>
          setSplicePaymentDetails((prev) => ({
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
          setWardPayments((prev) => ({
            ...prev,
            [objectId]: (() => {
              const next = [...(prev[objectId] ?? [])];
              next[index] = updater(next[index] ?? {});
              return next;
            })(),
          }))
        }
        onUpdateWardPaymentDetail={(objectId, updater) =>
          setWardPaymentDetails((prev) => ({
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
          setCopyTargetSelections((prev) => {
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
    </div>
  );
}
