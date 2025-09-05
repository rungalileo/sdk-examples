import { useLoaderData } from 'react-router';
import { UserForm } from '@/components/users/UserForm';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { z } from 'zod';
import type { User } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

const createUserSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  role: z.enum(['doctor', 'nurse', 'admin']),
  department: z.enum(['cardiology', 'neurology', 'pediatrics', 'oncology', 'emergency', 'endocrinology', 'general']),
});

interface NewUserData {
  currentUser: User;
}

// Loader function - ensure admin access
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication and admin role
    const currentUser = await requireAuth(request);
    
    // Check if user is admin
    if (currentUser.role !== 'admin') {
      throw new Response('Access denied. Admin privileges required.', { status: 403 });
    }
    
    return {
      currentUser
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle user creation
export async function action({ request }: ActionFunctionArgs) {
  const currentUser = await requireAuth(request);
  
  // Check if user is admin
  if (currentUser.role !== 'admin') {
    throw new Response('Access denied. Admin privileges required.', { status: 403 });
  }
  
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, createUserSchema, async (data) => {
    await serverApi.createUser(data, token);
    // Redirect will be handled by handleFormSubmission
  });
}

export default function NewUser() {
  const { currentUser } = useLoaderData<NewUserData>();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Add New User
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Create a new user account for the Healthcare Support Portal
          </p>
        </div>
      </div>

      {/* User Form */}
      <UserForm isEdit={false} />
    </div>
  );
}