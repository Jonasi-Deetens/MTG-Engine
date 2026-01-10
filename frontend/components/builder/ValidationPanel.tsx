'use client';

// frontend/components/builder/ValidationPanel.tsx

import { useEffect, useState } from 'react';
import { useBuilderStore } from '@/store/builderStore';
import { abilities } from '@/lib/abilities';
import { Button } from '@/components/ui/Button';

export function ValidationPanel() {
  const {
    currentCard,
    convertToGraph,
    setValidation,
    validationErrors,
    validationWarnings,
    isValid,
    triggeredAbilities,
    activatedAbilities,
    staticAbilities,
    continuousAbilities,
    keywords,
  } = useBuilderStore();

  const [validating, setValidating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const validateGraph = async () => {
      const graph = convertToGraph();
      
      if (!graph) {
        setValidation([], [], false);
        return;
      }

      setValidating(true);
      try {
        const result = await abilities.validate(graph, currentCard?.colors);
        setValidation(result.errors, result.warnings, result.valid);
      } catch (error) {
        console.error('Validation error:', error);
        setValidation(
          [{ type: 'error', message: 'Failed to validate abilities' }],
          [],
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
    triggeredAbilities,
    activatedAbilities,
    staticAbilities,
    continuousAbilities,
    keywords,
    currentCard,
    convertToGraph,
    setValidation,
  ]);

  const totalAbilities =
    triggeredAbilities.length +
    activatedAbilities.length +
    staticAbilities.length +
    continuousAbilities.length +
    keywords.length;

  const handleExport = () => {
    const graph = convertToGraph();
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

    const graph = convertToGraph();
    if (!graph) {
      setSaveMessage({ type: 'error', text: 'No abilities to save' });
      return;
    }

    setSaving(true);
    setSaveMessage(null);
    try {
      console.log('Saving graph for card_id:', cardId);
      await abilities.saveCardGraph(cardId, graph);
      setSaveMessage({ 
        type: 'success', 
        text: 'Ability graph saved successfully to all versions!' 
      });
      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error: any) {
      console.error('Save error:', error);
      setSaveMessage({ 
        type: 'error', 
        text: error.message || 'Failed to save ability graph' 
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
            {totalAbilities} ability{totalAbilities !== 1 ? 'ies' : ''} added
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
        <div className={`mb-4 p-3 rounded text-sm ${
          saveMessage.type === 'success' 
            ? 'bg-green-900/50 text-green-200 border border-green-600' 
            : 'bg-red-900/50 text-red-200 border border-red-600'
        }`}>
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
              No abilities added yet. Add abilities using the tabs above.
            </div>
          )}
          
          {totalAbilities > 0 && isValid && (
            <div className="p-3 bg-green-900/30 border border-green-600 rounded text-sm text-green-200">
              ✓ All abilities are valid
            </div>
          )}
          
          {validationErrors.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-red-300">Errors</h4>
              {validationErrors.map((error, index) => (
                <div
                  key={index}
                  className="p-3 bg-red-900/30 border border-red-600 rounded text-sm text-red-200"
                >
                  ✗ {error.message}
                </div>
              ))}
            </div>
          )}
          
          {validationWarnings.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-yellow-300">Warnings</h4>
              {validationWarnings.map((warning, index) => (
                <div
                  key={index}
                  className="p-3 bg-yellow-900/30 border border-yellow-600 rounded text-sm text-yellow-200"
                >
                  ⚠ {warning.message}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

