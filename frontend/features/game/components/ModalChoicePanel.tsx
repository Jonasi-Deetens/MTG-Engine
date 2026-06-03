'use client';

import { ModalChoiceConfig } from '@/lib/modalChoices';

interface ModalChoicePanelProps {
  config: ModalChoiceConfig | null;
  selectedModes: string[];
  errors: string[];
  onToggleMode: (modeId: string) => void;
  disabled?: boolean;
}

export function ModalChoicePanel({ config, selectedModes, errors, onToggleMode, disabled = false }: ModalChoicePanelProps) {
  if (!config) return null;
  const isSingle = config.max === 1 && config.min === 1;
  const selection = new Set(selectedModes);
  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Modal Choices</div>
      <div className="text-xs text-[color:var(--theme-text-secondary)]">
        {config.max === null
          ? `Choose ${config.min}+ mode(s).`
          : config.min === config.max
          ? `Choose ${config.min} mode(s).`
          : `Choose ${config.min}-${config.max} mode(s).`}
      </div>
      <div className="flex flex-col gap-2">
        {config.modes.map((mode) => {
          const checked = selection.has(mode.id);
          return (
            <label key={`mode-${mode.id}`} className="flex items-center gap-2 text-xs">
              <input
                type={isSingle ? 'radio' : 'checkbox'}
                name="modal-choice"
                value={mode.id}
                checked={checked}
                onChange={() => onToggleMode(mode.id)}
                disabled={disabled}
              />
              <span>{mode.label}</span>
            </label>
          );
        })}
      </div>
      {errors.length > 0 && (
        <div className="text-xs text-[color:var(--theme-status-error)]">{errors.join(' ')}</div>
      )}
    </div>
  );
}

