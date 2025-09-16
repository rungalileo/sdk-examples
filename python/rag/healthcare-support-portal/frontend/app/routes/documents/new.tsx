import { useLoaderData, redirect } from 'react-router';
import { DocumentForm } from '@/components/documents/DocumentForm';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { documentCreateSchema } from '@/lib/schemas';
import type { User, Patient } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

interface NewDocumentData {
  currentUser: User;
  patients: Patient[];
}

// Loader function - get current user and available patients
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const currentUser = await requireAuth(request);
    
    // Check if user has permission to create documents (doctors, nurses, and admins)
    if (!['doctor', 'nurse', 'admin'].includes(currentUser.role)) {
      throw new Response('Access denied. Only doctors, nurses, and administrators can create documents.', { status: 403 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Get URL search params for pre-filling form
    const url = new URL(request.url);
    const patientId = url.searchParams.get('patient_id');
    const documentType = url.searchParams.get('document_type');
    
    // Load all patients for association (filtered by authorization on backend)
    const patients = await serverApi.getPatients(token);
    
    return {
      currentUser,
      patients,
      defaultValues: {
        patientId: patientId ? parseInt(patientId) : null,
        documentType: documentType || null
      }
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle document creation
export async function action({ request }: ActionFunctionArgs) {
  const currentUser = await requireAuth(request);
  
  // Check if user has permission to create documents
  if (!['doctor', 'nurse', 'admin'].includes(currentUser.role)) {
    throw new Response('Access denied. Only doctors, nurses, and administrators can create documents.', { status: 403 });
  }
  
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, documentCreateSchema, async (data) => {
    // Add user context to document data
    const documentData = {
      ...data,
      department: data.department || currentUser.department, // Use user's department as default
    };
    
    await serverApi.createDocument(documentData, token);
    // Redirect to documents list on success
    return redirect('/documents');
  });
}

export default function NewDocument() {
  const { currentUser, patients } = useLoaderData<NewDocumentData>();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Create New Document
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Add a new document to the Healthcare Support Portal with AI-powered features
          </p>
        </div>
      </div>

      {/* Document Form */}
      <DocumentForm isEdit={false} patients={patients} />
    </div>
  );
}