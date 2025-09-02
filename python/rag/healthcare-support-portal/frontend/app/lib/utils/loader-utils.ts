import { redirect } from 'react-router';

/**
 * Get authentication token from request cookies or headers
 */
export function getAuthToken(request: Request): string | null {
  // Check localStorage is not available on server, so we'll use cookies
  const cookieHeader = request.headers.get('Cookie');
  if (!cookieHeader) return null;
  
  const cookies = Object.fromEntries(
    cookieHeader.split('; ').map(c => {
      const [key, value] = c.split('=');
      return [key, decodeURIComponent(value)];
    })
  );
  
  return cookies.authToken || null;
}

/**
 * Get current user from request
 */
export async function getCurrentUser(request: Request) {
  const token = getAuthToken(request);
  if (!token) {
    console.log('[Auth] No auth token found in cookies');
    return null;
  }
  
  try {
    // In a real app, this would validate the token with the auth service
    const userCookie = request.headers.get('Cookie')?.match(/user=([^;]+)/)?.[1];
    if (!userCookie) {
      console.log('[Auth] No user cookie found');
      return null;
    }
    
    const user = JSON.parse(decodeURIComponent(userCookie));
    console.log(`[Auth] User found: ${user.username} (${user.role})`);
    return user;
  } catch (error) {
    console.error('[Auth] Failed to parse user cookie:', error);
    // Clear corrupted cookies by returning null and letting the auth flow handle it
    return null;
  }
}

/**
 * Require authentication for a route
 * Redirects to login if not authenticated
 */
export async function requireAuth(request: Request) {
  const user = await getCurrentUser(request);
  if (!user) {
    throw redirect('/login');
  }
  return user;
}

/**
 * Require specific role for a route
 */
export async function requireRole(request: Request, allowedRoles: string[]) {
  const user = await requireAuth(request);
  if (!allowedRoles.includes(user.role)) {
    throw new Response('Forbidden', { status: 403 });
  }
  return user;
}

/**
 * Create headers with auth token
 */
export function createAuthHeaders(token: string): HeadersInit {
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

/**
 * Handle API errors in loaders
 */
export function handleApiError(error: any) {
  if (error.response?.status === 401) {
    // Unauthorized - redirect to login
    throw redirect('/login');
  }
  
  if (error.response?.status === 403) {
    // Forbidden
    throw new Response('You do not have permission to access this resource', {
      status: 403,
      statusText: 'Forbidden',
    });
  }
  
  if (error.response?.status === 404) {
    // Not found
    throw new Response('Resource not found', {
      status: 404,
      statusText: 'Not Found',
    });
  }
  
  // Generic error
  throw new Response('An error occurred while loading data', {
    status: error.response?.status || 500,
    statusText: error.response?.statusText || 'Internal Server Error',
  });
}

/**
 * Create a JSON response with proper headers
 */
export function json<T>(data: T, init?: ResponseInit): Response {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });
}