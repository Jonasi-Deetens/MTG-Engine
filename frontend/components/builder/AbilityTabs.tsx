'use client';

// frontend/components/builder/AbilityTabs.tsx

import { useState } from 'react';
import { AbilityList } from './AbilityList';
import { AbilityModal } from './AbilityModal';

type TabType = 'triggered' | 'activated' | 'static' | 'continuous' | 'keyword';

export function AbilityTabs() {
  const [activeTab, setActiveTab] = useState<TabType>('triggered');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | undefined>(undefined);

  const tabs: { id: TabType; label: string }[] = [
    { id: 'triggered', label: 'Triggered' },
    { id: 'activated', label: 'Activated' },
    { id: 'static', label: 'Static' },
    { id: 'continuous', label: 'Continuous' },
    { id: 'keyword', label: 'Keywords' },
  ];

  const handleAdd = () => {
    setEditingId(undefined);
    setModalOpen(true);
  };

  const handleEdit = (id: string) => {
    setEditingId(id);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingId(undefined);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Tab Navigation */}
      <div className="flex border-b border-[color:var(--theme-border-default)] mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium text-sm transition-colors ${
              activeTab === tab.id
                ? 'text-[color:var(--theme-accent-primary)] border-b-2 border-[color:var(--theme-accent-primary)]'
                : 'text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        <AbilityList
          type={activeTab}
          onAdd={handleAdd}
          onEdit={handleEdit}
        />
      </div>

      {/* Modal */}
      <AbilityModal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        type={activeTab}
        abilityId={editingId}
      />
    </div>
  );
}

