// frontend/app/api/auth/logout/route.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

export async function POST(request: NextRequest) {
  try {
    const response = await fetch(`${API_URL}/api/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
    });

    const data = await response.json();
    
    // Clear cookie
    const responseHeaders = new Headers();
    responseHeaders.set('set-cookie', 'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT');
    
    return NextResponse.json(data, { 
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : 'Logout failed' },
      { status: 500 }
    );
  }
}

