import { useLoaderData, Link, redirect } from 'react-router';
import { 
  ArrowLeft, 
  Edit, 
  Calendar, 
  User as UserIcon, 
  MapPin, 
  Phone, 
  Mail,
  FileText,
  Activity
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate, formatDateTime, getDepartmentColor } from '@/lib/utils';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { patientUpdateSchema } from '@/lib/schemas';
import type { Patient, User } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

interface PatientData {
  user: User;
  patient: Patient;
}

// Loader function - fetch individual patient data
export async function loader({ request, params }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const user = await requireAuth(request);
    
    const patientId = params.id;
    if (!patientId || isNaN(Number(patientId))) {
      throw new Response('Invalid patient ID', { status: 400 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load patient
    const patient = await serverApi.getPatient(parseInt(patientId), token);

    return {
      user,
      patient
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle patient updates
export async function action({ request, params }: ActionFunctionArgs) {
  const user = await requireAuth(request);
  const patientId = params.id;
  
  if (!patientId || isNaN(Number(patientId))) {
    throw new Response('Invalid patient ID', { status: 400 });
  }
  
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, patientUpdateSchema, async (data) => {
    await serverApi.updatePatient(parseInt(patientId), data, token);
    return redirect(`/patients/${patientId}`);
  });
}

export default function PatientDetail() {
  const { user, patient } = useLoaderData<PatientData>();


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm" asChild>
            <Link to="/patients">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Patients
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold leading-7 text-gray-900">
              {patient.name}
            </h1>
            <p className="text-sm text-gray-500">
              Medical Record Number: {patient.medical_record_number}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={patient.is_active ? 'active' : 'inactive'}>
            {patient.is_active ? 'Active' : 'Inactive'}
          </Badge>
          <Button size="sm" asChild>
            <Link to={`/patients/${patient.id}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit Patient
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Patient Information */}
          <Card className={getDepartmentColor(patient.department)}>
            <CardHeader>
              <CardTitle>Patient Information</CardTitle>
              <CardDescription>
                Basic patient details and demographics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">{patient.name}</dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Medical Record Number</dt>
                  <dd className="mt-1 text-sm text-gray-900">{patient.medical_record_number}</dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Calendar className="mr-2 h-4 w-4 text-gray-400" />
                    {patient.date_of_birth 
                      ? formatDate(patient.date_of_birth)
                      : 'Not specified'
                    }
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Department</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center capitalize">
                    <MapPin className="mr-2 h-4 w-4 text-gray-400" />
                    {patient.department}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1">
                    <Badge variant={patient.is_active ? 'active' : 'inactive'}>
                      {patient.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Created</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {formatDateTime(patient.created_at)}
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {/* Medical History */}
          <Card>
            <CardHeader>
              <CardTitle>Medical History</CardTitle>
              <CardDescription>
                Patient's medical history and records
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-gray-500 py-8">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No medical history available
                </h3>
                <p className="text-sm text-gray-500">
                  Medical history and records will appear here once added.
                </p>
                <Button variant="outline" className="mt-4" asChild>
                  <Link to={`/documents/new?patient_id=${patient.id}`}>
                    Add Medical Record
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Recent updates and changes to this patient record
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                      <UserIcon className="h-4 w-4 text-green-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      Patient record created
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatDateTime(patient.created_at)}
                    </p>
                  </div>
                </div>
                
                {patient.assigned_doctor && (
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                        <UserIcon className="h-4 w-4 text-blue-600" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        Assigned to Dr. {patient.assigned_doctor.username}
                      </p>
                      <p className="text-sm text-gray-500">
                        {patient.assigned_doctor.department} department
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Assigned Doctor */}
          {patient.assigned_doctor && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Assigned Doctor</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-4">
                  <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <UserIcon className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Dr. {patient.assigned_doctor.username}
                    </p>
                    <p className="text-sm text-gray-500 capitalize">
                      {patient.assigned_doctor.department}
                    </p>
                    <Badge variant="doctor" className="mt-1">
                      Doctor
                    </Badge>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <Button variant="outline" size="sm" className="w-full">
                    <Mail className="mr-2 h-4 w-4" />
                    Send Message
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    <Phone className="mr-2 h-4 w-4" />
                    Contact
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                <Link to={`/patients/${patient.id}/edit`}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Patient Info
                </Link>
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                <Link to={`/documents/new?patient_id=${patient.id}&document_type=medical_record`}>
                  <FileText className="mr-2 h-4 w-4" />
                  Add Medical Record
                </Link>
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start" disabled>
                <Calendar className="mr-2 h-4 w-4" />
                Schedule Appointment
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                <Link to="/chat">
                  <Activity className="mr-2 h-4 w-4" />
                  AI Assistant
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Patient Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Patient Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Status</span>
                  <Badge variant={patient.is_active ? 'active' : 'inactive'}>
                    {patient.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Department</span>
                  <span className="text-sm font-medium capitalize">{patient.department}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Records</span>
                  <span className="text-sm font-medium">0</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Last Visit</span>
                  <span className="text-sm font-medium">N/A</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}