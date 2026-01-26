'use client';

import { ManaPaymentDetail, hasComplexManaCost } from '@/lib/manaPayment';
import { ActivationCostEntry } from '../hooks/useActivationCosts';
import { Select } from '@/components/ui/Select';

interface ActivationCostPanelProps {
  active: boolean;
  title?: string;
  costEntries: ActivationCostEntry[];
  manaPool: Record<string, number>;
  payments: Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
    exile_ids?: string[];
  }>;
  paymentDetails: Record<number, ManaPaymentDetail>;
  errors: string[];
  onUpdatePayment: (
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }
  ) => void;
  onUpdatePaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
}

export function ActivationCostPanel({
  active,
  title = 'Activation Costs',
  costEntries,
  manaPool,
  payments,
  paymentDetails,
  errors,
  onUpdatePayment,
  onUpdatePaymentDetail,
}: ActivationCostPanelProps) {
  if (!active || costEntries.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">{title}</div>
      {costEntries.map((entry, index) => {
        const payment = payments[index] ?? {};
        const detail = paymentDetails[index];
        const isManaCost = entry.cost.type === 'mana';
        const isComplex = isManaCost ? hasComplexManaCost(entry.cost.cost) : false;
        return (
          <div key={`activation-cost-${index}`} className="rounded border border-[color:var(--theme-input-border)] p-2 space-y-2">
            <div className="text-xs text-[color:var(--theme-text-secondary)]">Cost {index + 1}: {entry.label}</div>
            {isManaCost && isComplex && detail && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                {(entry.cost.cost.hybrids ?? []).map(([colorA, colorB], idx) => (
                  <label key={`activation-hybrid-${index}-${idx}`} className="flex items-center gap-2">
                    <span className="text-[color:var(--theme-text-secondary)]">Hybrid</span>
                    <Select
                      value={detail.hybrid_choices[idx] ?? colorA}
                      onChange={(e) =>
                        onUpdatePaymentDetail(index, (prev) => {
                          const next = [...prev.hybrid_choices];
                          next[idx] = e.target.value;
                          return { ...prev, hybrid_choices: next };
                        })
                      }
                      className="flex-1"
                    >
                      <option value={colorA}>{colorA}</option>
                      <option value={colorB}>{colorB}</option>
                    </Select>
                  </label>
                ))}
                {(entry.cost.cost.two_brids ?? []).map(([genericValue, color], idx) => (
                  <label key={`activation-two-brid-${index}-${idx}`} className="flex items-center gap-2">
                    <span className="text-[color:var(--theme-text-secondary)]">Two-brid</span>
                    <Select
                      value={detail.two_brid_choices[idx] ? 'color' : 'generic'}
                      onChange={(e) =>
                        onUpdatePaymentDetail(index, (prev) => {
                          const next = [...prev.two_brid_choices];
                          next[idx] = e.target.value === 'color';
                          return { ...prev, two_brid_choices: next };
                        })
                      }
                      className="flex-1"
                    >
                      <option value="color">{color}</option>
                      <option value="generic">{genericValue} generic</option>
                    </Select>
                  </label>
                ))}
                {(entry.cost.cost.phyrexian ?? []).map((color, idx) => (
                  <label key={`activation-phyrexian-${index}-${idx}`} className="flex items-center gap-2">
                    <span className="text-[color:var(--theme-text-secondary)]">Phyrexian</span>
                    <Select
                      value={detail.phyrexian_choices[idx] ? 'life' : 'mana'}
                      onChange={(e) =>
                        onUpdatePaymentDetail(index, (prev) => {
                          const next = [...prev.phyrexian_choices];
                          next[idx] = e.target.value === 'life';
                          return { ...prev, phyrexian_choices: next };
                        })
                      }
                      className="flex-1"
                    >
                      <option value="mana">{color} mana</option>
                      <option value="life">2 life</option>
                    </Select>
                  </label>
                ))}
              </div>
            )}
            {isManaCost && !isComplex && (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                {['W', 'U', 'B', 'R', 'G', 'C'].map((color) => (
                  <label key={`activation-mana-${index}-${color}`} className="flex items-center gap-2">
                    <span className="w-4 text-[color:var(--theme-text-secondary)]">{color}</span>
                    <input
                      type="number"
                      min={0}
                      max={manaPool[color] ?? 0}
                      value={payment.mana_payment?.[color] ?? 0}
                      onChange={(e) =>
                        onUpdatePayment(index, (prev) => ({
                          ...prev,
                          mana_payment: {
                            ...(prev.mana_payment ?? {}),
                            [color]: Math.max(0, parseInt(e.target.value || '0', 10)),
                          },
                        }))
                      }
                      className="w-full px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                    />
                    <span className="text-[color:var(--theme-text-secondary)] text-xs">/ {manaPool[color] ?? 0}</span>
                  </label>
                ))}
              </div>
            )}
            {entry.cost.type === 'discard' && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-[color:var(--theme-text-secondary)]">Discard</span>
                <Select
                  multiple
                  value={payment.discard_ids ?? []}
                  onChange={(e) =>
                    onUpdatePayment(index, (prev) => ({
                      ...prev,
                      discard_ids: Array.from(e.target.selectedOptions).map((option) => option.value),
                    }))
                  }
                  className="flex-1"
                >
                  {entry.discardOptions.map((option) => (
                    <option key={`activation-discard-${index}-${option.value}`} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              </div>
            )}
            {entry.cost.type === 'exile_graveyard' && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-[color:var(--theme-text-secondary)]">Exile</span>
                <Select
                  multiple
                  value={payment.exile_ids ?? []}
                  onChange={(e) =>
                    onUpdatePayment(index, (prev) => ({
                      ...prev,
                      exile_ids: Array.from(e.target.selectedOptions).map((option) => option.value),
                    }))
                  }
                  className="flex-1"
                >
                  {entry.exileOptions.map((option) => (
                    <option key={`activation-exile-${index}-${option.value}`} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              </div>
            )}
            {entry.cost.type === 'sacrifice' && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-[color:var(--theme-text-secondary)]">Sacrifice</span>
                <Select
                  value={payment.sacrifice_id ?? ''}
                  onChange={(e) =>
                    onUpdatePayment(index, (prev) => ({
                      ...prev,
                      sacrifice_id: e.target.value || undefined,
                    }))
                  }
                  className="flex-1"
                >
                  <option value="">Select permanent</option>
                  {entry.sacrificeOptions.map((option) => (
                    <option key={`activation-sac-${index}-${option.value}`} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              </div>
            )}
            {entry.cost.type === 'tap' && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-[color:var(--theme-text-secondary)]">Tap</span>
                <Select
                  value={payment.tap_id ?? ''}
                  onChange={(e) =>
                    onUpdatePayment(index, (prev) => ({
                      ...prev,
                      tap_id: e.target.value || undefined,
                    }))
                  }
                  className="flex-1"
                >
                  <option value="">Select permanent</option>
                  {entry.tapOptions.map((option) => (
                    <option key={`activation-tap-${index}-${option.value}`} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              </div>
            )}
          </div>
        );
      })}
      {errors.length > 0 && (
        <div className="text-xs text-[color:var(--theme-status-error)]">{errors.join(' ')}</div>
      )}
    </div>
  );
}

