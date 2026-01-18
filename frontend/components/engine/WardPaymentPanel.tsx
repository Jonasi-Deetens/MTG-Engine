'use client';

import { ManaPaymentDetail, hasComplexManaCost } from '@/lib/manaPayment';
import { WardCost } from '@/lib/wardCosts';

type WardTargetEntry = {
  objectId: string;
  name: string;
  costs: Array<{
    cost: WardCost;
    costLabel?: string;
    discardOptions: Array<{ value: string; label: string }>;
    sacrificeOptions: Array<{ value: string; label: string }>;
    tapOptions: Array<{ value: string; label: string }>;
  }>;
  hasMultipleCosts: boolean;
};

interface WardPaymentPanelProps {
  active: boolean;
  autoPayWard: boolean;
  onToggleAutoPayWard: (value: boolean) => void;
  wardTargets: WardTargetEntry[];
  manaPool: Record<string, number>;
  wardPayments: Record<string, Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
  }>>;
  wardPaymentDetails: Record<string, ManaPaymentDetail>;
  wardPaymentErrors: Record<string, string[]>;
  onUpdateWardPayment: (
    objectId: string,
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }
  ) => void;
  onUpdateWardPaymentDetail: (
    objectId: string,
    updater: (prev: ManaPaymentDetail) => ManaPaymentDetail
  ) => void;
}

export function WardPaymentPanel({
  active,
  autoPayWard,
  onToggleAutoPayWard,
  wardTargets,
  manaPool,
  wardPayments,
  wardPaymentDetails,
  wardPaymentErrors,
  onUpdateWardPayment,
  onUpdateWardPaymentDetail,
}: WardPaymentPanelProps) {
  if (!active || wardTargets.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Ward Payment</div>
      <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
        <input
          type="checkbox"
          checked={autoPayWard}
          onChange={(e) => onToggleAutoPayWard(e.target.checked)}
        />
        Auto-pay ward costs
      </label>
      {wardTargets.map((target) => {
        const payments = wardPayments[target.objectId] ?? [];
        const detail = wardPaymentDetails[target.objectId];
        const errors = wardPaymentErrors[target.objectId] ?? [];
        return (
          <div key={`ward-${target.objectId}`} className="rounded border border-[color:var(--theme-input-border)] p-2 space-y-2">
            <div className="text-xs text-[color:var(--theme-text-secondary)]">{target.name}</div>
            {target.hasMultipleCosts && (
              <div className="text-xs text-[color:var(--theme-text-muted)]">
                Multiple ward costs detected; you must satisfy each cost.
              </div>
            )}
            {target.costs.map((entry, index) => {
              const isManaCost = entry.cost.type === 'mana';
              const isComplex = isManaCost ? hasComplexManaCost(entry.cost.cost) : false;
              const payment = payments[index] ?? {};
              return (
                <div key={`ward-cost-${target.objectId}-${index}`} className="space-y-2">
                  <div className="text-xs text-[color:var(--theme-text-secondary)]">
                    Cost {index + 1}: {entry.costLabel ?? entry.cost.type}
                  </div>
                  {!autoPayWard && isManaCost && isComplex && detail && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                      {(entry.cost.cost.hybrids ?? []).map(([colorA, colorB], idx) => (
                        <label key={`ward-hybrid-${target.objectId}-${index}-${idx}`} className="flex items-center gap-2">
                          <span className="text-[color:var(--theme-text-secondary)]">Hybrid</span>
                          <select
                            value={detail.hybrid_choices[idx] ?? colorA}
                            onChange={(e) =>
                              onUpdateWardPaymentDetail(target.objectId, (prev) => {
                                const next = [...prev.hybrid_choices];
                                next[idx] = e.target.value;
                                return { ...prev, hybrid_choices: next };
                              })
                            }
                            className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                          >
                            <option value={colorA}>{colorA}</option>
                            <option value={colorB}>{colorB}</option>
                          </select>
                        </label>
                      ))}
                      {(entry.cost.cost.two_brids ?? []).map(([genericValue, color], idx) => (
                        <label key={`ward-two-brid-${target.objectId}-${index}-${idx}`} className="flex items-center gap-2">
                          <span className="text-[color:var(--theme-text-secondary)]">Two-brid</span>
                          <select
                            value={detail.two_brid_choices[idx] ? 'color' : 'generic'}
                            onChange={(e) =>
                              onUpdateWardPaymentDetail(target.objectId, (prev) => {
                                const next = [...prev.two_brid_choices];
                                next[idx] = e.target.value === 'color';
                                return { ...prev, two_brid_choices: next };
                              })
                            }
                            className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                          >
                            <option value="color">{color}</option>
                            <option value="generic">{genericValue} generic</option>
                          </select>
                        </label>
                      ))}
                      {(entry.cost.cost.phyrexian ?? []).map((color, idx) => (
                        <label key={`ward-phyrexian-${target.objectId}-${index}-${idx}`} className="flex items-center gap-2">
                          <span className="text-[color:var(--theme-text-secondary)]">Phyrexian</span>
                          <select
                            value={detail.phyrexian_choices[idx] ? 'life' : 'mana'}
                            onChange={(e) =>
                              onUpdateWardPaymentDetail(target.objectId, (prev) => {
                                const next = [...prev.phyrexian_choices];
                                next[idx] = e.target.value === 'life';
                                return { ...prev, phyrexian_choices: next };
                              })
                            }
                            className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                          >
                            <option value="mana">{color} mana</option>
                            <option value="life">2 life</option>
                          </select>
                        </label>
                      ))}
                    </div>
                  )}
                  {!autoPayWard && isManaCost && !isComplex && (
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                      {['W', 'U', 'B', 'R', 'G', 'C'].map((color) => (
                        <label key={`ward-mana-${target.objectId}-${index}-${color}`} className="flex items-center gap-2">
                          <span className="w-4 text-[color:var(--theme-text-secondary)]">{color}</span>
                          <input
                            type="number"
                            min={0}
                            max={manaPool[color] ?? 0}
                            value={payment.mana_payment?.[color] ?? 0}
                            onChange={(e) =>
                              onUpdateWardPayment(target.objectId, index, (prev) => ({
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
                  {!autoPayWard && entry.cost.type === 'life' && (
                    <div className="text-xs text-[color:var(--theme-text-secondary)]">
                      Pay {entry.cost.amount} life
                    </div>
                  )}
                  {!autoPayWard && entry.cost.type === 'discard' && (
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-[color:var(--theme-text-secondary)]">Discard</span>
                      <select
                        multiple
                        value={payment.discard_ids ?? []}
                        onChange={(e) =>
                          onUpdateWardPayment(target.objectId, index, (prev) => ({
                            ...prev,
                            discard_ids: Array.from(e.target.selectedOptions).map((option) => option.value),
                          }))
                        }
                        className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                      >
                        {entry.discardOptions.map((option) => (
                          <option key={`ward-discard-${target.objectId}-${index}-${option.value}`} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  {!autoPayWard && entry.cost.type === 'sacrifice' && (
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-[color:var(--theme-text-secondary)]">Sacrifice</span>
                      <select
                        value={payment.sacrifice_id ?? ''}
                        onChange={(e) =>
                          onUpdateWardPayment(target.objectId, index, (prev) => ({
                            ...prev,
                            sacrifice_id: e.target.value || undefined,
                          }))
                        }
                        className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                      >
                        <option value="">Select permanent</option>
                        {entry.sacrificeOptions.map((option) => (
                          <option key={`ward-sac-${target.objectId}-${index}-${option.value}`} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  {!autoPayWard && entry.cost.type === 'tap' && (
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-[color:var(--theme-text-secondary)]">Tap</span>
                      <select
                        value={payment.tap_id ?? ''}
                        onChange={(e) =>
                          onUpdateWardPayment(target.objectId, index, (prev) => ({
                            ...prev,
                            tap_id: e.target.value || undefined,
                          }))
                        }
                        className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                      >
                        <option value="">Select permanent</option>
                        {entry.tapOptions.map((option) => (
                          <option key={`ward-tap-${target.objectId}-${index}-${option.value}`} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
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
      })}
    </div>
  );
}

