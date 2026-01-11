// frontend/app/api/cards/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = searchParams.get('page') || '1';
    const page_size = searchParams.get('page_size') || '20';
    const colors = searchParams.get('colors');
    const type = searchParams.get('type');
    const set_code = searchParams.get('set_code');
    
    // Build URL with filter parameters
    const urlParams = new URLSearchParams();
    urlParams.set('page', page);
    urlParams.set('page_size', page_size);
    if (colors) urlParams.set('colors', colors);
    if (type) urlParams.set('type', type);
    if (set_code) urlParams.set('set_code', set_code);
    
    const url = `${API_URL}/api/cards?${urlParams.toString()}`;
    
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
      { detail: error instanceof Error ? error.message : 'Failed to list cards', cards: [], total: 0, page: 1, page_size: 20, has_more: false },
      { status: 500 }
    );
  }
}

