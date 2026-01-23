'use client';

// frontend/components/builder/forms/KeywordAbilityForm.tsx

import { useState, useEffect } from 'react';
import { useBuilderStore, KeywordAbility, KeywordInfo } from '@/store/builderStore';
import { abilities } from '@/lib/abilities';
import { Button } from '@/components/ui/Button';
import { CostListEditor } from '../CostListEditor';

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
  const [costs, setCosts] = useState(existingKeyword?.costs ?? []);
  const [extraCosts, setExtraCosts] = useState(existingKeyword?.extraCosts ?? []);
  const [number, setNumber] = useState(existingKeyword?.number || undefined);
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
      costs: costs.length ? costs : undefined,
      number: number !== undefined ? number : undefined,
      extraCosts: extraCosts.length ? extraCosts : undefined,
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
              setNumber(undefined);
              setCosts([]);
              setExtraCosts([]);
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
          {selectedKeyword.options.has_cost && (
            <CostListEditor label="Keyword Costs" value={costs} onChange={setCosts} />
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

          {['escape', 'jump-start'].includes(selectedKeyword.name?.toLowerCase() ?? '') && (
            <CostListEditor label="Extra Costs" value={extraCosts} onChange={setExtraCosts} />
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

