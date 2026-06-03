'use client';

// frontend/components/decks/DeckValidationPanel.tsx

import { DeckValidationResponse } from '@/lib/decks';

interface DeckValidationPanelProps {
  validation: DeckValidationResponse | null;
}

export function DeckValidationPanel({ validation }: DeckValidationPanelProps) {
  if (!validation) {
    return (
      <div className="p-4 bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-lg">
        <p className="text-[color:var(--theme-text-secondary)] text-sm">Validation not available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div
        className={`p-4 rounded-lg ${
          validation.is_valid
            ? 'bg-[color:var(--theme-status-success)]/20 border border-[color:var(--theme-status-success)]/50'
            : 'bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50'
        }`}
      >
        <div className="flex items-center gap-2 mb-2">
          {validation.is_valid ? (
            <>
              <svg className="w-5 h-5 text-[color:var(--theme-status-success)]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <h3 className="font-semibold text-[color:var(--theme-status-success)]">Deck is Valid</h3>
            </>
          ) : (
            <>
              <svg className="w-5 h-5 text-[color:var(--theme-status-error)]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <h3 className="font-semibold text-[color:var(--theme-status-error)]">Deck has Errors</h3>
            </>
          )}
        </div>
        <p className="text-sm text-[color:var(--theme-text-secondary)]">
          Format: {validation.format} | Cards: {validation.card_count} | Commanders: {validation.commander_count}
        </p>
      </div>

      {validation.errors.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-semibold text-[color:var(--theme-status-error)]">Errors</h4>
          <ul className="space-y-1">
            {validation.errors.map((error, index) => (
              <li key={index} className="text-sm text-[color:var(--theme-status-error)]/80 flex items-start gap-2">
                <span className="text-[color:var(--theme-status-error)]">×</span>
                <span>{error.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {validation.warnings.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-semibold text-[color:var(--theme-status-warning)]">Warnings</h4>
          <ul className="space-y-1">
            {validation.warnings.map((warning, index) => (
              <li key={index} className="text-sm text-[color:var(--theme-status-warning)]/80 flex items-start gap-2">
                <span className="text-[color:var(--theme-status-warning)]">!</span>
                <span>{warning.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

