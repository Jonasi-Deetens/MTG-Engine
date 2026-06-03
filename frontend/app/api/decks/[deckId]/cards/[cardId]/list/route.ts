// frontend/app/api/decks/[deckId]/cards/[cardId]/list/route.ts

import { NextRequest, NextResponse } from 'next/server';

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ deckId: string; cardId: string }> }
) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';
  try {
    const { deckId, cardId } = await params;
    const body = await request.json();
    console.log('[DEBUG] deck list move proxy', { deckId, cardId, list_id: body?.list_id });

    const response = await fetch(`${API_URL}/api/decks/${deckId}/cards/${encodeURIComponent(cardId)}/list`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });

    const text = await response.text();
    const data = text ? (() => {
      try {
        return JSON.parse(text);
      } catch {
        return { detail: text };
      }
    })() : {};

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('[DEBUG] deck list move proxy failed', error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to move card to list' },
      { status: 500 }
    );
  }
}

