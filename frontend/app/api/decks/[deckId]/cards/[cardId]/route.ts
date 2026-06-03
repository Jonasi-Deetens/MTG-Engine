// frontend/app/api/decks/[deckId]/cards/[cardId]/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ deckId: string; cardId: string }> }
) {
  try {
    const { deckId, cardId } = await params;
    const body = await request.json();
    const url = `${API_URL}/api/decks/${deckId}/cards/${encodeURIComponent(cardId)}`;
    console.log(`[API Route] PUT ${url}`);
    
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });

    console.log(`[API Route] Response status: ${response.status}`);
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error(`[API Route] Error:`, error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to update card quantity' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ deckId: string; cardId: string }> }
) {
  try {
    const { deckId, cardId } = await params;
    const url = `${API_URL}/api/decks/${deckId}/cards/${encodeURIComponent(cardId)}`;
    console.log(`[API Route] DELETE ${url}`);
    
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
      credentials: 'include',
    });

    console.log(`[API Route] Response status: ${response.status}`);
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error(`[API Route] Error:`, error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to remove card from deck' },
      { status: 500 }
    );
  }
}

