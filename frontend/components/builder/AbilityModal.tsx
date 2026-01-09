'use client';

// frontend/components/builder/AbilityModal.tsx

import { useEffect } from 'react';
import { TriggeredAbilityForm } from './forms/TriggeredAbilityForm';
import { ActivatedAbilityForm } from './forms/ActivatedAbilityForm';
import { StaticAbilityForm } from './forms/StaticAbilityForm';
import { ContinuousAbilityForm } from './forms/ContinuousAbilityForm';
import { KeywordAbilityForm } from './forms/KeywordAbilityForm';
import { TriggeredAbility, ActivatedAbility, StaticAbility, ContinuousAbility, KeywordAbility } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';

interface AbilityModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'triggered' | 'activated' | 'static' | 'continuous' | 'keyword';
  abilityId?: string; // If provided, we're editing
}

export function AbilityModal({ isOpen, onClose, type, abilityId }: AbilityModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const getTitle = () => {
    const action = abilityId ? 'Edit' : 'Add';
    const typeName = type === 'continuous' ? 'Continuous' : type.charAt(0).toUpperCase() + type.slice(1);
    return `${action} ${typeName} Ability`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white border border-amber-200/50 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <div className="sticky top-0 bg-white border-b border-amber-200/50 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">{getTitle()}</h2>
          <Button
            onClick={onClose}
            variant="ghost"
            size="sm"
            className="text-slate-600 hover:text-slate-900"
            aria-label="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </Button>
        </div>
        
        <div className="p-6">
          {type === 'triggered' && (
            <TriggeredAbilityForm abilityId={abilityId} onSave={onClose} onCancel={onClose} />
          )}
          {type === 'activated' && (
            <ActivatedAbilityForm abilityId={abilityId} onSave={onClose} onCancel={onClose} />
          )}
          {type === 'static' && (
            <StaticAbilityForm abilityId={abilityId} onSave={onClose} onCancel={onClose} />
          )}
          {type === 'continuous' && (
            <ContinuousAbilityForm abilityId={abilityId} onSave={onClose} onCancel={onClose} />
          )}
          {type === 'keyword' && (
            <KeywordAbilityForm abilityId={abilityId} onSave={onClose} onCancel={onClose} />
          )}
        </div>
      </div>
    </div>
  );
}

