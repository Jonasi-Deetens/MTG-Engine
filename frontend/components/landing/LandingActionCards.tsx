'use client';

// frontend/components/landing/LandingActionCards.tsx

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { LogIn, UserPlus, Shuffle, Grid3x3 } from 'lucide-react';
import { cards } from '@/lib/api';

export function LandingActionCards() {
  const router = useRouter();

  const handleRandomCard = async () => {
    try {
      const card = await cards.getRandom();
      if (card?.card_id) {
        router.push(`/cards/${card.card_id}`);
      }
    } catch (err) {
      console.error('Failed to get random card:', err);
      // Error is already logged, user can try again
    }
  };

  const actionCards = [
    {
      title: 'Browse Cards',
      description: 'Explore the card database',
      icon: Grid3x3,
      href: '/search',
      onClick: undefined,
    },
    {
      title: 'Login',
      description: 'Sign in to your account',
      icon: LogIn,
      href: '/login',
      onClick: undefined,
    },
    {
      title: 'Register',
      description: 'Create a new account',
      icon: UserPlus,
      href: '/register',
      onClick: undefined,
    },
    {
      title: 'Random Card',
      description: 'Discover a random card',
      icon: Shuffle,
      href: undefined,
      onClick: handleRandomCard,
    },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto px-4 pb-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {actionCards.map((card, index) => {
          const Icon = card.icon;
          const content = (
            <div className="group bg-white/10 backdrop-blur-sm hover:bg-white/20 rounded-lg p-4 transition-all border border-white/20 hover:border-amber-500/50 cursor-pointer">
              <div className="flex flex-col items-center text-center space-y-2">
                <div className="w-10 h-10 bg-amber-500/20 rounded-full flex items-center justify-center group-hover:bg-amber-500/30 transition-colors">
                  <Icon className="w-5 h-5 text-amber-400" />
                </div>
                <h3 className="font-semibold text-white text-sm">{card.title}</h3>
                <p className="text-white/70 text-xs">{card.description}</p>
              </div>
            </div>
          );

          if (card.onClick) {
            return (
              <button key={index} onClick={card.onClick} className="text-left">
                {content}
              </button>
            );
          }

          return (
            <Link key={index} href={card.href!}>
              {content}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

