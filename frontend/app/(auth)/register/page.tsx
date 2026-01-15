'use client';

// frontend/app/(auth)/register/page.tsx

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register } from '@/lib/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      await register({ username, email, password });
      router.push('/login?registered=true');
    } catch (err: any) {
      const errorMessage = err?.data?.detail || err?.message || 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[color:var(--theme-bg-primary)] px-4">
      <div className="w-full max-w-md">
        <Card variant="elevated" className="p-8">
          <div className="text-center mb-8">
            <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
              Create Account
            </h1>
            <p className="text-[color:var(--theme-text-secondary)]">
              Sign up to access the MTG Engine
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)] text-sm">
                {error}
              </div>
            )}

            <Input
              label="Username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              placeholder="Choose a username"
            />

            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              placeholder="Enter your email"
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
              placeholder="Create a password"
            />

            <Input
              label="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
              placeholder="Confirm your password"
            />

            <Button
              type="submit"
              className="w-full"
              isLoading={isLoading}
              disabled={!username || !email || !password || !confirmPassword}
            >
              Register
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-[color:var(--theme-text-secondary)]">
            <p>
              Already have an account?{' '}
              <Link href="/login" className="text-[color:var(--theme-accent-primary)] hover:text-[color:var(--theme-accent-hover)] underline">
                Sign in here
              </Link>
            </p>
          </div>

          <div className="mt-4 text-center">
            <Link href="/" className="text-sm text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-accent-primary)]">
              ← Back to home
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}

