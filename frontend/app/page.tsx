// frontend/app/page.tsx

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Decorative background pattern instead of image */}
        <div className="absolute inset-0 bg-gradient-to-br from-amber-900/20 via-slate-800/40 to-slate-900/60"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(212,175,55,0.1),transparent_50%)]"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            <h1 className="font-heading text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6">
              MTG Engine
            </h1>
            <p className="text-xl sm:text-2xl text-slate-300 mb-8 max-w-2xl mx-auto">
              Search and explore Magic: The Gathering cards with powerful filtering and analysis tools
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/login">
                <Button size="lg" className="w-full sm:w-auto">
                  Get Started
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="font-heading text-3xl sm:text-4xl font-bold text-center text-white mb-12">
          Powerful Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card variant="elevated">
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="font-heading text-xl font-semibold text-white mb-2">Advanced Search</h3>
              <p className="text-slate-400">
                Search through thousands of cards with powerful filters and queries
              </p>
            </div>
          </Card>

          <Card variant="elevated">
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="font-heading text-xl font-semibold text-white mb-2">Card Details</h3>
              <p className="text-slate-400">
                View comprehensive card information including abilities, stats, and rulings
              </p>
            </div>
          </Card>

          <Card variant="elevated">
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </div>
              <h3 className="font-heading text-xl font-semibold text-white mb-2">Engine Integration</h3>
              <p className="text-slate-400">
                Powered by advanced MTG rules engine for accurate card parsing
              </p>
            </div>
          </Card>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <Card variant="bordered">
          <h2 className="font-heading text-3xl font-bold text-white mb-4">
            Ready to explore?
          </h2>
          <p className="text-slate-300 mb-6">
            Start searching through Magic: The Gathering cards today
          </p>
          <Link href="/login">
            <Button size="lg">
              Sign In to Get Started
            </Button>
          </Link>
        </Card>
      </div>
    </div>
  );
}
