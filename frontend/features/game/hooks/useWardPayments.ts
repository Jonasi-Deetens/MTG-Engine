import { useEffect, useMemo, useState } from 'react';
import { EngineGameObjectSnapshot, EnginePlayerSnapshot } from '@/lib/engine';
import {
  buildDefaultManaPayment,
  buildDefaultPaymentDetail,
  buildPaymentFromDetail,
  getManaPaymentErrors,
  hasComplexManaCost,
  ManaPaymentDetail,
} from '@/lib/manaPayment';
import { buildActivationCosts, formatActivationCostLabel } from '@/lib/activationCosts';
import { deriveWardCostsFromGraphs } from '@/lib/graphCosts';
import { EngineCardMap } from '@/lib/engine';

type WardCostEntry = {
  cost: ReturnType<typeof buildActivationCosts>[number];
  costLabel: string;
  discardOptions: Array<{ value: string; label: string }>;
  sacrificeOptions: Array<{ value: string; label: string }>;
  tapOptions: Array<{ value: string; label: string }>;
};

type WardTarget = {
  objectId: string;
  name: string;
  costs: WardCostEntry[];
  hasMultipleCosts: boolean;
};

const EMPTY_WARD_TARGETS: WardTarget[] = [];
const EMPTY_MANA_POOL: Record<string, number> = {};

type WardPaymentsUpdate = {
  next: Record<string, WardPaymentEntry[]>;
  changed: boolean;
};

type WardDetailsUpdate = {
  next: Record<string, ManaPaymentDetail>;
  changed: boolean;
};

const buildWardPaymentsUpdate = (
  prev: Record<string, WardPaymentEntry[]>,
  wardTargets: WardTarget[],
  manaPool: Record<string, number>
): WardPaymentsUpdate => {
  if (wardTargets.length === 0) {
    return {
      next: Object.keys(prev).length === 0 ? prev : {},
      changed: Object.keys(prev).length > 0,
    };
  }

  const activeIds = new Set(wardTargets.map((target) => target.objectId));
  let next = prev;
  let changed = false;

  Object.keys(prev).forEach((key) => {
    if (!activeIds.has(key)) {
      if (next === prev) next = { ...prev };
      delete next[key];
      changed = true;
    }
  });

  wardTargets.forEach((target) => {
    const existing = next[target.objectId] ?? [];
    let entries = existing;
    target.costs.forEach((entry, index) => {
      if (entries[index]) return;
      if (entries === existing) entries = [...existing];
      changed = true;
      if (entry.cost.type === 'mana' && !hasComplexManaCost(entry.cost.cost)) {
        entries[index] = { mana_payment: buildDefaultManaPayment(entry.cost.cost, manaPool) };
        return;
      }
      if (entry.cost.type === 'life') {
        entries[index] = { life_payment: entry.cost.amount };
        return;
      }
      entries[index] = {};
    });

    if (entries !== existing || !(target.objectId in next)) {
      if (next === prev) next = { ...next };
      next[target.objectId] = entries;
    }
  });

  return { next: changed ? next : prev, changed };
};

const buildWardPaymentDetailsUpdate = (
  prev: Record<string, ManaPaymentDetail>,
  wardTargets: WardTarget[],
  manaPool: Record<string, number>
): WardDetailsUpdate => {
  if (wardTargets.length === 0) {
    return {
      next: Object.keys(prev).length === 0 ? prev : {},
      changed: Object.keys(prev).length > 0,
    };
  }

  const activeIds = new Set(wardTargets.map((target) => target.objectId));
  let next = prev;
  let changed = false;

  Object.keys(prev).forEach((key) => {
    if (!activeIds.has(key)) {
      if (next === prev) next = { ...prev };
      delete next[key];
      changed = true;
    }
  });

  wardTargets.forEach((target) => {
    if (next[target.objectId]) return;
    const manaCost = target.costs.find((entry) => entry.cost.type === 'mana');
    if (manaCost && manaCost.cost.type === 'mana') {
      if (next === prev) next = { ...next };
      next[target.objectId] = buildDefaultPaymentDetail(manaCost.cost.cost, manaPool);
      changed = true;
    }
  });

  return { next: changed ? next : prev, changed };
};

export type WardPaymentEntry = {
  mana_payment?: Record<string, number>;
  mana_payment_detail?: ManaPaymentDetail;
  life_payment?: number;
  discard_id?: string;
  discard_ids?: string[];
  sacrifice_id?: string;
  tap_id?: string;
};

interface UseWardPaymentsArgs {
  objects: EngineGameObjectSnapshot[];
  players: EnginePlayerSnapshot[];
  cardMap: EngineCardMap;
  currentPlayerId: number | null;
  selectedTargetObjectIds: string[];
  manaPool: Record<string, number>;
  autoPayWard: boolean;
}

export const useWardPayments = ({
  objects,
  players,
  cardMap,
  currentPlayerId,
  selectedTargetObjectIds,
  manaPool,
  autoPayWard,
}: UseWardPaymentsArgs) => {
  const player = players.find((entry) => entry.id === currentPlayerId);
  const effectiveManaPool = useMemo(
    () => (Object.keys(manaPool).length ? manaPool : EMPTY_MANA_POOL),
    [manaPool]
  );
  const wardTargets = useMemo((): WardTarget[] => {
    if (!selectedTargetObjectIds.length) return EMPTY_WARD_TARGETS;
    const objectMap = new Map(objects.map((obj) => [obj.id, obj]));
    const cardName = (objectId: string) =>
      cardMap[objectId]?.name || objectMap.get(objectId)?.name || objectId;
    const handOptions = player?.hand?.map((objectId) => ({
      value: objectId,
      label: cardName(objectId),
    })) ?? [];
    const battlefieldOptions =
      player?.battlefield?.map((objectId) => ({
        value: objectId,
        label: cardName(objectId),
      })) ?? [];
    return selectedTargetObjectIds
      .map((objectId) => objectMap.get(objectId))
      .filter((obj): obj is EngineGameObjectSnapshot => Boolean(obj))
      .map((obj) => {
        const costs = buildActivationCosts(deriveWardCostsFromGraphs(obj.ability_graphs ?? []));
        if (!costs.length) {
          return null;
        }
        const isTypeMatch = (entry: EngineGameObjectSnapshot, cardType?: string, nonland?: boolean) => {
          if (nonland && entry.types?.includes('Land')) return false;
          if (!cardType) return true;
          return entry.types?.includes(cardType);
        };
        const costEntries = costs.map((cost) => {
          const costLabel = formatActivationCostLabel(cost) ?? '';
          const discardOptions = cost.type === 'discard' ? handOptions : [];
          const sacrificeOptions =
            cost.type === 'sacrifice'
              ? battlefieldOptions.filter((entry) => {
                  const obj = objectMap.get(entry.value);
                  if (!obj) return false;
                  return isTypeMatch(obj, cost.card_type, cost.nonland);
                })
              : [];
          const tapOptions =
            cost.type === 'tap'
              ? battlefieldOptions.filter((entry) => {
                  const obj = objectMap.get(entry.value);
                  if (!obj || obj.tapped) return false;
                  return isTypeMatch(obj, cost.card_type, cost.nonland);
                })
              : [];
          return {
            cost,
            costLabel,
            discardOptions,
            sacrificeOptions,
            tapOptions,
          };
        });
        return {
          objectId: obj.id,
          name: obj.name || obj.id,
          hasMultipleCosts: costs.length > 1,
          costs: costEntries,
        };
      })
      .filter((entry): entry is WardTarget => Boolean(entry));
  }, [cardMap, objects, player?.battlefield, player?.hand, selectedTargetObjectIds]);

  const [wardPayments, setWardPayments] = useState<Record<string, WardPaymentEntry[]>>({});
  const [wardPaymentDetails, setWardPaymentDetails] = useState<Record<string, ManaPaymentDetail>>({});

  useEffect(() => {
    setWardPayments((prev) => buildWardPaymentsUpdate(prev, wardTargets, effectiveManaPool).next);
    setWardPaymentDetails((prev) => buildWardPaymentDetailsUpdate(prev, wardTargets, effectiveManaPool).next);
  }, [effectiveManaPool, wardTargets]);

  const wardPaymentErrors = useMemo(() => {
    const errors: Record<string, string[]> = {};
    wardTargets.forEach((target) => {
      const targetErrors: string[] = [];
      target.costs.forEach((entry, index) => {
        const paymentEntry = wardPayments[target.objectId]?.[index];
        const prefix = target.costs.length > 1 ? `Cost ${index + 1}: ` : '';
        if (autoPayWard && entry.cost.type !== 'mana' && entry.cost.type !== 'life') {
          targetErrors.push(`${prefix}Auto-pay cannot satisfy this ward cost.`);
          return;
        }
        if (entry.cost.type === 'mana') {
          if (autoPayWard) return;
          if (hasComplexManaCost(entry.cost.cost)) {
            const detail = wardPaymentDetails[target.objectId];
            if (!detail) return;
            const { errors: detailErrors } = buildPaymentFromDetail(entry.cost.cost, manaPool, detail);
            if (detailErrors.length > 0) {
              detailErrors.forEach((err) => targetErrors.push(`${prefix}${err}`));
            }
            return;
          }
          const payment = paymentEntry?.mana_payment ?? {};
          const { errors: simpleErrors } = getManaPaymentErrors(entry.cost.cost, payment, manaPool);
          if (simpleErrors.length > 0) {
            simpleErrors.forEach((err) => targetErrors.push(`${prefix}${err}`));
          }
          return;
        }
        if (entry.cost.type === 'life') {
          if (!autoPayWard) {
            const payment = paymentEntry?.life_payment;
            if (!payment || payment < entry.cost.amount) {
              targetErrors.push(`${prefix}Life payment is required.`);
            }
          }
          return;
        }
        if (entry.cost.type === 'discard') {
          const selection = paymentEntry?.discard_ids ?? (paymentEntry?.discard_id ? [paymentEntry.discard_id] : []);
          if (selection.length !== entry.cost.amount) {
            targetErrors.push(`${prefix}Select ${entry.cost.amount} card(s) to discard.`);
          }
          return;
        }
        if (entry.cost.type === 'sacrifice') {
          const selection = paymentEntry?.sacrifice_id;
          if (!selection) {
            targetErrors.push(`${prefix}Select a permanent to sacrifice.`);
          }
          return;
        }
        if (entry.cost.type === 'tap') {
          const selection = paymentEntry?.tap_id;
          if (!selection) {
            targetErrors.push(`${prefix}Select a permanent to tap.`);
          }
        }
      });
      if (targetErrors.length > 0) {
        errors[target.objectId] = targetErrors;
      }
    });
    return errors;
  }, [autoPayWard, manaPool, wardPaymentDetails, wardPayments, wardTargets]);

  const wardPaymentsPayload = useMemo(() => {
    const payload: Record<string, WardPaymentEntry | WardPaymentEntry[]> = {};
    wardTargets.forEach((target) => {
      const entries: WardPaymentEntry[] = [];
      target.costs.forEach((entry, index) => {
        const paymentEntry = wardPayments[target.objectId]?.[index] ?? {};
        if (entry.cost.type === 'mana') {
          if (autoPayWard) {
            entries.push({});
            return;
          }
          if (hasComplexManaCost(entry.cost.cost)) {
            const detail = wardPaymentDetails[target.objectId];
            if (!detail) return;
            const { payment } = buildPaymentFromDetail(entry.cost.cost, manaPool, detail);
            entries.push({ mana_payment: payment, mana_payment_detail: detail });
            return;
          }
          const payment = paymentEntry.mana_payment;
          if (payment) {
            entries.push({ mana_payment: payment });
          } else {
            entries.push({});
          }
          return;
        }
        if (entry.cost.type === 'life') {
          entries.push({ life_payment: entry.cost.amount });
          return;
        }
        if (entry.cost.type === 'discard') {
          const selection = paymentEntry.discard_ids ?? (paymentEntry.discard_id ? [paymentEntry.discard_id] : undefined);
          if (selection) {
            entries.push({ discard_ids: selection });
          } else {
            entries.push({});
          }
          return;
        }
        if (entry.cost.type === 'sacrifice') {
          const selection = paymentEntry.sacrifice_id;
          entries.push(selection ? { sacrifice_id: selection } : {});
          return;
        }
        if (entry.cost.type === 'tap') {
          const selection = paymentEntry.tap_id;
          entries.push(selection ? { tap_id: selection } : {});
        }
      });
      if (target.costs.length > 1) {
        payload[target.objectId] = entries;
        return;
      }
      if (entries[0]) {
        payload[target.objectId] = entries[0];
      }
    });
    return Object.keys(payload).length > 0 ? payload : undefined;
  }, [autoPayWard, manaPool, wardPaymentDetails, wardPayments, wardTargets]);

  return {
    wardTargets,
    wardPayments,
    setWardPayments,
    wardPaymentDetails,
    setWardPaymentDetails,
    wardPaymentErrors,
    wardPaymentsPayload,
  };
};

