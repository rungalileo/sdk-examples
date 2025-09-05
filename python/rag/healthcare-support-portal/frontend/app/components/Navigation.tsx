import { useState } from 'react';
import { Link, useLocation } from 'react-router';
import { 
  Home, 
  Users, 
  MessageSquare, 
  FileText, 
  Settings, 
  LogOut,
  Menu,
  X,
  Activity,
  UserCheck,
  ShieldCheck
} from 'lucide-react';
import type { User } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  href: string;
  icon: any;
  roles?: string[];
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Patients', href: '/patients', icon: Users, roles: ['doctor', 'nurse', 'admin'] },
  { name: 'Chat Assistant', href: '/chat', icon: MessageSquare },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'User Management', href: '/users', icon: Users, roles: ['admin'] },
  { name: 'Settings', href: '/settings', icon: Settings, roles: ['admin'] },
];

function getInitials(name: string): string {
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

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

function getUserDisplayName(user: User | null): string {
  if (!user) return 'Unknown User';
  return user.username || 'Unknown User';
}

function hasRole(user: User, roles: string[]): boolean {
  return roles.includes(user.role);
}

interface NavigationProps {
  user: User;
}

export function Navigation({ user }: NavigationProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const filteredNavigation = navigation.filter(item => 
    !item.roles || hasRole(user, item.roles)
  );

  const handleLogout = () => {
    // Create a form to submit logout
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/logout';
    document.body.appendChild(form);
    form.submit();
  };

  return (
    <>
      {/* Mobile sidebar */}
      <div className={cn(
        "fixed inset-0 z-50 lg:hidden",
        sidebarOpen ? "block" : "hidden"
      )}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white shadow-xl">
          <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-healthcare-blue rounded-lg flex items-center justify-center">
                <Activity className="h-5 w-5 text-white" />
              </div>
              <span className="ml-2 text-xl font-semibold text-gray-900">
                Healthcare Portal
              </span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-6 w-6" />
            </Button>
          </div>
          
          <nav className="flex-1 px-4 py-4 space-y-1">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-healthcare-blue text-white"
                      : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  )}
                >
                  <item.icon
                    className={cn(
                      "mr-3 h-5 w-5 flex-shrink-0",
                      isActive ? "text-white" : "text-gray-400 group-hover:text-gray-500"
                    )}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center">
              <Avatar className="h-10 w-10">
                <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${user.username}`} />
                <AvatarFallback>{getInitials(user.username)}</AvatarFallback>
              </Avatar>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-gray-900">
                  {getUserDisplayName(user)}
                </p>
                <div className="flex items-center mt-1">
                  <Badge variant={getRoleBadgeVariant(user.role)} className="text-xs">
                    <span className="flex items-center">
                      {getRoleIcon(user.role)}
                      <span className="ml-1 capitalize">{user.role}</span>
                    </span>
                  </Badge>
                </div>
                <p className="text-xs text-gray-500 capitalize mt-1">
                  {user.department}
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="mt-3 w-full justify-start"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </Button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white border-r border-gray-200 px-6 pb-4">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center">
            <div className="h-8 w-8 bg-healthcare-blue rounded-lg flex items-center justify-center">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <span className="ml-2 text-xl font-semibold text-gray-900">
              Healthcare Portal
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {filteredNavigation.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={cn(
                            "group flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 transition-colors",
                            isActive
                              ? "bg-healthcare-blue text-white"
                              : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                          )}
                        >
                          <item.icon
                            className={cn(
                              "h-5 w-5 shrink-0",
                              isActive ? "text-white" : "text-gray-400 group-hover:text-gray-500"
                            )}
                          />
                          {item.name}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </li>

              {/* User section */}
              <li className="mt-auto">
                <div className="border-t border-gray-200 pt-4">
                  <div className="flex items-center">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${user.username}`} />
                      <AvatarFallback>{getInitials(user.username)}</AvatarFallback>
                    </Avatar>
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {getUserDisplayName(user)}
                      </p>
                      <div className="flex items-center mt-1">
                        <Badge variant={getRoleBadgeVariant(user.role)} className="text-xs">
                          <span className="flex items-center">
                            {getRoleIcon(user.role)}
                            <span className="ml-1 capitalize">{user.role}</span>
                          </span>
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-500 capitalize mt-1">
                        {user.department}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    className="mt-3 w-full justify-start"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign out
                  </Button>
                </div>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Mobile header */}
      <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:hidden">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu className="h-5 w-5" />
        </Button>

        <div className="h-6 w-px bg-gray-200" />

        <div className="flex flex-1 items-center justify-between">
          <div className="flex items-center">
            <div className="h-6 w-6 bg-healthcare-blue rounded flex items-center justify-center">
              <Activity className="h-4 w-4 text-white" />
            </div>
            <span className="ml-2 text-lg font-semibold text-gray-900">
              Healthcare Portal
            </span>
          </div>

          <div className="flex items-center gap-x-4">
            <Avatar className="h-8 w-8">
              <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${user.username}`} />
              <AvatarFallback>{getInitials(user.username)}</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </div>
    </>
  );
}