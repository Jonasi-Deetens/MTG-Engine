'use client';

// frontend/app/(protected)/templates/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingState } from '@/components/ui/LoadingState';
import { Layers } from 'lucide-react';

export default function TemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [usingTemplate, setUsingTemplate] = useState<string | null>(null);

  useEffect(() => {
    setLoading(false);
    setTemplates([]);
  }, []);

  const handleUseTemplate = async (_template: any) => {
    setUsingTemplate(template.id);
    setError('Legacy templates are not supported in the unified effect builder yet.');
    setUsingTemplate(null);
  };

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1
          className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2 nier-glitch"
          data-text="Ability Templates"
        >
          Ability Templates
        </h1>
        <p className="text-[color:var(--theme-text-secondary)]">
          Browse and use pre-built ability templates to get started quickly
        </p>
      </div>

      {error && (
        <div className="p-4 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)]">
          {error}
        </div>
      )}

      {templates.length === 0 && !loading ? (
        <Card variant="elevated">
          <EmptyState
            icon={Layers}
            title="No templates available"
            description="Ability templates will appear here once they are created. Templates help you quickly build common ability patterns."
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <Card key={template.id} variant="elevated">
              <div className="p-6 space-y-4">
                <div>
                  <h3 className="text-xl font-bold text-[color:var(--theme-text-primary)] mb-2">
                    {template.name}
                  </h3>
                  <p className="text-[color:var(--theme-text-secondary)] text-sm">
                    {template.description}
                  </p>
                </div>
                <div className="pt-4 border-t border-[color:var(--theme-border-default)]/50">
                  <Button
                    onClick={() => handleUseTemplate(template)}
                    disabled
                    variant="primary"
                    className="w-full"
                  >
                    Legacy Template (disabled)
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

