import { useEffect, useMemo, useState } from 'react';
import { EngineCardMap, EngineGameObjectSnapshot, EnginePlayerSnapshot } from '@/lib/engine';
import {
  buildDefaultManaPayment,
  buildDefaultPaymentDetail,
  buildPaymentFromDetail,
  getManaPaymentErrors,
  hasComplexManaCost,
  ManaPaymentDetail,
} from '@/lib/manaPayment';
import { ActivationCost, formatActivationCostLabel, parseActivationCosts } from '@/lib/activationCosts';

export type ActivationCostEntry = {
  cost: ActivationCost;
  label: string;
  discardOptions: Array<{ value: string; label: string }>;
  sacrificeOptions: Array<{ value: string; label: string }>;
  tapOptions: Array<{ value: string; label: string }>;
  exileOptions: Array<{ value: string; label: string }>;
};

export type ActivationCostPayment = {
  mana_payment?: Record<string, number>;
  mana_payment_detail?: ManaPaymentDetail;
  life_payment?: number;
  discard_id?: string;
  discard_ids?: string[];
  sacrifice_id?: string;
  tap_id?: string;
  exile_ids?: string[];
};

interface UseActivationCostsArgs {
  costText: string;
  objects: EngineGameObjectSnapshot[];
  players: EnginePlayerSnapshot[];
  cardMap: EngineCardMap;
  currentPlayerId: number | null;
  manaPool: Record<string, number>;
}

export const useActivationCosts = ({
  costText,
  objects,
  players,
  cardMap,
  currentPlayerId,
  manaPool,
}: UseActivationCostsArgs) => {
  const player = players.find((entry) => entry.id === currentPlayerId);
  const objectMap = useMemo(() => new Map(objects.map((obj) => [obj.id, obj])), [objects]);
  const costEntries = useMemo<ActivationCostEntry[]>(() => {
    if (!costText) return [];
    const cardName = (objectId: string) => cardMap[objectId]?.name || objectMap.get(objectId)?.name || objectId;
    const handOptions = player?.hand?.map((objectId) => ({
      value: objectId,
      label: cardName(objectId),
    })) ?? [];
    const graveyardOptions = player?.graveyard?.map((objectId) => ({
      value: objectId,
      label: cardName(objectId),
    })) ?? [];
    const battlefieldOptions = player?.battlefield?.map((objectId) => ({
      value: objectId,
      label: cardName(objectId),
    })) ?? [];
    const isTypeMatch = (entry: EngineGameObjectSnapshot, cardType?: string, nonland?: boolean) => {
      if (nonland && entry.types?.includes('Land')) return false;
      if (!cardType) return true;
      return entry.types?.includes(cardType);
    };
    return parseActivationCosts(costText).map((cost) => {
      const discardOptions = cost.type === 'discard' ? handOptions : [];
      const sacrificeOptions =
        cost.type === 'sacrifice'
          ? battlefieldOptions.filter((entry) => {
              const obj = objectMap.get(entry.value);
              if (!obj) return false;
              return isTypeMatch(obj, cost.cardType, cost.nonland);
            })
          : [];
      const tapOptions =
        cost.type === 'tap'
          ? battlefieldOptions.filter((entry) => {
              const obj = objectMap.get(entry.value);
              if (!obj || obj.tapped) return false;
              return isTypeMatch(obj, cost.cardType, cost.nonland);
            })
          : [];
      const exileOptions = cost.type === 'exile_graveyard' ? graveyardOptions : [];
      return {
        cost,
        label: formatActivationCostLabel(cost),
        discardOptions,
        sacrificeOptions,
        tapOptions,
        exileOptions,
      };
    });
  }, [cardMap, costText, objectMap, player?.battlefield, player?.hand, player?.graveyard]);

  const [payments, setPayments] = useState<ActivationCostPayment[]>([]);
  const [paymentDetails, setPaymentDetails] = useState<Record<number, ManaPaymentDetail>>({});

  useEffect(() => {
    setPayments((prev) => {
      const next = costEntries.map((entry, index) => {
        const existing = prev[index];
        if (existing) return existing;
        if (entry.cost.type === 'mana' && !hasComplexManaCost(entry.cost.cost)) {
          return { mana_payment: buildDefaultManaPayment(entry.cost.cost, manaPool) };
        }
        if (entry.cost.type === 'life') {
          return { life_payment: entry.cost.amount };
        }
        return {};
      });
      return next;
    });
    setPaymentDetails((prev) => {
      const next: Record<number, ManaPaymentDetail> = { ...prev };
      costEntries.forEach((entry, index) => {
        if (next[index]) return;
        if (entry.cost.type === 'mana') {
          next[index] = buildDefaultPaymentDetail(entry.cost.cost, manaPool);
        }
      });
      return next;
    });
  }, [costEntries, manaPool]);

  const paymentErrors = useMemo(() => {
    const errors: string[] = [];
    costEntries.forEach((entry, index) => {
      const payment = payments[index] ?? {};
      const prefix = costEntries.length > 1 ? `Cost ${index + 1}: ` : '';
      if (entry.cost.type === 'mana') {
        if (hasComplexManaCost(entry.cost.cost)) {
          const detail = paymentDetails[index];
          if (!detail) return;
          const { errors: detailErrors } = buildPaymentFromDetail(entry.cost.cost, manaPool, detail);
          detailErrors.forEach((err) => errors.push(`${prefix}${err}`));
          return;
        }
        const { errors: simpleErrors } = getManaPaymentErrors(entry.cost.cost, payment.mana_payment ?? {}, manaPool);
        simpleErrors.forEach((err) => errors.push(`${prefix}${err}`));
        return;
      }
      if (entry.cost.type === 'discard') {
        const selected = payment.discard_ids ?? (payment.discard_id ? [payment.discard_id] : []);
        if (selected.length !== entry.cost.amount) {
          errors.push(`${prefix}Select ${entry.cost.amount} card(s) to discard.`);
        }
        return;
      }
      if (entry.cost.type === 'exile_graveyard') {
        const selected = payment.exile_ids ?? [];
        if (selected.length !== entry.cost.amount) {
          errors.push(`${prefix}Select ${entry.cost.amount} card(s) to exile.`);
        }
        return;
      }
      if (entry.cost.type === 'sacrifice') {
        if (!payment.sacrifice_id) {
          errors.push(`${prefix}Select a permanent to sacrifice.`);
        }
        return;
      }
      if (entry.cost.type === 'tap') {
        if (!payment.tap_id) {
          errors.push(`${prefix}Select a permanent to tap.`);
        }
      }
    });
    return errors;
  }, [costEntries, manaPool, paymentDetails, payments]);

  const paymentsPayload = useMemo(() => {
    if (costEntries.length === 0) return undefined;
    const payload = costEntries.map((entry, index) => {
      const payment = payments[index] ?? {};
      if (entry.cost.type === 'mana') {
        if (hasComplexManaCost(entry.cost.cost)) {
          const detail = paymentDetails[index];
          if (!detail) return {};
          const { payment: mana_payment } = buildPaymentFromDetail(entry.cost.cost, manaPool, detail);
          return { mana_payment, mana_payment_detail: detail };
        }
        return payment.mana_payment ? { mana_payment: payment.mana_payment } : {};
      }
      if (entry.cost.type === 'life') {
        return { life_payment: entry.cost.amount };
      }
      if (entry.cost.type === 'discard') {
        const selection = payment.discard_ids ?? (payment.discard_id ? [payment.discard_id] : undefined);
        return selection ? { discard_ids: selection } : {};
      }
      if (entry.cost.type === 'exile_graveyard') {
        return payment.exile_ids ? { exile_ids: payment.exile_ids } : {};
      }
      if (entry.cost.type === 'sacrifice') {
        return payment.sacrifice_id ? { sacrifice_id: payment.sacrifice_id } : {};
      }
      if (entry.cost.type === 'tap') {
        return payment.tap_id ? { tap_id: payment.tap_id } : {};
      }
      return {};
    });
    return payload;
  }, [costEntries, manaPool, paymentDetails, payments]);

  return {
    costEntries,
    payments,
    setPayments,
    paymentDetails,
    setPaymentDetails,
    paymentErrors,
    paymentsPayload,
  };
};

