'use client';

// frontend/app/(protected)/getting-started/page.tsx

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export default function GettingStartedPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="font-heading text-4xl font-bold text-slate-900 mb-4">
          Getting Started
        </h1>
        <p className="text-slate-600 text-lg">
          Learn how to use MTG Engine to explore and build card abilities
        </p>
      </div>

      <div className="space-y-6">
        <Card variant="elevated">
          <div className="p-6 space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <span className="text-amber-500 font-bold">1</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Search for Cards
                </h3>
                <p className="text-slate-600 mb-4">
                  Use the search page to find Magic: The Gathering cards by name. You can also browse cards or get a random card to explore.
                </p>
                <Link href="/search">
                  <Button variant="outline" size="sm">
                    Go to Search →
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </Card>

        <Card variant="elevated">
          <div className="p-6 space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <span className="text-amber-500 font-bold">2</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  View Card Details
                </h3>
                <p className="text-slate-600 mb-4">
                  Click on any card to see its full details, all printings, and any saved ability graphs. You can share card links with others.
                </p>
                <Link href="/browse">
                  <Button variant="outline" size="sm">
                    Browse Cards →
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </Card>

        <Card variant="elevated">
          <div className="p-6 space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <span className="text-amber-500 font-bold">3</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Build Abilities
                </h3>
                <p className="text-slate-600 mb-4">
                  Use the Ability Builder to create structured ability graphs for cards. Add triggered abilities, activated abilities, static abilities, and keywords.
                </p>
                <Link href="/builder">
                  <Button variant="outline" size="sm">
                    Open Builder →
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </Card>

        <Card variant="elevated">
          <div className="p-6 space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <span className="text-amber-500 font-bold">4</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Use Templates
                </h3>
                <p className="text-slate-600 mb-4">
                  Browse pre-built ability templates to get started quickly. Templates can be loaded directly into the builder for customization.
                </p>
                <Link href="/templates">
                  <Button variant="outline" size="sm">
                    View Templates →
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <Card variant="bordered" className="mt-8">
        <div className="p-6 text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">
            Ready to start building?
          </h2>
          <p className="text-slate-600 mb-6">
            Choose a card and start creating ability graphs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/builder">
              <Button size="lg">
                Open Builder
              </Button>
            </Link>
            <Link href="/templates">
              <Button variant="outline" size="lg">
                Browse Templates
              </Button>
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
}

