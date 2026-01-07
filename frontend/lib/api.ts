// frontend/lib/api.ts

// Use relative URLs to proxy through Next.js API routes
// This avoids CORS issues and allows Next.js server to reach API container
const API_URL = typeof window === 'undefined' 
  ? (process.env.NEXT_PUBLIC_API_URL || 'http://api:8000') // Server-side: use service name
  : ''; // Client-side: use relative URLs (proxied through Next.js)

export interface ApiError {
  detail: string;
}

export class ApiClientError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: ApiError
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ApiError | null = null;
    try {
      errorData = await response.json();
    } catch {
      // If response is not JSON, use status text
    }
    
    throw new ApiClientError(
      errorData?.detail || response.statusText || 'An error occurred',
      response.status,
      errorData || undefined
    );
  }
  
  // Handle empty responses
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T;
  }
  
  return response.json();
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Important for cookies
  };
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, 10000);

    const response = await fetch(url, {
      ...config,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return handleResponse<T>(response);
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    if (error instanceof Error && (error.name === 'AbortError' || error.message.includes('aborted'))) {
      throw new ApiClientError(
        `Request timeout: API did not respond within 10 seconds.`,
        0
      );
    }
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiClientError(
        `Cannot connect to API. Make sure the server is running.`,
        0
      );
    }
    throw new ApiClientError(
      error instanceof Error ? error.message : 'Network error'
    );
  }
}

export const api = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, data?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),
  put: <T>(endpoint: string, data?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),
  delete: <T>(endpoint: string) =>
    apiRequest<T>(endpoint, { method: 'DELETE' }),
};

// Card API methods
export const cards = {
  // Get random card
  getRandom: async (): Promise<any> => {
    return api.get('/api/cards/random');
  },
  // Search cards by name
  search: async (query: string, page: number = 1, pageSize: number = 20): Promise<any> => {
    return api.get(`/api/cards/search?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`);
  },
  // Get all versions of a card
  getVersions: async (cardId: string): Promise<any[]> => {
    return api.get(`/api/cards/versions/${cardId}`);
  },
};

