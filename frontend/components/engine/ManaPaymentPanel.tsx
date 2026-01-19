'use client';

import { ManaPaymentDetail } from '@/lib/manaPayment';

interface ManaPaymentPanelProps {
  active: boolean;
  cost: any;
  costLabel: string;
  autoPayMana: boolean;
  isComplexCost: boolean;
  manaPool: Record<string, number>;
  manaPayment: Record<string, number>;
  manaPaymentDetail: ManaPaymentDetail;
  errors: string[];
  onToggleAutoPay: (value: boolean) => void;
  onUpdatePaymentDetail: (updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  onUpdateManaPayment: (updater: (prev: Record<string, number>) => Record<string, number>) => void;
}

export function ManaPaymentPanel({
  active,
  cost,
  costLabel,
  autoPayMana,
  isComplexCost,
  manaPool,
  manaPayment,
  manaPaymentDetail,
  errors,
  onToggleAutoPay,
  onUpdatePaymentDetail,
  onUpdateManaPayment,
}: ManaPaymentPanelProps) {
  if (!active) return null;

  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Mana Payment</div>
      <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
        <input
          type="checkbox"
          checked={autoPayMana}
          onChange={(e) => onToggleAutoPay(e.target.checked)}
          disabled={isComplexCost}
        />
        Auto-pay (use recommended payment)
      </label>
      <div className="text-xs text-[color:var(--theme-text-secondary)]">Cost: {costLabel}</div>
      {isComplexCost && (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">
          Choose how to pay hybrid/phyrexian/two-brid symbols.
        </div>
      )}
      {isComplexCost && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          {(cost.hybrids ?? []).map(([colorA, colorB]: [string, string], index: number) => (
            <label key={`hybrid-${index}`} className="flex items-center gap-2">
              <span className="text-[color:var(--theme-text-secondary)]">Hybrid</span>
              <select
                value={manaPaymentDetail.hybrid_choices[index] ?? colorA}
                onChange={(e) =>
                  onUpdatePaymentDetail((prev) => {
                    const next = [...prev.hybrid_choices];
                    next[index] = e.target.value;
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
          {(cost.two_brids ?? []).map(([genericValue, color]: [number, string], index: number) => (
            <label key={`two-brid-${index}`} className="flex items-center gap-2">
              <span className="text-[color:var(--theme-text-secondary)]">Two-brid</span>
              <select
                value={manaPaymentDetail.two_brid_choices[index] ? 'color' : 'generic'}
                onChange={(e) =>
                  onUpdatePaymentDetail((prev) => {
                    const next = [...prev.two_brid_choices];
                    next[index] = e.target.value === 'color';
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
          {(cost.phyrexian ?? []).map((color: string, index: number) => (
            <label key={`phyrexian-${index}`} className="flex items-center gap-2">
              <span className="text-[color:var(--theme-text-secondary)]">Phyrexian</span>
              <select
                value={manaPaymentDetail.phyrexian_choices[index] ? 'life' : 'mana'}
                onChange={(e) =>
                  onUpdatePaymentDetail((prev) => {
                    const next = [...prev.phyrexian_choices];
                    next[index] = e.target.value === 'life';
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
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
        {['W', 'U', 'B', 'R', 'G', 'C'].map((color) => (
          <label key={`mana-${color}`} className="flex items-center gap-2">
            <span className="w-4 text-[color:var(--theme-text-secondary)]">{color}</span>
            <input
              type="number"
              min={0}
              max={manaPool[color] ?? 0}
              value={manaPayment[color] ?? 0}
              onChange={(e) =>
                onUpdateManaPayment((prev) => ({
                  ...prev,
                  [color]: Math.max(0, parseInt(e.target.value || '0', 10)),
                }))
              }
              disabled={autoPayMana || isComplexCost}
              className="w-full px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
            <span className="text-[color:var(--theme-text-secondary)] text-xs">/ {manaPool[color] ?? 0}</span>
          </label>
        ))}
      </div>
      {errors.length > 0 && (
        <div className="text-xs text-[color:var(--theme-status-error)]">{errors.join(' ')}</div>
      )}
    </div>
  );
}

