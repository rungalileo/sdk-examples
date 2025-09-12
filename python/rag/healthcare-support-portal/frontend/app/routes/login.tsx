import { useState } from 'react';
import { Form, redirect, useNavigation } from 'react-router';
import { Activity, Eye, EyeOff } from 'lucide-react';
import { useForm, getFormProps, getInputProps } from '@conform-to/react';
import { parseWithZod } from '@conform-to/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { loginSchema } from '@/lib/schemas';
import { serverApi } from '@/lib/api.server';
import { handleFormSubmission, setAuthCookies } from '@/lib/utils/action-utils';
import { getCurrentUser, json } from '@/lib/utils/loader-utils';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

// Loader function - check if already authenticated
export async function loader({ request }: LoaderFunctionArgs) {
  const user = await getCurrentUser(request);
  if (user) {
    // Already logged in, redirect to dashboard
    return redirect('/');
  }
  return null;
}

// Action function - handle login form submission
export async function action({ request }: ActionFunctionArgs) {
  return handleFormSubmission(request, loginSchema, async (data) => {
    try {
      console.log('[Login] Attempting login for:', data.username);
      
      // Call auth service to login
      const authResponse = await serverApi.login(data);
      console.log('[Login] Auth response received:', authResponse);
      
      const token = authResponse.access_token;
      if (!token) {
        throw new Error('No access token received from auth service');
      }
      
      // Get user data
      const user = await serverApi.getCurrentUser(token);
      console.log('[Login] User data retrieved:', user);
      
      // Create redirect response with auth cookies
      const response = redirect('/');
      return setAuthCookies(response, token, user);
    } catch (error: any) {
      console.error('[Login] Error during login:', error);
      
      // Return form error
      const submission = parseWithZod(await request.formData(), { schema: loginSchema });
      return json({
        submission: submission.reply({
          formErrors: [
            error.response?.data?.detail || 
            error.message || 
            'Invalid username or password'
          ],
        }),
      }, { status: 400 });
    }
  });
}

interface LoginProps {
  actionData?: {
    submission?: any;
  };
}

export default function Login({ actionData }: LoginProps) {
  const [showPassword, setShowPassword] = useState(false);
  const navigation = useNavigation();
  const isSubmitting = navigation.state === 'submitting';
  
  const [form, fields] = useForm({
    lastResult: actionData?.submission,
    onValidate({ formData }) {
      return parseWithZod(formData, { schema: loginSchema });
    },
    shouldValidate: 'onBlur',
    shouldRevalidate: 'onInput',
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Title */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-healthcare-blue rounded-2xl flex items-center justify-center">
            <Activity className="h-10 w-10 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">
            Healthcare Support Portal
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to your account to continue
          </p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader>
            <CardTitle>Sign In</CardTitle>
            <CardDescription>
              Enter your credentials to access the healthcare portal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form method="post" {...getFormProps(form)} className="space-y-6">
              {form.errors && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                  {form.errors.join(', ')}
                </div>
              )}

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <Input
                  {...getInputProps(fields.username, { type: 'text' })}
                  placeholder="Enter your username"
                  className="w-full"
                />
                {fields.username.errors && (
                  <p className="mt-1 text-sm text-red-600">
                    {fields.username.errors.join(', ')}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <Input
                    {...getInputProps(fields.password, { type: showPassword ? 'text' : 'password' })}
                    placeholder="Enter your password"
                    className="w-full pr-10"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {fields.password.errors && (
                  <p className="mt-1 text-sm text-red-600">
                    {fields.password.errors.join(', ')}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full"
                variant="healthcare"
              >
                {isSubmitting ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Signing in...
                  </div>
                ) : (
                  'Sign In'
                )}
              </Button>
            </Form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">
                    Need access?
                  </span>
                </div>
              </div>

              <div className="mt-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    Contact your system administrator to request access to the Healthcare Support Portal.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Demo Credentials */}
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <h3 className="text-sm font-medium text-blue-900 mb-2">Demo Credentials</h3>
            <div className="text-xs text-blue-700 space-y-1">
              <div><strong>Doctor:</strong> dr_smith / secure_password</div>
              <div><strong>Nurse:</strong> nurse_johnson / secure_password</div>
              <div><strong>Admin:</strong> admin_wilson / secure_password</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}