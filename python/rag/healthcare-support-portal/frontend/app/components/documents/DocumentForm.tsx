import { useState, useEffect } from 'react';
import { Form, useFetcher, useLoaderData } from 'react-router';
import { useForm, getFormProps, getInputProps, getSelectProps, getTextareaProps } from '@conform-to/react';
import { parseWithZod } from '@conform-to/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { ArrowLeft, Save, FileText, Building, User, AlertTriangle, BookOpen } from 'lucide-react';
import { Link } from 'react-router';
import { documentCreateSchema, documentUpdateSchema } from '@/lib/schemas';
import type { Document, User as UserType, Patient } from '@/lib/types';

interface DocumentFormProps {
  isEdit: boolean;
  document?: Document;
  patients?: Patient[];
}

const departments = [
  { value: 'cardiology', label: 'Cardiology' },
  { value: 'neurology', label: 'Neurology' },
  { value: 'pediatrics', label: 'Pediatrics' },
  { value: 'oncology', label: 'Oncology' },
  { value: 'emergency', label: 'Emergency' },
  { value: 'endocrinology', label: 'Endocrinology' },
  { value: 'obgyn', label: 'OB/GYN' },
  { value: 'general', label: 'General Medicine' },
];

const documentTypes = [
  { value: 'protocol', label: 'Protocol', icon: '📋' },
  { value: 'policy', label: 'Policy', icon: '📜' },
  { value: 'guideline', label: 'Guideline', icon: '📖' },
  { value: 'research', label: 'Research', icon: '🔬' },
  { value: 'report', label: 'Report', icon: '📊' },
  { value: 'medical_record', label: 'Medical Record', icon: '📝' },
];

export function DocumentForm({ isEdit, document, patients = [] }: DocumentFormProps) {
  const fetcher = useFetcher();
  const [selectedDepartment, setSelectedDepartment] = useState(document?.department || '');
  const [selectedPatientId, setSelectedPatientId] = useState(
    document?.patient_id?.toString() || 'none'
  );
  const [selectedDocumentType, setSelectedDocumentType] = useState(document?.document_type || '');
  const [isSensitive, setIsSensitive] = useState(document?.is_sensitive || false);

  const schema = isEdit ? documentUpdateSchema : documentCreateSchema;

  const [form, fields] = useForm({
    onValidate({ formData }) {
      return parseWithZod(formData, { schema });
    },
    defaultValue: isEdit && document ? {
      title: document.title,
      content: document.content,
      document_type: document.document_type,
      patient_id: document.patient_id?.toString() || 'none',
      department: document.department,
      is_sensitive: document.is_sensitive,
    } : undefined,
  });

  // Filter patients by selected department
  const availablePatients = patients.filter(patient => 
    !selectedDepartment || patient.department === selectedDepartment
  );

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div className="flex items-center space-x-4">
        <Button asChild variant="ghost" size="sm">
          <Link to="/documents">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Documents
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="mr-2 h-5 w-5" />
            {isEdit ? 'Edit Document' : 'Create New Document'}
          </CardTitle>
          <CardDescription>
            {isEdit 
              ? 'Update document information and content'
              : 'Create a new document for the Healthcare Support Portal'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          <fetcher.Form method={isEdit ? 'PUT' : 'POST'} {...getFormProps(form)}>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {/* Document Title */}
              <div className="sm:col-span-2">
                <Label htmlFor={fields.title.id} className="flex items-center">
                  <BookOpen className="mr-2 h-4 w-4" />
                  Document Title *
                </Label>
                <Input
                  {...getInputProps(fields.title, { type: 'text' })}
                  placeholder="Enter document title"
                  className="mt-1"
                />
                {fields.title.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.title.errors[0]}</p>
                )}
              </div>

              {/* Document Type */}
              <div>
                <Label className="flex items-center">
                  <FileText className="mr-2 h-4 w-4" />
                  Document Type *
                </Label>
                <Select 
                  value={selectedDocumentType} 
                  onValueChange={setSelectedDocumentType}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select document type" />
                  </SelectTrigger>
                  <SelectContent>
                    {documentTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className="flex items-center">
                          <span className="mr-2">{type.icon}</span>
                          {type.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <input type="hidden" name="document_type" value={selectedDocumentType} />
                {fields.document_type.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.document_type.errors[0]}</p>
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
                    setSelectedPatientId('none'); // Reset patient selection when department changes
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

              {/* Associated Patient */}
              <div className="sm:col-span-2">
                <Label className="flex items-center">
                  <User className="mr-2 h-4 w-4" />
                  Associated Patient (Optional)
                </Label>
                <Select 
                  value={selectedPatientId} 
                  onValueChange={setSelectedPatientId}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select patient (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No associated patient</SelectItem>
                    {availablePatients.map((patient) => (
                      <SelectItem key={patient.id} value={patient.id.toString()}>
                        {patient.name} - {patient.medical_record_number}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <input type="hidden" name="patient_id" value={selectedPatientId === 'none' ? '' : selectedPatientId} />
                {fields.patient_id.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.patient_id.errors[0]}</p>
                )}
              </div>

              {/* Sensitive Document Checkbox */}
              <div className="sm:col-span-2">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="is_sensitive"
                    checked={isSensitive}
                    onCheckedChange={(checked) => setIsSensitive(checked as boolean)}
                  />
                  <Label htmlFor="is_sensitive" className="flex items-center cursor-pointer">
                    <AlertTriangle className="mr-2 h-4 w-4 text-red-500" />
                    Mark as Sensitive Document
                  </Label>
                </div>
                <input type="hidden" name="is_sensitive" value={isSensitive.toString()} />
                <p className="mt-1 text-sm text-gray-500">
                  Sensitive documents have restricted access based on role and department permissions.
                </p>
              </div>

              {/* Document Content */}
              <div className="sm:col-span-2">
                <Label htmlFor={fields.content.id} className="flex items-center">
                  <FileText className="mr-2 h-4 w-4" />
                  Document Content *
                </Label>
                <Textarea
                  {...getTextareaProps(fields.content)}
                  placeholder="Enter document content..."
                  className="mt-1 min-h-[200px]"
                />
                {fields.content.errors && (
                  <p className="mt-1 text-sm text-red-600">{fields.content.errors[0]}</p>
                )}
                <p className="mt-1 text-sm text-gray-500">
                  Content will be processed for AI-powered search and assistance features.
                </p>
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
                <Link to="/documents">Cancel</Link>
              </Button>
              <Button 
                type="submit" 
                disabled={fetcher.state === 'submitting'}
                variant="healthcare"
              >
                <Save className="mr-2 h-4 w-4" />
                {fetcher.state === 'submitting' 
                  ? (isEdit ? 'Updating...' : 'Creating...') 
                  : (isEdit ? 'Update Document' : 'Create Document')
                }
              </Button>
            </div>
          </fetcher.Form>
        </CardContent>
      </Card>

      {/* AI Processing Note */}
      {!isEdit && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center">
              <div className="text-blue-600 mr-3">🤖</div>
              <div>
                <h3 className="text-sm font-medium text-blue-800">AI Enhancement</h3>
                <p className="text-sm text-blue-700 mt-1">
                  This document will be automatically processed to create AI embeddings for intelligent search and chat assistance.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}