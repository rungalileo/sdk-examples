import { useForm, getFormProps, getInputProps, getSelectProps } from '@conform-to/react';
import { parseWithZod } from '@conform-to/zod';
import { z } from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Save, UserPlus } from 'lucide-react';
import type { User } from '@/lib/types';

const userSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters').optional(),
  role: z.enum(['doctor', 'nurse', 'admin']),
  department: z.enum(['cardiology', 'neurology', 'pediatrics', 'oncology', 'emergency', 'endocrinology', 'general']),
});

interface UserFormProps {
  user?: User;
  isEdit?: boolean;
  error?: string;
  departments?: string[];
  roles?: string[];
}

export function UserForm({ user, isEdit = false, error, departments, roles }: UserFormProps) {
  const [form, fields] = useForm({
    defaultValue: {
      username: user?.username || '',
      email: user?.email || '',
      role: user?.role || 'nurse',
      department: user?.department || 'general',
      password: '',
    },
    onValidate({ formData }) {
      return parseWithZod(formData, { schema: userSchema });
    },
  });

  const defaultDepartments = [
    'cardiology', 'neurology', 'pediatrics', 'oncology', 
    'emergency', 'endocrinology', 'general'
  ];
  
  const defaultRoles = ['doctor', 'nurse', 'admin'];

  const departmentList = departments || defaultDepartments;
  const roleList = roles || defaultRoles;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UserPlus className="h-5 w-5" />
          {isEdit ? 'Edit User' : 'Create New User'}
        </CardTitle>
        <CardDescription>
          {isEdit 
            ? 'Update user account information and permissions' 
            : 'Add a new user to the Healthcare Support Portal'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        <form {...getFormProps(form)} method="post" className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor={fields.username.id}>Username</Label>
              <Input
                {...getInputProps(fields.username, { type: 'text' })}
                placeholder="Enter username"
                disabled={isEdit}
              />
              {fields.username.errors && (
                <p className="text-sm text-red-500">{fields.username.errors}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor={fields.email.id}>Email</Label>
              <Input
                {...getInputProps(fields.email, { type: 'email' })}
                placeholder="user@example.com"
              />
              {fields.email.errors && (
                <p className="text-sm text-red-500">{fields.email.errors}</p>
              )}
            </div>

            {!isEdit && (
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor={fields.password.id}>Password</Label>
                <Input
                  {...getInputProps(fields.password, { type: 'password' })}
                  placeholder="Enter password (min 8 characters)"
                />
                {fields.password.errors && (
                  <p className="text-sm text-red-500">{fields.password.errors}</p>
                )}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor={fields.role.id}>Role</Label>
              <select
                {...getSelectProps(fields.role)}
                className="w-full h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                {roleList.map(role => (
                  <option key={role} value={role} className="capitalize">
                    {role.charAt(0).toUpperCase() + role.slice(1)}
                  </option>
                ))}
              </select>
              {fields.role.errors && (
                <p className="text-sm text-red-500">{fields.role.errors}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor={fields.department.id}>Department</Label>
              <select
                {...getSelectProps(fields.department)}
                className="w-full h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                {departmentList.map(dept => (
                  <option key={dept} value={dept} className="capitalize">
                    {dept.charAt(0).toUpperCase() + dept.slice(1)}
                  </option>
                ))}
              </select>
              {fields.department.errors && (
                <p className="text-sm text-red-500">{fields.department.errors}</p>
              )}
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={() => window.history.back()}>
              Cancel
            </Button>
            <Button type="submit" variant="healthcare">
              <Save className="mr-2 h-4 w-4" />
              {isEdit ? 'Update User' : 'Create User'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}