import { redirect } from 'react-router';
import { serverApi } from '@/lib/api.server';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  department: string;
  is_active: boolean;
  created_at: string;
}

export async function getCurrentUser(request: Request): Promise<User | null> {
  try {
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      return null;
    }

    // Verify token by calling auth service
    const user = await serverApi.getCurrentUser(token);
    return user;
  } catch (error) {
    console.error('Failed to get current user:', error);
    return null;
  }
}

export function json(data: any, init?: ResponseInit) {
  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    ...init,
  });
}

export function getAuthToken(request: Request): string | null {
  const cookieHeader = request.headers.get('Cookie');
  return cookieHeader?.match(/authToken=([^;]+)/)?.[1] || null;
}