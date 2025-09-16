import { useState } from 'react';
import { useFetcher } from 'react-router';
import { 
  UserCheck, 
  Activity, 
  ShieldCheck, 
  LogIn,
  Users,
  FileText,
  MessageSquare
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';

interface DemoUser {
  username: string;
  password: string;
  role: string;
  department: string;
  description: string;
  permissions: string[];
  icon: any;
  color: string;
}

const DEMO_USERS: DemoUser[] = [
  {
    username: 'admin_wilson',
    password: 'secure_password',
    role: 'admin',
    department: 'administration',
    description: 'Full system access with administrative privileges',
    permissions: ['All documents', 'All departments', 'User management', 'System settings', 'RAG chat assistant'],
    icon: ShieldCheck,
    color: 'bg-red-500'
  },
  {
    username: 'dr_smith',
    password: 'secure_password', 
    role: 'doctor',
    department: 'cardiology',
    description: 'Cardiology specialist with access to patient records and medical protocols',
    permissions: ['Cardiology documents', 'Patient records', 'Medical protocols', 'RAG chat assistant'],
    icon: UserCheck,
    color: 'bg-blue-500'
  },
  {
    username: 'nurse_johnson',
    password: 'secure_password',
    role: 'nurse', 
    department: 'emergency',
    description: 'Emergency department nurse with access to emergency protocols and procedures',
    permissions: ['Emergency documents', 'Patient care protocols', 'RAG chat assistant'],
    icon: Activity,
    color: 'bg-green-500'
  }
];

function getRoleBadgeVariant(role: string) {
  switch (role) {
    case 'doctor':
      return 'doctor' as const;
    case 'nurse':
      return 'nurse' as const;
    case 'admin':
      return 'admin' as const;
    default:
      return 'default' as const;
  }
}

export default function DemoLogin() {
  const fetcher = useFetcher();
  const [selectedUser, setSelectedUser] = useState<DemoUser | null>(null);

  const handleLogin = (user: DemoUser) => {
    setSelectedUser(user);
    const formData = new FormData();
    formData.append('username', user.username);
    formData.append('password', user.password);
    
    fetcher.submit(formData, { 
      method: 'post', 
      action: '/login'
    });
  };

  const isLoggingIn = fetcher.state === 'submitting';

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 bg-healthcare-blue rounded-2xl flex items-center justify-center">
              <Users className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Healthcare Support Portal
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Choose a demo user role to explore the system. Each role has different permissions 
            and access to various documents and features.
          </p>
        </div>

        {/* Demo Users Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {DEMO_USERS.map((user) => {
            const IconComponent = user.icon;
            const isSelected = selectedUser?.username === user.username;
            const isCurrentUserLoggingIn = isLoggingIn && isSelected;

            return (
              <Card 
                key={user.username}
                className={cn(
                  "transition-all duration-200 cursor-pointer hover:shadow-lg",
                  isSelected ? "ring-2 ring-healthcare-blue" : "hover:ring-1 hover:ring-gray-300"
                )}
                onClick={() => !isLoggingIn && handleLogin(user)}
              >
                <CardHeader className="text-center pb-4">
                  <div className="flex justify-center mb-3">
                    <div className={cn(
                      "h-12 w-12 rounded-full flex items-center justify-center",
                      user.color
                    )}>
                      <IconComponent className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <CardTitle className="text-lg">{user.username}</CardTitle>
                  <CardDescription>{user.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-center">
                    <Badge variant={getRoleBadgeVariant(user.role)} className="text-sm">
                      <span className="flex items-center">
                        <IconComponent className="h-3 w-3 mr-1" />
                        <span className="capitalize">{user.role}</span>
                      </span>
                    </Badge>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-gray-600">
                      <strong>Department:</strong> {user.department}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-900 mb-2">Permissions:</p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {user.permissions.map((permission, idx) => (
                        <li key={idx} className="flex items-center">
                          <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                          {permission}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Button 
                    className="w-full"
                    disabled={isLoggingIn}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLogin(user);
                    }}
                  >
                    {isCurrentUserLoggingIn ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Logging in...
                      </>
                    ) : (
                      <>
                        <LogIn className="h-4 w-4 mr-2" />
                        Login as {user.role}
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Features Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <MessageSquare className="h-5 w-5 mr-2 text-healthcare-blue" />
              RAG Chat Assistant Features
            </CardTitle>
            <CardDescription>
              Test how the AI assistant responds differently based on user permissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">What you can test:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Document access based on user role</li>
                  <li>• Department-specific information retrieval</li>
                  <li>• Permission-based search results</li>
                  <li>• Context-aware responses</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Try asking:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• "What are the emergency protocols?"</li>
                  <li>• "Show me cardiology guidelines"</li>
                  <li>• "What documents can I access?"</li>
                  <li>• "Help me with patient care procedures"</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Info Alert */}
        <Alert>
          <Users className="h-4 w-4" />
          <AlertDescription>
            <strong>Demo Mode:</strong> All demo users share the same password: <code className="bg-gray-100 px-1 rounded">secure_password</code>. 
            This allows you to quickly switch between different user roles to test permissions and see how the RAG system 
            provides different responses based on user access levels.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}
