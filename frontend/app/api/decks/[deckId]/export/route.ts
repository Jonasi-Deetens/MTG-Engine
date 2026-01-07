// frontend/app/api/decks/[deckId]/export/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ deckId: string }> }
) {
  try {
    const { deckId } = await params;
    const searchParams = request.nextUrl.searchParams;
    const format = searchParams.get('format') || 'text';
    
    const response = await fetch(`${API_URL}/api/decks/${deckId}/export?format=${format}`, {
      method: 'GET',
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
      { detail: error instanceof Error ? error.message : 'Failed to export deck' },
      { status: 500 }
    );
  }
}

