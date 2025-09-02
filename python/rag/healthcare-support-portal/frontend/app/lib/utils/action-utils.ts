import { redirect } from 'react-router';
import { parseWithZod } from '@conform-to/zod';
import type { z } from 'zod';
import { json } from './loader-utils';

/**
 * Parse form data with Zod schema
 */
export async function parseFormData<T extends z.ZodSchema>(
  request: Request,
  schema: T
) {
  const formData = await request.formData();
  return parseWithZod(formData, { schema });
}

/**
 * Handle form submission with validation
 */
export async function handleFormSubmission<T extends z.ZodSchema>(
  request: Request,
  schema: T,
  onSuccess: (data: z.infer<T>) => Promise<Response | void>
) {
  const submission = await parseFormData(request, schema);
  
  if (submission.status !== 'success') {
    return json({ submission: submission.reply() }, { status: 400 });
  }
  
  try {
    const result = await onSuccess(submission.value);
    return result || redirect('/');
  } catch (error: any) {
    // Handle API errors
    if (error.response?.data?.detail) {
      return json({
        submission: submission.reply({
          formErrors: [error.response.data.detail],
        }),
      }, { status: error.response.status || 400 });
    }
    
    // Generic error
    return json({
      submission: submission.reply({
        formErrors: ['An error occurred. Please try again.'],
      }),
    }, { status: 500 });
  }
}

/**
 * Set auth cookies in response
 */
export function setAuthCookies(response: Response, token: string, user: any): Response {
  const headers = new Headers(response.headers);
  
  try {
    // Set auth token cookie
    headers.append('Set-Cookie', `authToken=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400`);
    
    // Set user data cookie (for client-side access)
    headers.append('Set-Cookie', `user=${encodeURIComponent(JSON.stringify(user))}; Path=/; SameSite=Lax; Max-Age=86400`);
    
    console.log(`[Auth] Set auth cookies for user: ${user.username}`);
  } catch (error) {
    console.error('[Auth] Failed to set auth cookies:', error);
    // Clear any existing cookies if there's an error
    headers.append('Set-Cookie', 'authToken=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0');
    headers.append('Set-Cookie', 'user=; Path=/; SameSite=Lax; Max-Age=0');
  }
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

/**
 * Clear auth cookies
 */
export function clearAuthCookies(): Response {
  const headers = new Headers();
  headers.append('Set-Cookie', 'authToken=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0');
  headers.append('Set-Cookie', 'user=; Path=/; SameSite=Lax; Max-Age=0');
  
  return redirect('/login', { headers });
}

/**
 * Create form error response
 */
export function formError(
  submission: any,
  errors: Record<string, string[]> | string[]
) {
  if (Array.isArray(errors)) {
    return json({
      submission: submission.reply({ formErrors: errors }),
    }, { status: 400 });
  }
  
  return json({
    submission: submission.reply({ fieldErrors: errors }),
  }, { status: 400 });
}

/**
 * Handle API form errors
 */
export function handleApiFormError(error: any, submission: any) {
  if (error.response?.data?.detail) {
    // FastAPI validation errors
    if (Array.isArray(error.response.data.detail)) {
      const fieldErrors: Record<string, string[]> = {};
      
      error.response.data.detail.forEach((err: any) => {
        const field = err.loc?.[err.loc.length - 1] || 'form';
        if (!fieldErrors[field]) {
          fieldErrors[field] = [];
        }
        fieldErrors[field].push(err.msg);
      });
      
      return formError(submission, fieldErrors);
    }
    
    // Single error message
    return formError(submission, [error.response.data.detail]);
  }
  
  // Generic error
  return formError(submission, ['An error occurred. Please try again.']);
}