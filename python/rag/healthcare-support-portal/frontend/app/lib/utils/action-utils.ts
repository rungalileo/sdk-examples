import { parseWithZod } from '@conform-to/zod';
import { redirect } from 'react-router';
import { json } from './loader-utils';

export async function handleFormSubmission(
  request: Request,
  schema: any,
  handler: (data: any) => Promise<Response>
) {
  try {
    const formData = await request.formData();
    const submission = parseWithZod(formData, { schema });

    if (submission.status !== 'success') {
      return json({
        submission: submission.reply(),
      }, { status: 400 });
    }

    return await handler(submission.value);
  } catch (error) {
    console.error('Form submission error:', error);
    return json({
      submission: {
        formErrors: ['An unexpected error occurred. Please try again.'],
      },
    }, { status: 500 });
  }
}

export function setAuthCookies(response: Response, token: string, user: any): Response {
  // Set HTTP-only cookies for authentication
  const headers = new Headers(response.headers);
  
  // Set auth token cookie
  headers.append('Set-Cookie', `authToken=${token}; HttpOnly; Path=/; SameSite=Strict; Max-Age=1800`);
  
  // Set user info cookie (for client-side access)
  headers.append('Set-Cookie', `userInfo=${JSON.stringify(user)}; Path=/; SameSite=Strict; Max-Age=1800`);
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export function clearAuthCookies(): Response {
  const headers = new Headers();
  
  // Clear auth cookies
  headers.append('Set-Cookie', 'authToken=; HttpOnly; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT');
  headers.append('Set-Cookie', 'userInfo=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT');
  
  return new Response(null, {
    status: 302,
    headers: {
      ...Object.fromEntries(headers.entries()),
      Location: '/login',
    },
  });
}