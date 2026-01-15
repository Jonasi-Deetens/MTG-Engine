'use client';

import { Card } from '@/components/ui/Card';
import { EngineStackItemSnapshot } from '@/lib/engine';

interface StackViewProps {
  stack: EngineStackItemSnapshot[];
}

export function StackView({ stack }: StackViewProps) {
  return (
    <Card variant="bordered" className="p-4 space-y-2">
      <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Stack</div>
      {stack.length === 0 && (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">Stack is empty</div>
      )}
      {stack.map((item, index) => (
        <div key={`${item.kind}-${index}`} className="text-xs text-[color:var(--theme-text-secondary)]">
          {item.kind} · controller {item.controller_id ?? 'N/A'}
        </div>
      ))}
    </Card>
  );
}
