import { useState, useEffect } from 'react';
import { Link, useLoaderData } from 'react-router';
import { 
  Plus, 
  Search, 
  Filter, 
  Users, 
  Edit, 
  Mail, 
  Shield,
  Building,
  UserCheck,
  MoreVertical
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { formatDateTime, getDepartmentColor } from '@/lib/utils';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { serverApi } from '@/lib/api.server';
import type { User } from '@/lib/types';
import type { LoaderFunctionArgs } from 'react-router';

interface UsersData {
  currentUser: User;
  users: User[];
}

// Loader function - fetch users data
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication and admin role
    const currentUser = await requireAuth(request);
    
    // Check if user is admin
    if (currentUser.role !== 'admin') {
      throw new Response('Access denied. Admin privileges required.', { status: 403 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load users
    const users = await serverApi.getUsers(token);

    return {
      currentUser,
      users
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

export default function UsersIndex() {
  const { currentUser, users } = useLoaderData<UsersData>();
  const [filteredUsers, setFilteredUsers] = useState<User[]>(users);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');

  useEffect(() => {
    filterUsers();
  }, [users, searchTerm, roleFilter, departmentFilter]);

  const filterUsers = () => {
    let filtered = users;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(user =>
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Role filter
    if (roleFilter !== 'all') {
      filtered = filtered.filter(user => user.role === roleFilter);
    }

    // Department filter
    if (departmentFilter !== 'all') {
      filtered = filtered.filter(user => user.department === departmentFilter);
    }

    setFilteredUsers(filtered);
  };

  const departments = Array.from(new Set(users.map(u => u.department))).sort();
  const roles = Array.from(new Set(users.map(u => u.role))).sort();

  const getRoleBadgeVariant = (role: string) => {
    switch(role) {
      case 'admin': return 'destructive';
      case 'doctor': return 'default';
      case 'nurse': return 'secondary';
      default: return 'outline';
    }
  };

  const getRoleIcon = (role: string) => {
    switch(role) {
      case 'admin': return <Shield className="h-3 w-3" />;
      case 'doctor': return <UserCheck className="h-3 w-3" />;
      default: return <Users className="h-3 w-3" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            User Management
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage user accounts and permissions
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <Button asChild variant="healthcare">
            <Link to="/users/new">
              <Plus className="mr-2 h-4 w-4" />
              Add User
            </Link>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="all">All Roles</option>
              {roles.map(role => (
                <option key={role} value={role} className="capitalize">
                  {role.charAt(0).toUpperCase() + role.slice(1)}
                </option>
              ))}
            </select>
            <select
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
              className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="all">All Departments</option>
              {departments.map(dept => (
                <option key={dept} value={dept} className="capitalize">
                  {dept.charAt(0).toUpperCase() + dept.slice(1)}
                </option>
              ))}
            </select>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Users className="h-4 w-4" />
              <span>{filteredUsers.length} users</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
          <CardDescription>
            A list of all users in the Healthcare Support Portal
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredUsers.length === 0 ? (
            <div className="p-12 text-center">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {users.length === 0 
                  ? "Get started by adding your first user."
                  : "Try adjusting your search or filter criteria."
                }
              </p>
              {users.length === 0 && (
                <div className="mt-6">
                  <Button asChild variant="healthcare">
                    <Link to="/users/new">
                      <Plus className="mr-2 h-4 w-4" />
                      Add User
                    </Link>
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-medium">{user.username}</span>
                        <span className="text-sm text-gray-500 flex items-center">
                          <Mail className="mr-1 h-3 w-3" />
                          {user.email}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(user.role)} className="capitalize">
                        <span className="flex items-center gap-1">
                          {getRoleIcon(user.role)}
                          {user.role}
                        </span>
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        <Building className="mr-1 h-3 w-3" />
                        {user.department}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={user.is_active ? 'active' : 'inactive'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {formatDateTime(user.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem asChild>
                            <Link to={`/users/${user.id}/edit`}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit User
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            disabled={user.id === currentUser.id}
                            className="text-red-600"
                          >
                            Deactivate User
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {users.filter(u => u.is_active).length}
              </div>
              <div className="text-sm text-gray-500">Active Users</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {users.filter(u => u.role === 'admin').length}
              </div>
              <div className="text-sm text-gray-500">Administrators</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {users.filter(u => u.role === 'doctor').length}
              </div>
              <div className="text-sm text-gray-500">Doctors</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {users.filter(u => u.role === 'nurse').length}
              </div>
              <div className="text-sm text-gray-500">Nurses</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}