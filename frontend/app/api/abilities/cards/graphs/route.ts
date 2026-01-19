import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${API_URL}/api/abilities/cards/graphs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: request.headers.get('cookie') || '',
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
    console.error('Error fetching card ability graphs:', error);
    return NextResponse.json(
      { detail: 'Failed to fetch ability graphs' },
      { status: 500 }
    );
  }
}
