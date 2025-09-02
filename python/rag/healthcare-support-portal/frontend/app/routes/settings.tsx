import { useLoaderData } from 'react-router';
import { 
  Settings as SettingsIcon, 
  Users, 
  Shield, 
  Database, 
  Bell,
  Key,
  Globe,
  Palette,
  Activity,
  UserCheck,
  ShieldCheck,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { serverApi } from '@/lib/api.server';
import type { User } from '@/lib/types';
import type { LoaderFunctionArgs } from 'react-router';

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalPatients: number;
  totalDocuments: number;
  systemUptime: string;
}

interface SettingsData {
  user: User;
  stats: SystemStats;
  departments: string[];
  roles: string[];
}

// Loader function - require admin authentication
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication and admin role
    const user = await requireAuth(request);
    
    // Check if user is admin
    if (user.role !== 'admin') {
      throw new Response('Access denied. Admin privileges required.', { status: 403 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load system data in parallel
    const [patients, documents] = await Promise.all([
      serverApi.getPatients(token).catch(() => []),
      serverApi.getDocuments(token).catch(() => [])
    ]);

    // Mock system stats (in a real app, these would come from dedicated admin endpoints)
    const stats: SystemStats = {
      totalUsers: 25, // Mock - would come from user service
      activeUsers: 18, // Mock - would come from user service  
      totalPatients: patients.length,
      totalDocuments: documents.length,
      systemUptime: '7 days, 14 hours' // Mock - would come from system monitoring
    };

    // System configuration options
    const departments = ['cardiology', 'neurology', 'pediatrics', 'oncology', 'emergency', 'endocrinology', 'general'];
    const roles = ['doctor', 'nurse', 'admin'];

    return {
      user,
      stats,
      departments,
      roles
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

function getUserDisplayName(user: User | null): string {
  if (!user) return 'Unknown User';
  return user.username || 'Unknown User';
}

export default function Settings() {
  const { user, stats, departments, roles } = useLoaderData<SettingsData>();

  const settingsSections = [
    {
      id: 'users',
      title: 'User Management',
      description: 'Manage user accounts, roles, and permissions',
      icon: Users,
      color: 'bg-blue-500',
      items: [
        { label: 'Total Users', value: stats.totalUsers },
        { label: 'Active Users', value: stats.activeUsers },
        { label: 'Pending Registrations', value: '3' }
      ]
    },
    {
      id: 'system',
      title: 'System Configuration',
      description: 'Configure departments, roles, and system settings',
      icon: SettingsIcon,
      color: 'bg-green-500',
      items: [
        { label: 'Departments', value: departments.length },
        { label: 'User Roles', value: roles.length },
        { label: 'System Uptime', value: stats.systemUptime }
      ]
    },
    {
      id: 'security',
      title: 'Security & Access',
      description: 'Manage authentication and authorization policies',
      icon: Shield,
      color: 'bg-red-500',
      items: [
        { label: 'Active Sessions', value: '24' },
        { label: 'Failed Login Attempts (24h)', value: '2' },
        { label: 'Password Policy', value: 'Strong' }
      ]
    },
    {
      id: 'data',
      title: 'Data Management',
      description: 'Manage patient data, documents, and backups',
      icon: Database,
      color: 'bg-purple-500',
      items: [
        { label: 'Total Patients', value: stats.totalPatients },
        { label: 'Total Documents', value: stats.totalDocuments },
        { label: 'Last Backup', value: '2 hours ago' }
      ]
    }
  ];

  const systemServices = [
    { name: 'Auth Service', status: 'healthy', port: '8001' },
    { name: 'Patient Service', status: 'healthy', port: '8002' },
    { name: 'RAG Service', status: 'healthy', port: '8003' },
    { name: 'Database', status: 'healthy', port: '5432' },
    { name: 'Oso Dev Server', status: 'healthy', port: '8080' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            System Settings
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage system configuration and administrative settings
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <Badge variant="admin" className="text-sm">
            <ShieldCheck className="mr-1 h-3 w-3" />
            {getUserDisplayName(user)} • Administrator
          </Badge>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {settingsSections.map((section) => (
          <Card key={section.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${section.color} flex items-center justify-center`}>
                  <section.icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <CardTitle>{section.title}</CardTitle>
                  <CardDescription>{section.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {section.items.map((item, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{item.label}</span>
                    <span className="text-sm font-medium text-gray-900">{item.value}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <Button variant="outline" size="sm" className="w-full">
                  Configure {section.title}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* System Services Status */}
      <Card>
        <CardHeader>
          <CardTitle>Service Status</CardTitle>
          <CardDescription>
            Current status of healthcare portal microservices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {systemServices.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    {service.status === 'healthy' ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm font-medium text-gray-900">
                      {service.name}
                    </span>
                  </div>
                </div>
                <Badge variant={service.status === 'healthy' ? 'active' : 'inactive'} className="text-xs">
                  :{service.port}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Configuration Options */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Departments Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Departments</CardTitle>
            <CardDescription>
              Available departments in the healthcare system
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {departments.map((dept) => (
                <div key={dept} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm capitalize text-gray-900">{dept}</span>
                  <Badge variant="default" className="text-xs">
                    Active
                  </Badge>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Button variant="outline" size="sm" className="w-full">
                Manage Departments
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Roles Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>User Roles</CardTitle>
            <CardDescription>
              Available user roles and their permissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {roles.map((role) => (
                <div key={role} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center space-x-2">
                    {role === 'doctor' && <UserCheck className="h-4 w-4 text-blue-600" />}
                    {role === 'nurse' && <Activity className="h-4 w-4 text-green-600" />}
                    {role === 'admin' && <ShieldCheck className="h-4 w-4 text-red-600" />}
                    <span className="text-sm capitalize text-gray-900">{role}</span>
                  </div>
                  <Badge variant={role as any} className="text-xs capitalize">
                    {role}
                  </Badge>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Button variant="outline" size="sm" className="w-full">
                Configure Permissions
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common administrative tasks and system operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Button variant="outline" className="justify-start">
              <Users className="mr-2 h-4 w-4" />
              Add User
            </Button>
            <Button variant="outline" className="justify-start">
              <Database className="mr-2 h-4 w-4" />
              Backup Data
            </Button>
            <Button variant="outline" className="justify-start">
              <Bell className="mr-2 h-4 w-4" />
              System Alerts
            </Button>
            <Button variant="outline" className="justify-start">
              <Activity className="mr-2 h-4 w-4" />
              View Logs
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}