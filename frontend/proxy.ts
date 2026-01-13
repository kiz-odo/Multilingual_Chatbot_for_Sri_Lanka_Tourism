import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export async function proxy(request: NextRequest) {
  // Only proxy API requests
  if (request.nextUrl.pathname.startsWith('/api/v1/')) {
    const path = request.nextUrl.pathname.replace('/api/v1/', '');
    const backendUrl = `${BACKEND_URL}/api/v1/${path}${request.nextUrl.search}`;

    try {
      // Read and parse the body for methods that have a body
      let body: string | undefined = undefined;
      if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
        try {
          // Clone the request to read the body
          const clonedRequest = request.clone();
          body = await clonedRequest.text();
        } catch (e) {
          console.error('[Proxy] Error reading request body:', e);
        }
      }

      // Build headers - exclude problematic ones
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      // Copy relevant headers from original request
      const authHeader = request.headers.get('authorization');
      if (authHeader) {
        headers['Authorization'] = authHeader;
      }
      
      const acceptHeader = request.headers.get('accept');
      if (acceptHeader) {
        headers['Accept'] = acceptHeader;
      }

      // Forward the request to backend
      const response = await fetch(backendUrl, {
        method: request.method,
        headers,
        body: body || undefined,
      });

      // Return backend response
      const responseData = await response.text();
      
      return new NextResponse(responseData, {
        status: response.status,
        statusText: response.statusText,
        headers: {
          'Content-Type': response.headers.get('Content-Type') || 'application/json',
        },
      });
    } catch (error: any) {
      console.error('[Proxy] Error:', error);
      return NextResponse.json(
        { error: `Failed to connect to backend: ${error.message}` },
        { status: 503 }
      );
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/api/v1/:path*',
}
