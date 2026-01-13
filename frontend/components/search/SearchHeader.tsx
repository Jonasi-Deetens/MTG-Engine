// frontend/components/search/SearchHeader.tsx

import { Button } from '@/components/ui/Button';
import { Sparkles } from 'lucide-react';

interface SearchHeaderProps {
  onRandomClick: () => void;
}

export function SearchHeader({ onRandomClick }: SearchHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      <h1 className="text-3xl font-bold text-[color:var(--theme-text-primary)]">Search Cards</h1>
      <Button
        onClick={onRandomClick}
        variant="outline"
        size="sm"
        className="flex items-center gap-2"
      >
        <Sparkles className="w-4 h-4" />
        Random Card
      </Button>
    </div>
  );
}

