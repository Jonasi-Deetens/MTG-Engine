'use client';

// frontend/components/builder/ValidationPanel.tsx

import { useEffect, useState } from 'react';
import { useEffectStore } from '@/store/effectStore';
import { effects } from '@/lib/effects';
import { getEffectGraphWarnings } from '@/lib/effectValidation';
import { getErrorMessage } from '@/lib/utils/errors';
import { Button } from '@/components/ui/Button';

export function ValidationPanel() {
  const {
    currentCard,
    toEffectGraph,
    setValidation,
    validation,
    steps,
  } = useEffectStore();

  const [validating, setValidating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const validateGraph = async () => {
      const graph = toEffectGraph();
      
      if (!graph) {
        setValidation([], [], false);
        return;
      }

      setValidating(true);
      try {
        const result = await effects.validate(graph);
        const warnings = getEffectGraphWarnings(graph);
        setValidation(result.errors, warnings, result.valid);
      } catch (error) {
        console.error('Validation error:', error);
        const warnings = getEffectGraphWarnings(graph);
        setValidation(
          [getErrorMessage(error) || 'Failed to validate effects'],
          warnings,
          false
        );
      } finally {
        setValidating(false);
      }
    };

    // Debounce validation
    const timeoutId = setTimeout(validateGraph, 500);
    return () => clearTimeout(timeoutId);
  }, [
    steps,
    currentCard,
    toEffectGraph,
    setValidation,
  ]);

  const totalAbilities = steps.length;

  const handleExport = () => {
    const graph = toEffectGraph();
    if (!graph) {
      alert('No abilities to export');
      return;
    }
    const json = JSON.stringify(graph, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentCard?.name || 'ability-graph'}-graph.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleShare = async () => {
    if (currentCard) {
      const url = `${window.location.origin}/cards/${currentCard.card_id}`;
      try {
        await navigator.clipboard.writeText(url);
        alert('Card link copied to clipboard!');
      } catch (err) {
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Card link copied to clipboard!');
      }
    }
  };

  const handleSave = async () => {
    console.log('Save clicked, currentCard:', currentCard);
    if (!currentCard) {
      setSaveMessage({ type: 'error', text: 'No card selected' });
      return;
    }

    const cardId = currentCard.card_id;
    console.log('Card ID to save:', cardId);
    if (!cardId) {
      console.error('Card ID is missing! Card object:', currentCard);
      setSaveMessage({ type: 'error', text: 'Card ID is missing. Please select a card again.' });
      return;
    }

    const graph = toEffectGraph();
    if (!graph) {
      setSaveMessage({ type: 'error', text: 'No abilities to save' });
      return;
    }

    setSaving(true);
    setSaveMessage(null);
    try {
      console.log('Saving graph for card_id:', cardId);
      await effects.saveCardEffectGraph(cardId, graph);
      setSaveMessage({ 
        type: 'success', 
        text: 'Effect graph saved successfully to all versions!' 
      });
      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error: any) {
      console.error('Save error:', error);
      setSaveMessage({ 
        type: 'error', 
        text: getErrorMessage(error) || 'Failed to save effect graph' 
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-[color:var(--theme-text-primary)]">Validation</h3>
        <div className="flex items-center gap-2">
          <div className="text-sm text-[color:var(--theme-text-secondary)]">
            {totalAbilities} effect{totalAbilities !== 1 ? 's' : ''} added
          </div>
          {totalAbilities > 0 && (
            <Button
              onClick={handleExport}
              variant="outline"
              size="sm"
            >
              Export JSON
            </Button>
          )}
          {currentCard && (
            <>
              <Button
                onClick={handleShare}
                variant="outline"
                size="sm"
              >
                Share Card
              </Button>
              <Button
                onClick={handleSave}
                disabled={saving || totalAbilities === 0}
                variant="primary"
                size="sm"
              >
                {saving ? 'Saving...' : 'Save Graph'}
              </Button>
            </>
          )}
        </div>
      </div>
      
      {saveMessage && (
        <div
          className={`mb-4 p-3 rounded text-sm ${
            saveMessage.type === 'success'
              ? 'bg-[color:var(--theme-status-success)]/20 text-[color:var(--theme-status-success)] border border-[color:var(--theme-status-success)]/50'
              : 'bg-[color:var(--theme-status-error)]/20 text-[color:var(--theme-status-error)] border border-[color:var(--theme-status-error)]/50'
          }`}
        >
          {saveMessage.type === 'success' ? '✓' : '✗'} {saveMessage.text}
        </div>
      )}
      
      {validating && (
        <div className="text-sm text-[color:var(--theme-text-muted)] mb-4">Validating...</div>
      )}
      
      {!validating && (
        <div className="space-y-3">
          {totalAbilities === 0 && (
            <div className="p-3 bg-[color:var(--theme-card-hover)] border border-[color:var(--theme-card-border)] rounded text-sm text-[color:var(--theme-text-secondary)]">
              No effects added yet. Add an effect to start building.
            </div>
          )}
          
          {totalAbilities > 0 && validation.isValid && (
            <div className="p-3 bg-[color:var(--theme-status-success)]/20 border border-[color:var(--theme-status-success)]/50 rounded text-sm text-[color:var(--theme-status-success)]">
              ✓ All effects are valid
            </div>
          )}
          
          {validation.errors.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-[color:var(--theme-status-error)]">Errors</h4>
              {validation.errors.map((error, index) => (
                <div
                  key={index}
                  className="p-3 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded text-sm text-[color:var(--theme-status-error)]"
                >
                  ✗ {error}
                </div>
              ))}
            </div>
          )}
          
          {validation.warnings.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-[color:var(--theme-status-warning)]">Warnings</h4>
              {validation.warnings.map((warning, index) => (
                <div
                  key={index}
                  className="p-3 bg-[color:var(--theme-status-warning)]/20 border border-[color:var(--theme-status-warning)]/50 rounded text-sm text-[color:var(--theme-status-warning)]"
                >
                  ⚠ {warning}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

