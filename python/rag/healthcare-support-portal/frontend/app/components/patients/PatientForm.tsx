import { useState, useEffect } from 'react';
import { Form, useFetcher, useLoaderData } from 'react-router';
import { useForm, getFormProps, getInputProps, getSelectProps } from '@conform-to/react';
import { parseWithZod } from '@conform-to/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Save, User, Calendar, FileText, Building, UserCheck } from 'lucide-react';
import { Link } from 'react-router';
import { patientCreateSchema, patientUpdateSchema } from '@/lib/schemas';
import type { Patient, User as UserType } from '@/lib/types';

interface PatientFormProps {
  isEdit: boolean;
  patient?: Patient;
  doctors?: UserType[];
}

const departments = [
  { value: 'cardiology', label: 'Cardiology' },
  { value: 'neurology', label: 'Neurology' },
  { value: 'pediatrics', label: 'Pediatrics' },
  { value: 'oncology', label: 'Oncology' },
  { value: 'emergency', label: 'Emergency' },
  { value: 'endocrinology', label: 'Endocrinology' },
  { value: 'general', label: 'General Medicine' },
];

export function PatientForm({ isEdit, patient, doctors = [] }: PatientFormProps) {
  const fetcher = useFetcher();
  const [selectedDepartment, setSelectedDepartment] = useState(patient?.department || '');
  const [selectedDoctorId, setSelectedDoctorId] = useState(
    patient?.assigned_doctor_id?.toString() || ''
  );

  const schema = isEdit ? patientUpdateSchema : patientCreateSchema;

  const [form, fields] = useForm({
    onValidate({ formData }) {
      return parseWithZod(formData, { schema });
    },
    defaultValue: isEdit && patient ? {
      name: patient.name,
      date_of_birth: patient.date_of_birth || '',
      medical_record_number: patient.medical_record_number,
      department: patient.department,
      assigned_doctor_id: patient.assigned_doctor_id?.toString() || '',
    } : undefined,
  });

  // Filter doctors by selected department
  const availableDoctors = doctors.filter(doctor => 
    doctor.role === 'doctor' && 
    (!selectedDepartment || doctor.department === selectedDepartment)
  );

  // Auto-generate MRN for new patients
  const generateMRN = () => {
    const randomNumber = Math.floor(Math.random() * 900000) + 100000;
    return `MRN-${randomNumber}`;
  };

  useEffect(() => {
    // Generate MRN for new patients if not already set
    if (!isEdit && !fields.medical_record_number.value) {
      const mrnInput = document.querySelector('[name="medical_record_number"]') as HTMLInputElement;
      if (mrnInput) {
        mrnInput.value = generateMRN();
      }
    }
  }, [isEdit, fields.medical_record_number.value]);

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div className="flex items-center space-x-4">
        <Button asChild variant="ghost" size="sm">
          <Link to="/patients">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Patients
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="mr-2 h-5 w-5" />
            {isEdit ? 'Edit Patient' : 'Add New Patient'}
          </CardTitle>
          <CardDescription>
            {isEdit 
              ? 'Update patient information and assignments'
              : 'Create a new patient record for the Healthcare Support Portal'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          <fetcher.Form method={isEdit ? 'PUT' : 'POST'} {...getFormProps(form)}>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {/* Patient Name */}
              <div className="sm:col-span-2">
                <Label htmlFor={fields.name.id} className="flex items-center">
                  <User className="mr-2 h-4 w-4" />
                  Patient Name *
                </Label>
                <Input
                  {...getInputProps(fields.name, { type: 'text' })}
                  placeholder="Enter patient's full name"
                  className="mt-1"
                />
                {fields.name.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.name.errors[0]}</p>
                )}
              </div>

              {/* Date of Birth */}
              <div>
                <Label htmlFor={fields.date_of_birth.id} className="flex items-center">
                  <Calendar className="mr-2 h-4 w-4" />
                  Date of Birth
                </Label>
                <Input
                  {...getInputProps(fields.date_of_birth, { type: 'date' })}
                  className="mt-1"
                />
                {fields.date_of_birth.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.date_of_birth.errors[0]}</p>
                )}
              </div>

              {/* Medical Record Number */}
              <div>
                <Label htmlFor={fields.medical_record_number.id} className="flex items-center">
                  <FileText className="mr-2 h-4 w-4" />
                  Medical Record Number *
                </Label>
                <div className="mt-1 flex space-x-2">
                  <Input
                    {...getInputProps(fields.medical_record_number, { type: 'text' })}
                    placeholder="MRN-XXXXXX"
                    className="flex-1"
                  />
                  {!isEdit && (
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => {
                        const input = document.querySelector('[name="medical_record_number"]') as HTMLInputElement;
                        if (input) input.value = generateMRN();
                      }}
                    >
                      Generate
                    </Button>
                  )}
                </div>
                {fields.medical_record_number.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.medical_record_number.errors[0]}</p>
                )}
              </div>

              {/* Department */}
              <div>
                <Label className="flex items-center">
                  <Building className="mr-2 h-4 w-4" />
                  Department *
                </Label>
                <Select 
                  value={selectedDepartment} 
                  onValueChange={(value) => {
                    setSelectedDepartment(value);
                    setSelectedDoctorId(''); // Reset doctor selection when department changes
                  }}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map((dept) => (
                      <SelectItem key={dept.value} value={dept.value}>
                        {dept.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <input type="hidden" name="department" value={selectedDepartment} />
                {fields.department.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.department.errors[0]}</p>
                )}
              </div>

              {/* Assigned Doctor */}
              <div>
                <Label className="flex items-center">
                  <UserCheck className="mr-2 h-4 w-4" />
                  Assigned Doctor
                </Label>
                <Select 
                  value={selectedDoctorId} 
                  onValueChange={setSelectedDoctorId}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select doctor (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No assigned doctor</SelectItem>
                    {availableDoctors.map((doctor) => (
                      <SelectItem key={doctor.id} value={doctor.id.toString()}>
                        Dr. {doctor.username} - {doctor.department}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <input type="hidden" name="assigned_doctor_id" value={selectedDoctorId} />
                {fields.assigned_doctor_id.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.assigned_doctor_id.errors[0]}</p>
                )}
              </div>
            </div>

            {/* Form Status Messages */}
            {fetcher.data?.error && (
              <Alert className="mt-6" variant="destructive">
                <AlertDescription>{fetcher.data.error}</AlertDescription>
              </Alert>
            )}

            {fetcher.data?.success && (
              <Alert className="mt-6">
                <AlertDescription>{fetcher.data.message}</AlertDescription>
              </Alert>
            )}

            {/* Form Actions */}
            <div className="mt-8 flex justify-end space-x-3">
              <Button asChild variant="outline">
                <Link to="/patients">Cancel</Link>
              </Button>
              <Button 
                type="submit" 
                disabled={fetcher.state === 'submitting'}
                variant="healthcare"
              >
                <Save className="mr-2 h-4 w-4" />
                {fetcher.state === 'submitting' 
                  ? (isEdit ? 'Updating...' : 'Creating...') 
                  : (isEdit ? 'Update Patient' : 'Create Patient')
                }
              </Button>
            </div>
          </fetcher.Form>
        </CardContent>
      </Card>
    </div>
  );
}