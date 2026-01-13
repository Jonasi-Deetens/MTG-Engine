// frontend/lib/api/proxy.ts

import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';

interface ProxyOptions {
  method?: string;
  body?: any;
  params?: Record<string, string>;
  errorMessage?: string;
  includeCookie?: boolean;
}

export async function proxyApiRequest(
  request: NextRequest,
  path: string,
  options: ProxyOptions = {}
): Promise<NextResponse> {
  const { method = 'GET', body, errorMessage = 'Internal server error', includeCookie = true } = options;

  const url = `${API_URL}${path}`;
  const headers = new Headers({
    'Content-Type': 'application/json',
  });

  if (includeCookie) {
    const cookie = request.headers.get('cookie');
    if (cookie) {
      headers.set('Cookie', cookie);
    }
  }

  try {
    const fetchOptions: RequestInit = {
      method,
      headers,
      credentials: 'include',
    };

    if (body) {
      fetchOptions.body = JSON.stringify(body);
    }

    const response = await fetch(url, fetchOptions);
    const data = await response.json().catch(() => ({ detail: response.statusText }));

    const responseHeaders = new Headers(response.headers);
    // Forward Set-Cookie header if present
    const setCookieHeader = response.headers.get('set-cookie');
    if (setCookieHeader) {
      responseHeaders.set('set-cookie', setCookieHeader);
    }

    return NextResponse.json(data, { status: response.status, headers: responseHeaders });
  } catch (error) {
    console.error(`Proxy API request to ${path} failed:`, error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : errorMessage },
      { status: 500 }
    );
  }
}

