// frontend/app/api/decks/[deckId]/cards/[cardId]/list/route.ts

import { NextRequest } from 'next/server';
import { proxyApiRequest } from '@/lib/api/proxy';

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ deckId: string; cardId: string }> }
) {
  const { deckId, cardId } = await params;
  const body = await request.json();
  
  return proxyApiRequest(
    request,
    `/api/decks/${deckId}/cards/${encodeURIComponent(cardId)}/list`,
    {
      method: 'PUT',
      body,
      errorMessage: 'Failed to move card to list',
    }
  );
}

