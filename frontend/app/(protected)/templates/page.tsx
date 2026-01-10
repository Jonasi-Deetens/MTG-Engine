'use client';

// frontend/app/(protected)/templates/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { abilities } from '@/lib/abilities';
import { Template } from '@/lib/abilities';
import { useBuilderStore } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Layers } from 'lucide-react';

export default function TemplatesPage() {
  const router = useRouter();
  const { loadFromGraph, clearAll, setCurrentCard } = useBuilderStore();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [usingTemplate, setUsingTemplate] = useState<string | null>(null);

  useEffect(() => {
    const loadTemplates = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await abilities.getTemplates();
        setTemplates(response.templates || []);
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Failed to load templates');
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, []);

  const handleUseTemplate = async (template: Template) => {
    setUsingTemplate(template.id);
    try {
      // Clear current builder state
      clearAll();
      // Load the template graph
      loadFromGraph(template.graph);
      // Navigate to builder
      router.push('/builder');
    } catch (err) {
      console.error('Failed to load template:', err);
      setError('Failed to load template');
    } finally {
      setUsingTemplate(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-angel-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
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
                <div className="pt-4 border-t border-amber-200/50">
                  <Button
                    onClick={() => handleUseTemplate(template)}
                    disabled={usingTemplate === template.id}
                    variant="primary"
                    className="w-full"
                  >
                    {usingTemplate === template.id ? 'Loading...' : 'Use Template'}
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

