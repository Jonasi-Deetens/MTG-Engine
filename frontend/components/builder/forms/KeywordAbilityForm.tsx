'use client';

// frontend/components/builder/forms/KeywordAbilityForm.tsx

import { useState, useEffect } from 'react';
import { useBuilderStore, KeywordAbility, KeywordInfo } from '@/store/builderStore';
import { abilities } from '@/lib/abilities';
import { Button } from '@/components/ui/Button';

interface KeywordAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

export function KeywordAbilityForm({ abilityId, onSave, onCancel }: KeywordAbilityFormProps) {
  const { keywords, addKeyword, updateKeyword } = useBuilderStore();
  
  const existingKeyword = abilityId ? keywords.find((k) => k.id === abilityId) : null;
  
  const [availableKeywords, setAvailableKeywords] = useState<KeywordInfo[]>([]);
  const [selectedKeywordName, setSelectedKeywordName] = useState(existingKeyword?.keyword || '');
  const [cost, setCost] = useState(existingKeyword?.cost || '');
  const [number, setNumber] = useState(existingKeyword?.number || undefined);
  const [lifeCost, setLifeCost] = useState(existingKeyword?.lifeCost || undefined);
  const [sacrificeCost, setSacrificeCost] = useState(existingKeyword?.sacrificeCost || false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadKeywords = async () => {
      setLoading(true);
      try {
        const response = await abilities.listKeywords();
        if (response.keywords) {
          setAvailableKeywords(response.keywords);
        }
      } catch (error) {
        console.error('Failed to load keywords:', error);
      } finally {
        setLoading(false);
      }
    };
    loadKeywords();
  }, []);

  const selectedKeyword = availableKeywords.find((k) => k.name === selectedKeywordName);

  const handleSave = () => {
    const keyword: KeywordAbility = {
      id: abilityId || `keyword-${Date.now()}`,
      keyword: selectedKeywordName,
      cost: cost || undefined,
      number: number !== undefined ? number : undefined,
      lifeCost: lifeCost !== undefined ? lifeCost : undefined,
      sacrificeCost: sacrificeCost || undefined,
    };

    if (abilityId) {
      updateKeyword(abilityId, keyword);
    } else {
      addKeyword(keyword);
    }
    onSave();
  };

  return (
    <div className="space-y-6">
      {/* Keyword Selection */}
      <div>
        <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
          Keyword *
        </label>
        {loading ? (
          <div className="text-sm text-[color:var(--theme-text-secondary)]">Loading keywords...</div>
        ) : (
          <select
            value={selectedKeywordName}
            onChange={(e) => {
              setSelectedKeywordName(e.target.value);
              // Reset parameters when keyword changes
              setCost('');
              setNumber(undefined);
              setLifeCost(undefined);
              setSacrificeCost(false);
            }}
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            <option value="">Select a keyword...</option>
            {availableKeywords.map((kw) => (
              <option key={kw.name} value={kw.name}>
                {kw.name}
              </option>
            ))}
          </select>
        )}
        {selectedKeyword?.options.description && (
          <p className="text-xs text-[color:var(--theme-text-secondary)] mt-1">{selectedKeyword.options.description}</p>
        )}
      </div>

      {/* Parameter Fields */}
      {selectedKeyword && (
        <div className="space-y-4">
          {selectedKeyword.options.has_mana_cost && (
            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Mana Cost
              </label>
              <input
                type="text"
                value={cost}
                onChange={(e) => setCost(e.target.value)}
                placeholder="e.g., {2}, {1}{R}"
                className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
            </div>
          )}

          {selectedKeyword.options.has_number && (
            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Number Value
              </label>
              <input
                type="number"
                value={number || ''}
                onChange={(e) => setNumber(e.target.value ? parseInt(e.target.value) : undefined)}
                min="0"
                placeholder="e.g., 2 for Annihilator 2"
                className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
            </div>
          )}

          {selectedKeyword.options.has_life_cost && (
            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Life Cost
              </label>
              <input
                type="number"
                value={lifeCost || ''}
                onChange={(e) => setLifeCost(e.target.value ? parseInt(e.target.value) : undefined)}
                min="0"
                placeholder="e.g., 3"
                className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
            </div>
          )}

          {selectedKeyword.options.has_sacrifice_cost && (
            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={sacrificeCost}
                  onChange={(e) => setSacrificeCost(e.target.checked)}
                    className="w-4 h-4 rounded border-[color:var(--theme-input-border)] bg-[color:var(--theme-input-bg)] text-[color:var(--theme-accent-primary)] focus:ring-[color:var(--theme-border-focus)]"
                />
                <span className="text-sm font-medium text-[color:var(--theme-text-secondary)]">Requires Sacrifice Cost</span>
              </label>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-[color:var(--theme-border-default)]">
        <Button
          onClick={handleSave}
          disabled={!selectedKeywordName}
          variant="primary"
          className="flex-1"
        >
          Save
        </Button>
        <Button
          onClick={onCancel}
          variant="secondary"
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}

