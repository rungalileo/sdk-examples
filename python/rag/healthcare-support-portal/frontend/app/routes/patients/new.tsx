import { useLoaderData, redirect } from 'react-router';
import { PatientForm } from '@/components/patients/PatientForm';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { patientCreateSchema } from '@/lib/schemas';
import type { User } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

interface NewPatientData {
  currentUser: User;
  doctors: User[];
}

// Loader function - get current user and available doctors
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const currentUser = await requireAuth(request);
    
    // Check if user has permission to create patients (doctors and admins only)
    if (!['doctor', 'admin'].includes(currentUser.role)) {
      throw new Response('Access denied. Only doctors and administrators can create patients.', { status: 403 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load all users to get doctors for assignment
    const users = await serverApi.getUsers(token);
    const doctors = users.filter(user => user.role === 'doctor' && user.is_active);
    
    return {
      currentUser,
      doctors
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle patient creation
export async function action({ request }: ActionFunctionArgs) {
  const currentUser = await requireAuth(request);
  
  // Check if user has permission to create patients
  if (!['doctor', 'admin'].includes(currentUser.role)) {
    throw new Response('Access denied. Only doctors and administrators can create patients.', { status: 403 });
  }
  
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, patientCreateSchema, async (data) => {
    // Add user context to patient data
    const patientData = {
      ...data,
      department: data.department || currentUser.department, // Use user's department as default
    };
    
    await serverApi.createPatient(patientData, token);
    // Redirect to patients list on success
    return redirect('/patients');
  });
}

export default function NewPatient() {
  const { currentUser, doctors } = useLoaderData<NewPatientData>();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Add New Patient
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Create a new patient record for the Healthcare Support Portal
          </p>
        </div>
      </div>

      {/* Patient Form */}
      <PatientForm isEdit={false} doctors={doctors} />
    </div>
  );
}