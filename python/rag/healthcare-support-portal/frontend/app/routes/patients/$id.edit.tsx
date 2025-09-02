import { useLoaderData, redirect } from 'react-router';
import { PatientForm } from '@/components/patients/PatientForm';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { patientUpdateSchema } from '@/lib/schemas';
import type { User, Patient } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

interface EditPatientData {
  currentUser: User;
  patient: Patient;
  doctors: User[];
}

// Loader function - get patient data and available doctors
export async function loader({ request, params }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const currentUser = await requireAuth(request);
    
    // Check if user has permission to edit patients (doctors and admins only)
    if (!['doctor', 'admin'].includes(currentUser.role)) {
      throw new Response('Access denied. Only doctors and administrators can edit patients.', { status: 403 });
    }
    
    // Get patient ID from params
    const patientId = parseInt(params.id as string);
    if (isNaN(patientId)) {
      throw new Response('Invalid patient ID', { status: 400 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load patient data and all users to get doctors for assignment
    const [patient, users] = await Promise.all([
      serverApi.getPatient(patientId, token),
      serverApi.getUsers(token)
    ]);
    
    const doctors = users.filter(user => user.role === 'doctor' && user.is_active);
    
    return {
      currentUser,
      patient,
      doctors
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle patient update
export async function action({ request, params }: ActionFunctionArgs) {
  const currentUser = await requireAuth(request);
  
  // Check if user has permission to edit patients
  if (!['doctor', 'admin'].includes(currentUser.role)) {
    throw new Response('Access denied. Only doctors and administrators can edit patients.', { status: 403 });
  }
  
  // Get patient ID from params
  const patientId = parseInt(params.id as string);
  if (isNaN(patientId)) {
    throw new Response('Invalid patient ID', { status: 400 });
  }
  
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, patientUpdateSchema, async (data) => {
    await serverApi.updatePatient(patientId, data, token);
    // Redirect to patient detail page on success
    return redirect(`/patients/${patientId}`);
  });
}

export default function EditPatient() {
  const { currentUser, patient, doctors } = useLoaderData<EditPatientData>();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Edit Patient: {patient.name}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Update patient information and assignments
          </p>
        </div>
      </div>

      {/* Patient Form */}
      <PatientForm isEdit={true} patient={patient} doctors={doctors} />
    </div>
  );
}