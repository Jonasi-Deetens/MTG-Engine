'use client';

import { Effect } from '@/store/builderStore';
import { EffectFields } from './EffectFields';
import { Button } from '@/components/ui/Button';
import { updateEffectsWithField } from './abilityFormHelpers';

interface AbilityEffectsSectionProps {
  effects: Effect[];
  setEffects: React.Dispatch<React.SetStateAction<Effect[]>>;
  isModal: boolean;
  setIsModal: React.Dispatch<React.SetStateAction<boolean>>;
  modalMin: number;
  setModalMin: React.Dispatch<React.SetStateAction<number>>;
  modalMax: number | null | '';
  setModalMax: React.Dispatch<React.SetStateAction<number | null | ''>>;
  modalModes: Array<{ id: string; label: string }>;
  setModalModes: React.Dispatch<React.SetStateAction<Array<{ id: string; label: string }>>>;
}

export function AbilityEffectsSection({
  effects,
  setEffects,
  isModal,
  setIsModal,
  modalMin,
  setModalMin,
  modalMax,
  setModalMax,
  modalModes,
  setModalModes,
}: AbilityEffectsSectionProps) {
  const handleAddEffect = () => {
    setEffects((prev) => [...prev, { type: 'damage', amount: 0 }]);
  };

  const handleRemoveEffect = (index: number) => {
    setEffects((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpdateEffect = (index: number, field: string, value: any) => {
    setEffects((prev) => updateEffectsWithField(prev, index, field, value));
  };

  const handleAddMode = () => {
    setModalModes((prev) => [...prev, { id: `mode-${prev.length + 1}`, label: `Mode ${prev.length + 1}` }]);
  };

  const handleRemoveMode = (index: number) => {
    setModalModes((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpdateMode = (index: number, field: 'id' | 'label', value: string) => {
    setModalModes((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-[color:var(--theme-text-secondary)]">
          <input type="checkbox" checked={isModal} onChange={(e) => setIsModal(e.target.checked)} />
          Modal ability (choose modes on cast/activation)
        </label>
        {isModal && (
          <div className="space-y-3 rounded border border-[color:var(--theme-card-border)] p-3 bg-[color:var(--theme-card-hover)]">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Min modes</label>
                <input
                  type="number"
                  min="0"
                  value={modalMin}
                  onChange={(e) => setModalMin(parseInt(e.target.value, 10) || 0)}
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Max modes</label>
                <input
                  type="number"
                  min="1"
                  value={modalMax === null ? '' : modalMax}
                  onChange={(e) =>
                    setModalMax(e.target.value === '' ? null : parseInt(e.target.value, 10) || 1)
                  }
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-[color:var(--theme-text-secondary)]">Modes</span>
                <Button onClick={handleAddMode} variant="secondary" size="xs">
                  + Add Mode
                </Button>
              </div>
              {modalModes.length === 0 ? (
                <p className="text-xs text-[color:var(--theme-text-secondary)]">No modes yet.</p>
              ) : (
                <div className="space-y-2">
                  {modalModes.map((mode, index) => (
                    <div key={`${mode.id}-${index}`} className="grid grid-cols-[1fr_2fr_auto] gap-2 items-center">
                      <input
                        value={mode.id}
                        onChange={(e) => handleUpdateMode(index, 'id', e.target.value)}
                        placeholder="mode-id"
                        className="px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-xs focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                      />
                      <input
                        value={mode.label}
                        onChange={(e) => handleUpdateMode(index, 'label', e.target.value)}
                        placeholder="Mode label"
                        className="px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-xs focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                      />
                      <Button onClick={() => handleRemoveMode(index)} variant="danger" size="xs">
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {effects.map((effect, index) => (
          <div
            key={`${effect.type || 'effect'}-${index}`}
            className="border border-[color:var(--theme-border-default)] rounded p-4 space-y-2 bg-[color:var(--theme-card-hover)]"
          >
            <div className="flex justify-between items-center">
              <h4 className="text-sm font-medium text-[color:var(--theme-text-primary)]">
                Effect {index + 1}
              </h4>
              <Button onClick={() => handleRemoveEffect(index)} variant="danger" size="xs">
                Remove
              </Button>
            </div>
            <EffectFields
              effect={effect}
              index={index}
              allEffects={effects}
              modeOptions={
                isModal
                  ? modalModes.map((mode) => ({ value: mode.id, label: mode.label || mode.id }))
                  : []
              }
              onUpdate={(field, value) => handleUpdateEffect(index, field, value)}
            />
          </div>
        ))}
        <Button onClick={handleAddEffect} variant="secondary" size="sm">
          + Add Effect
        </Button>
      </div>
    </div>
  );
}
