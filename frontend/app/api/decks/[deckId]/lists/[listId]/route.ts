// frontend/app/api/decks/[deckId]/lists/[listId]/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ deckId: string; listId: string }> }
) {
  try {
    const { deckId, listId } = await params;
    const body = await request.json();
    const response = await fetch(`${API_URL}/api/decks/${deckId}/lists/${listId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to update custom list' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ deckId: string; listId: string }> }
) {
  try {
    const { deckId, listId } = await params;
    const response = await fetch(`${API_URL}/api/decks/${deckId}/lists/${listId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
      credentials: 'include',
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to delete custom list' },
      { status: 500 }
    );
  }
}

