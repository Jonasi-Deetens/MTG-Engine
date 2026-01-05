// frontend/app/api/cards/search/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const q = searchParams.get('q') || '';
    const page = searchParams.get('page') || '1';
    const page_size = searchParams.get('page_size') || '20';
    
    const url = `${API_URL}/api/cards/search?q=${encodeURIComponent(q)}&page=${page}&page_size=${page_size}`;
    
    const response = await fetch(url, {
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
      { detail: error instanceof Error ? error.message : 'Search failed', cards: [], total: 0, page: 1, page_size: 20, has_more: false },
      { status: 500 }
    );
  }
}

