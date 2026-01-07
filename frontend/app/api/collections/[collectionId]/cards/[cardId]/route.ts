// frontend/app/api/collections/[collectionId]/cards/[cardId]/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ collectionId: string; cardId: string }> }
) {
  try {
    const { collectionId, cardId } = await params;
    const response = await fetch(`${API_URL}/api/collections/${collectionId}/cards/${encodeURIComponent(cardId)}`, {
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
      { detail: error instanceof Error ? error.message : 'Failed to remove card from collection' },
      { status: 500 }
    );
  }
}

