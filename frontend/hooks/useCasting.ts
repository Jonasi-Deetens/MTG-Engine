import { useEffect, useMemo, useState } from 'react';
import { EngineActionRequest, EngineCardMap } from '@/lib/engine';
import {
  buildDefaultManaPayment,
  buildDefaultPaymentDetail,
  buildPaymentFromDetail,
  getManaPaymentErrors,
  hasComplexManaCost,
  ManaPaymentDetail,
} from '@/lib/manaPayment';

interface UseCastingArgs {
  selectedHandId: string | null;
  selectedCommandId?: string | null;
  currentPriority: number | null;
  abilityGraphs: Record<string, any>;
  cardMap: EngineCardMap;
  manaPool: Record<string, number>;
  buildCastContext: (
    sourceIdOverride?: string | null,
    wardOptions?: {
      wardAutoPay?: boolean;
      wardPayments?: Record<string, any>;
      additionalCostPayments?: any;
      alternativeCostTag?: string | null;
      alternativeCostPayments?: any;
    }
  ) => EngineActionRequest['context'];
  wardPayments?: Record<string, any>;
  autoPayWard: boolean;
  additionalCostPayments?: any;
  alternativeCostTag?: string | null;
  alternativeCostPayments?: any;
  runEngineAction: (
    action: EngineActionRequest['action'],
    payload?: Partial<EngineActionRequest>
  ) => Promise<any>;
}

export const useCasting = ({
  selectedHandId,
  selectedCommandId,
  currentPriority,
  abilityGraphs,
  cardMap,
  manaPool,
  buildCastContext,
  wardPayments,
  autoPayWard,
  additionalCostPayments,
  alternativeCostTag,
  alternativeCostPayments,
  runEngineAction,
}: UseCastingArgs) => {
  const selectedCastId = selectedCommandId ?? selectedHandId;
  const [preparedCast, setPreparedCast] = useState<{ objectId: string; cost: any } | null>(null);
  const [manaPayment, setManaPayment] = useState<Record<string, number>>({});
  const [manaPaymentDetail, setManaPaymentDetail] = useState<ManaPaymentDetail>({
    hybrid_choices: [],
    two_brid_choices: [],
    phyrexian_choices: [],
  });
  const [autoPayMana, setAutoPayMana] = useState(true);

  useEffect(() => {
    setPreparedCast(null);
    setManaPayment({});
    setManaPaymentDetail({ hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] });
    setAutoPayMana(true);
  }, [selectedCastId]);

  const handlePrepareCast = async () => {
    if (!selectedCastId || currentPriority === null) return;
    const response = await runEngineAction('prepare_cast', {
      player_id: currentPriority,
      object_id: selectedCastId,
      ability_graph: abilityGraphs[cardMap[selectedCastId]?.card_id ?? ''],
      context: buildCastContext(selectedCastId, {
        wardAutoPay: autoPayWard,
        wardPayments,
        additionalCostPayments,
        alternativeCostTag,
        alternativeCostPayments,
      }),
    });
    const cost = response?.result?.cost;
    if (cost) {
      setPreparedCast({ objectId: selectedCastId, cost });
      const detail = buildDefaultPaymentDetail(cost, manaPool);
      setManaPaymentDetail(detail);
      if (hasComplexManaCost(cost)) {
        const { payment } = buildPaymentFromDetail(cost, manaPool, detail);
        setManaPayment(payment);
      } else {
        setManaPayment(buildDefaultManaPayment(cost, manaPool));
      }
      setAutoPayMana(true);
    }
  };

  const handleFinalizeCast = async () => {
    if (!selectedCastId || !preparedCast || preparedCast.objectId !== selectedCastId) return;
    if (currentPriority === null) return;
    const response = await runEngineAction('finalize_cast', {
      player_id: currentPriority,
      object_id: selectedCastId,
      ability_graph: abilityGraphs[cardMap[selectedCastId]?.card_id ?? ''],
      context: buildCastContext(selectedCastId, {
        wardAutoPay: autoPayWard,
        wardPayments,
        additionalCostPayments,
        alternativeCostTag,
        alternativeCostPayments,
      }),
      mana_payment: Object.keys(manaPayment).length > 0 ? manaPayment : undefined,
      mana_payment_detail: isComplexCost ? manaPaymentDetail : undefined,
    });
    if (response?.result?.status === 'spell_cast') {
      setPreparedCast(null);
      setManaPayment({});
      setAutoPayMana(true);
    }
  };

  const isComplexCost = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return false;
    return hasComplexManaCost(preparedCast.cost);
  }, [preparedCast, selectedCastId]);

  useEffect(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return;
    if (!autoPayMana) return;
    if (isComplexCost) {
      const { payment } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
      setManaPayment(payment);
      return;
    }
    setManaPayment(buildDefaultManaPayment(preparedCast.cost, manaPool));
  }, [autoPayMana, isComplexCost, manaPaymentDetail, manaPool, preparedCast, selectedCastId]);

  useEffect(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return;
    if (!isComplexCost) return;
    const { payment } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
    setManaPayment(payment);
  }, [isComplexCost, manaPaymentDetail, manaPool, preparedCast, selectedCastId]);

  const manaPaymentStatus = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) {
      return { errors: [] as string[], totalRequired: 0 };
    }
    if (isComplexCost) {
      const { errors } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
      return { errors, totalRequired: 0 };
    }
    return getManaPaymentErrors(preparedCast.cost, manaPayment, manaPool);
  }, [preparedCast, selectedCastId, manaPayment, manaPool, isComplexCost, manaPaymentDetail]);

  const costLabel = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return '';
    const cost = preparedCast.cost;
    const parts: string[] = [];
    const xCount = Number((cost as any).x_count ?? (cost as any).x ?? 0);
    if (xCount > 0) {
      parts.push(`${xCount}X`);
    }
    if (cost.colored) {
      Object.entries(cost.colored).forEach(([color, amount]) => {
        const count = Number(amount || 0);
        if (count > 0) parts.push(`${count}${color}`);
      });
    }
    if (cost.colorless) parts.push(`${cost.colorless}C`);
    if (cost.generic) parts.push(`${cost.generic}`);
    if (hasComplexManaCost(cost)) {
      parts.push('hybrid/phyrexian');
    }
    return parts.join(' + ') || '0';
  }, [preparedCast, selectedCastId]);

  useEffect(() => {
    if (!isComplexCost) return;
    setAutoPayMana(true);
  }, [isComplexCost]);

  return {
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
  };
};

