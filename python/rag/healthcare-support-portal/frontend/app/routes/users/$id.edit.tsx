import { useLoaderData, redirect } from 'react-router';
import { UserForm } from '@/components/users/UserForm';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { z } from 'zod';
import type { User } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

const updateUserSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().optional(),
  role: z.enum(['doctor', 'nurse', 'admin']),
  department: z.enum(['cardiology', 'neurology', 'pediatrics', 'oncology', 'emergency', 'endocrinology', 'obgyn', 'general']),
});

interface EditUserData {
  currentUser: User;
  user: User;
}

// Loader function - load user to edit
export async function loader({ request, params }: LoaderFunctionArgs) {
  try {
    // Require authentication and admin role
    const currentUser = await requireAuth(request);
    
    // Check if user is admin
    if (currentUser.role !== 'admin') {
      throw new Response('Access denied. Admin privileges required.', { status: 403 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load the user to edit
    const userId = params.id as string;
    const user = await serverApi.getUser(userId, token);
    
    return {
      currentUser,
      user
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle user update
export async function action({ request, params }: ActionFunctionArgs) {
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

  const userId = parseInt(params.id as string);

  return handleFormSubmission(request, updateUserSchema, async (data) => {
    // Don't send empty password
    const updateData = { ...data };
    if (!updateData.password) {
      delete updateData.password;
    }
    
    await serverApi.updateUser(userId, updateData, token);
    return redirect('/users');
  });
}

export default function EditUser() {
  const { currentUser, user } = useLoaderData<EditUserData>();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Edit User: {user.username}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Update user account information and permissions
          </p>
        </div>
      </div>

      {/* User Form */}
      <UserForm user={user} isEdit={true} />
    </div>
  );
}