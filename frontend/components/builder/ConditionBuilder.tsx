'use client';

// frontend/components/builder/ConditionBuilder.tsx

import { useState, useEffect, useRef } from 'react';
import { StructuredCondition, CONDITION_TYPE_OPTIONS, COMPARISON_OPERATORS, PERMANENT_TYPES, CONDITION_TARGET_OPTIONS } from '@/lib/conditionTypes';
import { Button } from '@/components/ui/Button';

interface ConditionBuilderProps {
  condition: StructuredCondition | string | undefined;
  onChange: (condition: StructuredCondition | undefined) => void;
  onRemove?: () => void;
}

export function ConditionBuilder({ condition, onChange, onRemove }: ConditionBuilderProps) {
  // Parse initial condition (handle both string and structured)
  const getInitialCondition = (): StructuredCondition | undefined => {
    if (!condition) return undefined;
    if (typeof condition === 'string') {
      // Try to parse legacy string conditions (basic support)
      return undefined; // For now, start fresh with structured
    }
    return condition as StructuredCondition;
  };

  const [conditionType, setConditionType] = useState<string>(getInitialCondition()?.type || 'control_count');
  const [value, setValue] = useState<number>(getInitialCondition()?.value || 1);
  const [comparison, setComparison] = useState<string>(getInitialCondition()?.comparison || '>=');
  const [target, setTarget] = useState<string>(getInitialCondition()?.target || 'self');
  const [permanentType, setPermanentType] = useState<string>(getInitialCondition()?.permanentType || 'creature');
  const [keyword, setKeyword] = useState<string>(getInitialCondition()?.keyword || '');
  const [counterType, setCounterType] = useState<string>(getInitialCondition()?.counterType || '+1/+1');
  const [manaValue, setManaValue] = useState<number>(getInitialCondition()?.manaValue || 0);
  const [source, setSource] = useState<string>(getInitialCondition()?.source || 'triggering_source');

  const selectedConditionType = CONDITION_TYPE_OPTIONS.find((opt) => opt.value === conditionType);
  const lastConditionRef = useRef<string>('');
  const onChangeRef = useRef(onChange);

  // Keep onChange ref up to date
  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useEffect(() => {
    // Only update if we have a valid condition type
    if (!selectedConditionType) {
      return;
    }

    const structuredCondition: StructuredCondition = {
      type: conditionType,
    };

    if (selectedConditionType.requiresValue) {
      structuredCondition.value = value;
    }
    if (selectedConditionType.requiresComparison) {
      structuredCondition.comparison = comparison;
    }
    if (selectedConditionType.requiresTarget) {
      structuredCondition.target = target;
    }
    if (selectedConditionType.requiresType) {
      structuredCondition.permanentType = permanentType;
    }
    if (conditionType === 'has_keyword') {
      structuredCondition.keyword = keyword;
    }
    if (conditionType === 'has_counter') {
      structuredCondition.counterType = counterType;
    }
    if (conditionType === 'mana_value_comparison') {
      if (source && source !== 'triggering_source') {
        structuredCondition.source = source;
      } else if (manaValue !== undefined && manaValue > 0) {
        structuredCondition.manaValue = manaValue;
        structuredCondition.value = manaValue;
      } else {
        structuredCondition.source = 'triggering_source';
      }
    }

    // Create a stable string representation to compare
    const conditionString = JSON.stringify(structuredCondition);
    
    // Only call onChange if the condition actually changed
    if (conditionString !== lastConditionRef.current) {
      lastConditionRef.current = conditionString;
      onChangeRef.current(structuredCondition);
    }
  }, [conditionType, value, comparison, target, permanentType, keyword, counterType, manaValue, source, selectedConditionType]);

  // Sync internal state when external condition prop changes (but avoid loops)
  useEffect(() => {
    if (condition && typeof condition !== 'string') {
      const cond = condition as StructuredCondition;
      const condString = JSON.stringify(cond);
      
      // Only update if the external condition is different from what we have
      if (condString !== lastConditionRef.current) {
        setConditionType(cond.type);
        setValue(cond.value ?? 1);
        setComparison(cond.comparison ?? '>=');
        setTarget(cond.target ?? 'self');
        setPermanentType(cond.permanentType ?? 'creature');
        setKeyword(cond.keyword ?? '');
        setCounterType(cond.counterType ?? '+1/+1');
        setManaValue(cond.manaValue ?? 0);
        setSource(cond.source ?? 'triggering_source');
        lastConditionRef.current = condString;
      }
    } else if (!condition && lastConditionRef.current !== '') {
      // Condition was removed externally, reset
      lastConditionRef.current = '';
    }
  }, [condition]);

  return (
    <div className="space-y-3 bg-[color:var(--theme-card-hover)] rounded-lg p-4 border border-[color:var(--theme-card-border)]">
      {onRemove && (
        <div className="flex justify-end mb-2">
          <Button
            type="button"
            onClick={onRemove}
            variant="link"
            size="xs"
            className="text-[color:var(--theme-status-error)] hover:opacity-80"
          >
            Remove
          </Button>
        </div>
      )}
      <div>
        <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Condition Type</label>
        <select
          value={conditionType}
          onChange={(e) => {
            setConditionType(e.target.value);
            // Reset dependent fields when type changes
            setValue(1);
            setComparison('>=');
            setTarget('self');
            setPermanentType('creature');
            setKeyword('');
            setCounterType('+1/+1');
            setManaValue(0);
            setSource('triggering_source');
          }}
          className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
        >
          {CONDITION_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {selectedConditionType?.requiresValue && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Value</label>
          <input
            type="number"
            value={value}
            onChange={(e) => setValue(parseInt(e.target.value) || 0)}
            min="0"
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
        </div>
      )}

      {selectedConditionType?.requiresComparison && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Comparison</label>
          <select
            value={comparison}
            onChange={(e) => setComparison(e.target.value)}
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {COMPARISON_OPERATORS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {selectedConditionType?.requiresTarget && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Target</label>
          <select
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {CONDITION_TARGET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {selectedConditionType?.requiresType && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Permanent Type</label>
          <select
            value={permanentType}
            onChange={(e) => setPermanentType(e.target.value)}
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {PERMANENT_TYPES.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {conditionType === 'has_keyword' && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Keyword</label>
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="e.g., flying, haste"
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
        </div>
      )}

      {conditionType === 'has_counter' && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Counter Type</label>
          <input
            type="text"
            value={counterType}
            onChange={(e) => setCounterType(e.target.value)}
            placeholder="e.g., +1/+1, -1/-1, loyalty"
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
        </div>
      )}

      {conditionType === 'mana_value_comparison' && (
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Compare Against</label>
            <select
              value={source}
              onChange={(e) => {
                setSource(e.target.value);
                if (e.target.value !== 'triggering_source') {
                  setManaValue(0);
                }
              }}
              className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {CONDITION_TARGET_OPTIONS.filter(opt => 
                opt.value === 'triggering_source' || 
                opt.value === 'triggering_aura' || 
                opt.value === 'triggering_spell' ||
                opt.value === 'self' ||
                opt.value === 'target_permanent'
              ).map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          {source === 'triggering_source' || source === 'triggering_aura' || source === 'triggering_spell' ? (
            <p className="text-xs text-[color:var(--theme-text-muted)]">Will compare against the triggering source's mana value</p>
          ) : (
            <div>
              <label className="block text-xs text-[color:var(--theme-text-muted)] mb-1">Fixed Mana Value</label>
              <input
                type="number"
                value={manaValue}
                onChange={(e) => setManaValue(parseInt(e.target.value) || 0)}
                min="0"
                className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

