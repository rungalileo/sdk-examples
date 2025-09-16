import { useState } from 'react';
import { useFetcher } from 'react-router';
import { 
  Users, 
  ChevronDown, 
  UserCheck, 
  Activity, 
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { User } from '@/lib/types';

interface DemoUser {
  username: string;
  password: string;
  role: string;
  department: string;
  description: string;
  permissions: string[];
}

const DEMO_USERS: DemoUser[] = [
  {
    username: 'admin_wilson',
    password: 'secure_password',
    role: 'admin',
    department: 'administration',
    description: 'Full system access, can manage all users and documents',
    permissions: ['All documents', 'All departments', 'User management', 'System settings']
  },
  {
    username: 'dr_smith',
    password: 'secure_password', 
    role: 'doctor',
    department: 'cardiology',
    description: 'Cardiology specialist with access to patient records and protocols',
    permissions: ['Cardiology documents', 'Patient records', 'Medical protocols', 'Chat assistant']
  },
  {
    username: 'nurse_johnson',
    password: 'secure_password',
    role: 'nurse', 
    department: 'emergency',
    description: 'Emergency department nurse with access to emergency protocols',
    permissions: ['Emergency documents', 'Patient care protocols', 'Chat assistant']
  }
];

function getRoleIcon(role: string) {
  switch (role) {
    case 'doctor':
      return <UserCheck className="h-4 w-4" />;
    case 'nurse':
      return <Activity className="h-4 w-4" />;
    case 'admin':
      return <ShieldCheck className="h-4 w-4" />;
    default:
      return null;
  }
}

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

interface UserSwitcherProps {
  currentUser: User;
}

export function UserSwitcher({ currentUser }: UserSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const fetcher = useFetcher();
  const isSwitching = fetcher.state === 'submitting';

  const handleUserSwitch = async (user: DemoUser) => {
    // Create form data for login
    const formData = new FormData();
    formData.append('username', user.username);
    formData.append('password', user.password);
    
    // Submit login form
    fetcher.submit(formData, { 
      method: 'post', 
      action: '/login'
    });
  };

  const isCurrentUser = (user: DemoUser) => {
    return user.username === currentUser.username;
  };

  return (
    <div className="relative">
      {/* Current User Display */}
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full justify-between"
        disabled={isSwitching}
      >
        <div className="flex items-center space-x-2">
          <Users className="h-4 w-4" />
          <span className="truncate">
            {currentUser.username} ({currentUser.role})
          </span>
        </div>
        <ChevronDown className={cn(
          "h-4 w-4 transition-transform",
          isOpen && "rotate-180"
        )} />
      </Button>

      {/* User Selection Dropdown */}
      {isOpen && (
        <Card className="absolute top-full left-0 right-0 mt-2 z-50 shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center">
              <RefreshCw className="h-4 w-4 mr-2" />
              Switch User Role
            </CardTitle>
            <CardDescription className="text-xs">
              Quickly switch between different user roles to test permissions and document access
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {DEMO_USERS.map((user) => (
              <div
                key={user.username}
                className={cn(
                  "p-3 rounded-lg border transition-colors cursor-pointer",
                  isCurrentUser(user) 
                    ? "bg-blue-50 border-blue-200" 
                    : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                )}
                onClick={() => {
                  if (!isCurrentUser(user)) {
                    handleUserSwitch(user);
                  }
                  setIsOpen(false);
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-sm">{user.username}</span>
                      <Badge variant={getRoleBadgeVariant(user.role)} className="text-xs">
                        <span className="flex items-center">
                          {getRoleIcon(user.role)}
                          <span className="ml-1 capitalize">{user.role}</span>
                        </span>
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">{user.description}</p>
                    <div className="text-xs text-gray-500">
                      <span className="font-medium">Department:</span> {user.department}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      <span className="font-medium">Permissions:</span>
                      <ul className="list-disc list-inside ml-2 mt-1">
                        {user.permissions.map((permission, idx) => (
                          <li key={idx}>{permission}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  {isCurrentUser(user) && (
                    <div className="flex-shrink-0 ml-2">
                      <Badge variant="default" className="text-xs">
                        Current
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Info Section */}
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-xs text-blue-800">
                <strong>💡 Pro Tip:</strong> Use this switcher to test how the RAG chat assistant 
                responds differently based on user permissions. Each role has access to different 
                documents and departments.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading Overlay */}
      {isSwitching && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <RefreshCw className="h-4 w-4 animate-spin" />
            <span>Switching user...</span>
          </div>
        </div>
      )}
    </div>
  );
}
