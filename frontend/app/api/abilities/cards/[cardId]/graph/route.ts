import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    const body = await request.json();
    
    const response = await fetch(`${API_URL}/api/abilities/cards/${cardId}/graph`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error saving card ability graph:', error);
    return NextResponse.json(
      { detail: 'Failed to save ability graph' },
      { status: 500 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    
    const response = await fetch(`${API_URL}/api/abilities/cards/${cardId}/graph`, {
      method: 'GET',
      headers: {
        'Cookie': request.headers.get('cookie') || '',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { detail: 'Ability graph not found' },
          { status: 404 }
        );
      }
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching card ability graph:', error);
    return NextResponse.json(
      { detail: 'Failed to fetch ability graph' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { cardId } = await params;
    
    const response = await fetch(`${API_URL}/api/abilities/cards/${cardId}/graph`, {
      method: 'DELETE',
      headers: {
        'Cookie': request.headers.get('cookie') || '',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error deleting card ability graph:', error);
    return NextResponse.json(
      { detail: 'Failed to delete ability graph' },
      { status: 500 }
    );
  }
}

