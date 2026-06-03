// frontend/components/search/SearchHeader.tsx

import { Button } from '@/components/ui/Button';
import { Sparkles } from 'lucide-react';

interface SearchHeaderProps {
  onRandomClick: () => void;
}

export function SearchHeader({ onRandomClick }: SearchHeaderProps) {
  return (
    <div className="flex w-full items-center justify-between sm:w-auto">
      <Button
        onClick={onRandomClick}
        variant="outline"
        size="sm"
        className="flex w-full items-center justify-center gap-2 sm:w-auto"
      >
        <Sparkles className="w-4 h-4" />
        Random Card
      </Button>
    </div>
  );
}

