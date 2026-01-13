'use client';

// frontend/components/decks/CustomListManager.tsx

import { useState } from 'react';
import { DeckCustomListResponse, DeckCustomListUpdate } from '@/lib/decks';
import { Button } from '@/components/ui/Button';

interface CustomListManagerProps {
  customLists: DeckCustomListResponse[];
  onCreate: (name: string) => void;
  onUpdate: (listId: number, updates: DeckCustomListUpdate) => void;
  onDelete: (listId: number) => void;
}

export function CustomListManager({
  customLists,
  onCreate,
  onUpdate,
  onDelete,
}: CustomListManagerProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');

  const handleCreate = () => {
    if (newListName.trim()) {
      onCreate(newListName.trim());
      setNewListName('');
      setShowCreateForm(false);
    }
  };

  const handleStartEdit = (list: DeckCustomListResponse) => {
    setEditingId(list.id);
    setEditName(list.name);
  };

  const handleSaveEdit = (listId: number) => {
    if (editName.trim()) {
      onUpdate(listId, { name: editName.trim() });
      setEditingId(null);
      setEditName('');
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditName('');
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-[color:var(--theme-text-primary)]">Custom Lists</h4>
        {!showCreateForm && (
          <Button
            onClick={() => setShowCreateForm(true)}
            variant="outline"
            size="xs"
          >
            + New List
          </Button>
        )}
      </div>

      {showCreateForm && (
        <div className="flex gap-2 p-2 bg-[color:var(--theme-bg-secondary)] rounded">
          <input
            type="text"
            value={newListName}
            onChange={(e) => setNewListName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleCreate();
              if (e.key === 'Escape') {
                setShowCreateForm(false);
                setNewListName('');
              }
            }}
            placeholder="List name..."
            className="flex-1 px-2 py-1 text-xs bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            autoFocus
          />
          <Button
            onClick={handleCreate}
            variant="primary"
            size="xs"
            disabled={!newListName.trim()}
          >
            Create
          </Button>
          <Button
            onClick={() => {
              setShowCreateForm(false);
              setNewListName('');
            }}
            variant="outline"
            size="xs"
          >
            Cancel
          </Button>
        </div>
      )}

      <div className="space-y-1">
        {customLists.map((list) => (
          <div
            key={list.id}
            className="flex items-center gap-2 px-2 py-1.5 bg-[color:var(--theme-card-bg)] rounded hover:bg-[color:var(--theme-card-hover)] transition-colors"
          >
            {editingId === list.id ? (
              <>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveEdit(list.id);
                    if (e.key === 'Escape') handleCancelEdit();
                  }}
                  className="flex-1 px-2 py-1 text-xs bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  autoFocus
                />
                <Button
                  onClick={() => handleSaveEdit(list.id)}
                  variant="primary"
                  size="xs"
                  disabled={!editName.trim()}
                >
                  Save
                </Button>
                <Button
                  onClick={handleCancelEdit}
                  variant="outline"
                  size="xs"
                >
                  Cancel
                </Button>
              </>
            ) : (
              <>
                <span className="flex-1 text-xs text-[color:var(--theme-text-primary)]">{list.name}</span>
                <Button
                  onClick={() => handleStartEdit(list)}
                  variant="outline"
                  size="xs"
                >
                  Edit
                </Button>
                <Button
                  onClick={() => onDelete(list.id)}
                  variant="outline"
                  size="xs"
                  className="text-[color:var(--theme-status-error)] hover:bg-[color:var(--theme-status-error)]/20"
                >
                  Delete
                </Button>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

