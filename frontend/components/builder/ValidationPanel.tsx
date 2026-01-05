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

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Validation</h3>
        <div className="text-sm text-slate-400">
          {totalAbilities} ability{totalAbilities !== 1 ? 'ies' : ''} added
        </div>
      </div>
      
      {validating && (
        <div className="text-sm text-slate-400 mb-4">Validating...</div>
      )}
      
      {!validating && (
        <div className="space-y-3">
          {totalAbilities === 0 && (
            <div className="p-3 bg-slate-700/50 border border-slate-600 rounded text-sm text-slate-400">
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

