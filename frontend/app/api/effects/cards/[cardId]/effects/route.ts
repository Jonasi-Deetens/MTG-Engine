import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

async function proxy(request: NextRequest, cardId: string) {
  const response = await fetch(`${API_URL}/api/effects/cards/${cardId}/effects`, {
    method: request.method,
    headers: {
      'Content-Type': 'application/json',
      Cookie: request.headers.get('cookie') || '',
    },
    body: request.method === 'POST' ? await request.text() : undefined,
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    return NextResponse.json(error, { status: response.status });
  }

  const data = await response.json();
  return NextResponse.json(data);
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    return await proxy(request, cardId);
  } catch (error) {
    console.error('Error fetching card effects:', error);
    return NextResponse.json({ detail: 'Failed to fetch card effects' }, { status: 500 });
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    return await proxy(request, cardId);
  } catch (error) {
    console.error('Error saving card effects:', error);
    return NextResponse.json({ detail: 'Failed to save card effects' }, { status: 500 });
  }
}
