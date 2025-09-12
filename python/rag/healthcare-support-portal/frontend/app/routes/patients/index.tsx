import { useState, useEffect } from 'react';
import { Link, useLoaderData } from 'react-router';
import { Plus, Search, Filter, Users, Calendar, Phone, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate, getDepartmentColor } from '@/lib/utils';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { patientCreateSchema } from '@/lib/schemas';
import type { Patient, User } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

interface PatientsData {
  user: User;
  patients: Patient[];
}

// Loader function - fetch patients data
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const user = await requireAuth(request);
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load patients
    const patients = await serverApi.getPatients(token);

    return {
      user,
      patients
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle patient creation
export async function action({ request }: ActionFunctionArgs) {
  const user = await requireAuth(request);
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, patientCreateSchema, async (data) => {
    // Add user context to patient data
    const patientData = {
      ...data,
      department: data.department || user.department, // Use user's department as default
    };
    
    await serverApi.createPatient(patientData, token);
    // No need to return anything - handleFormSubmission will handle success
  });
}

export default function PatientsIndex() {
  const { user, patients } = useLoaderData<PatientsData>();
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>(patients);
  const [searchTerm, setSearchTerm] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('all');

  useEffect(() => {
    filterPatients();
  }, [patients, searchTerm, departmentFilter]);

  const filterPatients = () => {
    let filtered = patients;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(patient =>
        patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        patient.medical_record_number.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Department filter
    if (departmentFilter !== 'all') {
      filtered = filtered.filter(patient => patient.department === departmentFilter);
    }

    setFilteredPatients(filtered);
  };

  const departments = Array.from(new Set(patients.map(p => p.department))).sort();


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Patients
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage patient records and assignments
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <Button asChild variant="healthcare">
            <Link to="/patients/new">
              <Plus className="mr-2 h-4 w-4" />
              Add Patient
            </Link>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="Search patients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
              className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="all">All Departments</option>
              {departments.map(dept => (
                <option key={dept} value={dept} className="capitalize">
                  {dept}
                </option>
              ))}
            </select>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Users className="h-4 w-4" />
              <span>{filteredPatients.length} patients</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Patients Grid */}
      {filteredPatients.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No patients found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {patients.length === 0 
                ? "Get started by adding your first patient."
                : "Try adjusting your search or filter criteria."
              }
            </p>
            {patients.length === 0 && (
              <div className="mt-6">
                <Button asChild variant="healthcare">
                  <Link to="/patients/new">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Patient
                  </Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredPatients.map((patient) => (
            <Card key={patient.id} className={`patient-card ${getDepartmentColor(patient.department)}`}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <Users className="h-5 w-5 text-gray-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{patient.name}</CardTitle>
                      <CardDescription>
                        MRN: {patient.medical_record_number}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge variant={patient.is_active ? 'active' : 'inactive'}>
                    {patient.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <Calendar className="mr-2 h-4 w-4" />
                    {patient.date_of_birth 
                      ? `DOB: ${formatDate(patient.date_of_birth)}`
                      : 'DOB: Not specified'
                    }
                  </div>
                  <div className="flex items-center text-gray-600 capitalize">
                    <Filter className="mr-2 h-4 w-4" />
                    Department: {patient.department}
                  </div>
                  {patient.assigned_doctor && (
                    <div className="flex items-center text-gray-600">
                      <Users className="mr-2 h-4 w-4" />
                      Dr. {patient.assigned_doctor.username}
                    </div>
                  )}
                </div>
                <div className="mt-4 flex space-x-2">
                  <Button asChild variant="outline" size="sm" className="flex-1">
                    <Link to={`/patients/${patient.id}`}>
                      View Details
                    </Link>
                  </Button>
                  <Button asChild variant="ghost" size="sm">
                    <Link to={`/patients/${patient.id}/edit`}>
                      Edit
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {patients.filter(p => p.is_active).length}
              </div>
              <div className="text-sm text-gray-500">Active Patients</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {patients.filter(p => p.assigned_doctor_id === user?.id).length}
              </div>
              <div className="text-sm text-gray-500">My Patients</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {patients.filter(p => p.department === user?.department).length}
              </div>
              <div className="text-sm text-gray-500">Department</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {departments.length}
              </div>
              <div className="text-sm text-gray-500">Departments</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}