/**
 * API Proxy Route
 * Forwards all /api/* requests to the backend server
 * This bypasses CORS issues during development
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, params.path, 'GET');
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, params.path, 'POST');
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, params.path, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, params.path, 'DELETE');
}

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, params.path, 'PATCH');
}

export async function OPTIONS(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, params.path, 'OPTIONS');
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string
) {
  try {
    const path = pathSegments.join('/');
    
    // Only add trailing slash for GET requests on collection endpoints
    // Don't add for: POST/PUT/PATCH/DELETE, IDs, or paths with extensions
    const lastSegment = pathSegments[pathSegments.length - 1];
    const looksLikeId = /^[a-f0-9]{24}$/i.test(lastSegment);
    const hasExtension = /\.[a-z0-9]+$/i.test(lastSegment);
    const isGetRequest = method === 'GET';
    const shouldAddSlash = isGetRequest && !looksLikeId && !hasExtension && !path.endsWith('/');
    
    const finalPath = shouldAddSlash ? `${path}/` : path;
    const searchParams = request.nextUrl.searchParams.toString();
    const backendUrl = `${BACKEND_URL}/api/v1/${finalPath}${searchParams ? `?${searchParams}` : ''}`;

    console.log(`[API Proxy] ${method} ${path} -> ${backendUrl}`);

    // Get request body if present
    let body: any = undefined;
    let contentType = 'application/json';
    
    if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
      const originalContentType = request.headers.get('content-type') || '';
      console.log('[API Proxy] Original Content-Type:', originalContentType);
      
      try {
        if (originalContentType.includes('application/json')) {
          // Read as JSON first
          const jsonData = await request.json();
          console.log('[API Proxy] Parsed JSON body:', JSON.stringify(jsonData, null, 2));
          console.log('[API Proxy] JSON data type:', typeof jsonData, 'isArray:', Array.isArray(jsonData));
          
          // Ensure it's a valid object
          if (jsonData !== null && jsonData !== undefined) {
            if (typeof jsonData === 'object' && !Array.isArray(jsonData)) {
              body = JSON.stringify(jsonData);
              console.log('[API Proxy] Stringified body:', body);
              console.log('[API Proxy] Body length:', body.length);
              contentType = 'application/json';
            } else {
              console.error('[API Proxy] Invalid JSON data - not an object:', jsonData);
              // Convert to string anyway
              body = JSON.stringify(jsonData);
              contentType = 'application/json';
            }
          } else {
            console.error('[API Proxy] JSON data is null or undefined');
            body = '{}'; // Send empty object
            contentType = 'application/json';
          }
        } else if (originalContentType.includes('multipart/form-data')) {
          body = await request.formData();
          contentType = originalContentType;
        } else {
          body = await request.text();
          contentType = originalContentType || 'text/plain';
        }
      } catch (e: any) {
        console.error('[API Proxy] Body parse error:', e);
        console.error('[API Proxy] Error details:', {
          message: e.message,
          stack: e.stack,
        });
        // Try to read as text as fallback
        try {
          // Note: This won't work if we already read the body above
          // But it's worth trying
          const bodyText = await request.text();
          if (bodyText) {
            body = bodyText;
            contentType = 'application/json';
            console.log('[API Proxy] Fallback: Using text body:', bodyText.substring(0, 100));
          }
        } catch (e2) {
          console.error('[API Proxy] Failed to read body as text:', e2);
        }
      }
    }

    // Forward headers (excluding host and connection headers)
    const headers: Record<string, string> = {};
    request.headers.forEach((value, key) => {
      const lowerKey = key.toLowerCase();
      if (!['host', 'connection', 'content-length', 'transfer-encoding'].includes(lowerKey)) {
        headers[key] = value;
      }
    });
    
    // Set Content-Type if body exists - ensure it's set correctly
    if (body !== undefined && method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
      headers['content-type'] = contentType;
    }

    // Make request to backend
    const fetchOptions: RequestInit = {
      method,
      headers,
      redirect: 'manual',
    };

    if (body !== undefined) {
      fetchOptions.body = body;
      console.log('[API Proxy] Sending body to backend:', {
        hasBody: true,
        bodyType: typeof body,
        bodyLength: typeof body === 'string' ? body.length : 'N/A',
        contentType: headers['Content-Type'],
        bodyPreview: typeof body === 'string' ? body.substring(0, 200) : body,
      });
    } else {
      console.log('[API Proxy] No body to send');
    }

    const response = await fetch(backendUrl, fetchOptions);

    // Get response body
    const responseBody = await response.text();

    console.log(`[API Proxy] Response ${response.status} for ${method} ${path}`);

    // Create response with backend status and headers
    const nextResponse = new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'Content-Type': response.headers.get('content-type') || 'application/json',
      },
    });

    // Copy response headers
    response.headers.forEach((value, key) => {
      const lowerKey = key.toLowerCase();
      if (!['connection', 'transfer-encoding', 'content-encoding'].includes(lowerKey)) {
        nextResponse.headers.set(key, value);
      }
    });

    return nextResponse;
  } catch (error: any) {
    console.error('[API Proxy] Error:', {
      message: error.message,
      stack: error.stack,
      cause: error.cause,
    });
    return NextResponse.json(
      {
        success: false,
        error: {
          code: 'PROXY_ERROR',
          message: `Failed to connect to backend at ${BACKEND_URL}: ${error.message}`,
          details: error.cause?.message || error.stack?.split('\n')[0],
        },
      },
      { status: 503 }
    );
  }
}
