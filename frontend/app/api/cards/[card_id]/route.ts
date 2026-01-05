// frontend/app/api/cards/[card_id]/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { card_id: string } }
) {
  try {
    const { card_id } = params;
    
    const response = await fetch(`${API_URL}/api/cards/${encodeURIComponent(card_id)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Failed to get card' },
      { status: 500 }
    );
  }
}

