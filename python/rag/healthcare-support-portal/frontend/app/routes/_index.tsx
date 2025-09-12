import { useState, useEffect } from 'react';
import { Link, useLoaderData } from 'react-router';
import { 
  Users, 
  FileText, 
  MessageCircle, 
  Activity,
  Plus,
  Eye,
  TrendingUp,
  Calendar,
  Bell,
  Search
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDateTime, formatDate } from '@/lib/utils';
import { getCurrentUser, handleApiError } from '@/lib/utils/loader-utils';
import { serverApi } from '@/lib/api.server';
import type { User, Patient, Document } from '@/lib/types';
import type { LoaderFunctionArgs } from 'react-router';

interface DashboardData {
  user: User;
  patients: Patient[];
  documents: Document[];
  recentDocuments: Document[];
  myPatients: Patient[];
  departmentStats: {
    totalPatients: number;
    totalDocuments: number;
    activePatients: number;
    sensitiveDocuments: number;
  };
}

// Loader function - fetch dashboard data
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Get current user - layout already ensures authentication
    const user = await getCurrentUser(request);
    if (!user) {
      console.error('[Dashboard] No user found in loader - layout auth may have failed');
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      console.error('[Dashboard] No auth token found');
      throw new Response('Authentication required', { status: 401 });
    }
    
    console.log(`[Dashboard] Loading dashboard for ${user.username}`);
    
    // Load data concurrently based on user role
    const [patients, documents] = await Promise.all([
      serverApi.getPatients(token).catch(error => {
        console.error('[Dashboard] Failed to load patients:', error);
        return [];
      }),
      serverApi.getDocuments(token).catch(error => {
        console.error('[Dashboard] Failed to load documents:', error);
        return [];
      })
    ]);

    // Process data for dashboard
    const myPatients = user.role === 'doctor' 
      ? patients.filter(p => p.assigned_doctor_id === user.id)
      : patients.filter(p => p.department === user.department);
    
    const recentDocuments = documents
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);

    const departmentStats = {
      totalPatients: patients.length,
      totalDocuments: documents.length,
      activePatients: patients.filter(p => p.is_active).length,
      sensitiveDocuments: documents.filter(d => d.is_sensitive).length,
    };

    console.log(`[Dashboard] Loaded ${patients.length} patients, ${documents.length} documents`);

    return {
      user,
      patients,
      documents,
      recentDocuments,
      myPatients,
      departmentStats
    };
  } catch (error) {
    console.error('[Dashboard] Loader error:', error);
    throw handleApiError(error);
  }
}

export default function Dashboard() {
  const { user, patients, documents, recentDocuments, myPatients, departmentStats } = useLoaderData<DashboardData>();
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update current time every minute
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getRoleTitle = (role: string) => {
    switch (role) {
      case 'doctor': return 'Dr.';
      case 'nurse': return 'Nurse';
      case 'admin': return 'Administrator';
      default: return '';
    }
  };

  const getDocumentIcon = (type: string) => {
    switch (type) {
      case 'protocol': return '📋';
      case 'policy': return '📜';
      case 'guideline': return '📖';
      case 'research': return '🔬';
      case 'report': return '📊';
      case 'medical_record': return '📝';
      default: return '📄';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            {getGreeting()}, {getRoleTitle(user.role)} {user.username}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {formatDateTime(currentTime.toISOString())} • {user.department} Department
          </p>
        </div>
        <div className="mt-4 flex space-x-2 md:ml-4 md:mt-0">
          <Button asChild variant="outline">
            <Link to="/chat">
              <MessageCircle className="mr-2 h-4 w-4" />
              AI Assistant
            </Link>
          </Button>
          <Button asChild variant="healthcare">
            <Link to="/documents/new">
              <Plus className="mr-2 h-4 w-4" />
              New Document
            </Link>
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">
                  {user.role === 'doctor' ? 'My Patients' : 'Department Patients'}
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {user.role === 'doctor' ? myPatients.length : departmentStats.activePatients}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <FileText className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Documents</p>
                <p className="text-2xl font-bold text-gray-900">
                  {departmentStats.totalDocuments}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Active Cases</p>
                <p className="text-2xl font-bold text-gray-900">
                  {departmentStats.activePatients}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <Bell className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Sensitive Docs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {departmentStats.sensitiveDocuments}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Recent Documents
            </CardTitle>
            <CardDescription>
              Latest documents in your department
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recentDocuments.length === 0 ? (
              <div className="text-center py-6">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No documents yet</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by creating your first document.</p>
                <div className="mt-6">
                  <Button asChild variant="healthcare">
                    <Link to="/documents/new">
                      <Plus className="mr-2 h-4 w-4" />
                      Create Document
                    </Link>
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {recentDocuments.map((doc) => (
                  <div key={doc.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
                    <div className="text-2xl">
                      {getDocumentIcon(doc.document_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {doc.title}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant="outline" className="text-xs capitalize">
                          {doc.document_type.replace('_', ' ')}
                        </Badge>
                        {doc.is_sensitive && (
                          <Badge variant="destructive" className="text-xs">
                            Sensitive
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-gray-500">
                        {formatDate(doc.created_at)}
                      </p>
                    </div>
                    <Button asChild variant="ghost" size="sm">
                      <Link to={`/documents/${doc.id}`}>
                        <Eye className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                ))}
                <div className="pt-3 border-t">
                  <Button asChild variant="outline" className="w-full">
                    <Link to="/documents">
                      View All Documents
                    </Link>
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* My Patients or Department Patients */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="mr-2 h-5 w-5" />
              {user.role === 'doctor' ? 'My Patients' : 'Department Patients'}
            </CardTitle>
            <CardDescription>
              {user.role === 'doctor' 
                ? 'Patients assigned to you'
                : `Patients in ${user.department} department`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {myPatients.length === 0 ? (
              <div className="text-center py-6">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No patients yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {user.role === 'doctor' 
                    ? 'No patients are currently assigned to you.'
                    : 'No patients in your department yet.'
                  }
                </p>
                {['doctor', 'admin'].includes(user.role) && (
                  <div className="mt-6">
                    <Button asChild variant="healthcare">
                      <Link to="/patients/new">
                        <Plus className="mr-2 h-4 w-4" />
                        Add Patient
                      </Link>
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {myPatients.slice(0, 5).map((patient) => (
                  <div key={patient.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
                    <div className="p-2 bg-blue-100 rounded-full">
                      <Users className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {patient.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {patient.medical_record_number}
                      </p>
                      {patient.date_of_birth && (
                        <p className="text-xs text-gray-500">
                          DOB: {formatDate(patient.date_of_birth)}
                        </p>
                      )}
                    </div>
                    <Button asChild variant="ghost" size="sm">
                      <Link to={`/patients/${patient.id}`}>
                        <Eye className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                ))}
                <div className="pt-3 border-t">
                  <Button asChild variant="outline" className="w-full">
                    <Link to="/patients">
                      View All Patients
                    </Link>
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="mr-2 h-5 w-5" />
            Quick Actions
          </CardTitle>
          <CardDescription>
            Common tasks for healthcare professionals
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Button asChild variant="outline" className="h-20 flex-col space-y-2">
              <Link to="/chat">
                <MessageCircle className="h-6 w-6" />
                <span className="text-sm">AI Chat</span>
              </Link>
            </Button>
            
            <Button asChild variant="outline" className="h-20 flex-col space-y-2">
              <Link to="/documents/new">
                <Plus className="h-6 w-6" />
                <span className="text-sm">New Document</span>
              </Link>
            </Button>

            {['doctor', 'admin'].includes(user.role) && (
              <Button asChild variant="outline" className="h-20 flex-col space-y-2">
                <Link to="/patients/new">
                  <Users className="h-6 w-6" />
                  <span className="text-sm">Add Patient</span>
                </Link>
              </Button>
            )}

            <Button asChild variant="outline" className="h-20 flex-col space-y-2">
              <Link to="/documents">
                <Search className="h-6 w-6" />
                <span className="text-sm">Search Docs</span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}