import { useState, useRef } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { useFetcher, useLoaderData, useNavigate } from 'react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertTriangle,
  Building,
  User,
  AlertCircle
} from 'lucide-react';
import type { User as UserType, Patient } from '@/lib/types';
import { serverApi } from '@/lib/api.server';

interface DocumentUploadProps {
  patients?: Patient[];
  user?: UserType;
}

interface UploadFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
  title?: string;
  documentType?: string;
  department?: string;
  patientId?: string;
  isSensitive?: boolean;
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

const documentTypes = [
  { value: 'protocol', label: 'Protocol', icon: '📋' },
  { value: 'policy', label: 'Policy', icon: '📜' },
  { value: 'guideline', label: 'Guideline', icon: '📖' },
  { value: 'research', label: 'Research', icon: '🔬' },
  { value: 'report', label: 'Report', icon: '📊' },
  { value: 'medical_record', label: 'Medical Record', icon: '📝' },
];

export function DocumentUpload({ patients = [], user }: DocumentUploadProps) {
  const fetcher = useFetcher();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [completedUploads, setCompletedUploads] = useState(0);

  // Default values
  const defaultDepartment = user?.department || 'general';
  const defaultDocumentType = 'medical_record';

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const handleFiles = (files: File[]) => {
    const validFiles = files.filter(file => {
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return false;
      }
      
      // Check file type (text files, PDFs, docs)
      const allowedTypes = [
        'text/plain',
        'text/markdown', 
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      
      if (!allowedTypes.includes(file.type)) {
        alert(`File ${file.name} is not a supported format. Supported: TXT, MD, PDF, DOC, DOCX`);
        return false;
      }
      
      return true;
    });

    const newUploadFiles: UploadFile[] = validFiles.map(file => ({
      file,
      id: Math.random().toString(36).substring(7),
      status: 'pending',
      progress: 0,
      title: file.name.replace(/\.[^/.]+$/, ''), // Remove extension
      documentType: defaultDocumentType,
      department: defaultDepartment,
      patientId: '',
      isSensitive: false,
    }));

    setUploadFiles(prev => [...prev, ...newUploadFiles]);
  };

  const updateUploadFile = (id: string, updates: Partial<UploadFile>) => {
    setUploadFiles(prev => prev.map(file => 
      file.id === id ? { ...file, ...updates } : file
    ));
  };

  const removeUploadFile = (id: string) => {
    setUploadFiles(prev => prev.filter(file => file.id !== id));
  };

  const uploadSingleFile = async (uploadFile: UploadFile) => {
    updateUploadFile(uploadFile.id, { status: 'uploading', progress: 0 });

    try {
      const formData = new FormData();
      formData.append('file', uploadFile.file);
      formData.append('title', uploadFile.title || '');
      formData.append('document_type', uploadFile.documentType || '');
      formData.append('department', uploadFile.department || '');
      formData.append('is_sensitive', uploadFile.isSensitive?.toString() || 'false');
      
      if (uploadFile.patientId) {
        formData.append('patient_id', uploadFile.patientId);
      }

      // Simulate progress
      const progressInterval = setInterval(() => {
        updateUploadFile(uploadFile.id, { 
          progress: Math.min(uploadFile.progress + 10, 90) 
        });
      }, 200);

      // Get auth token from cookies
      const token = document.cookie.match(/authToken=([^;]+)/)?.[1];
      
      if (!token) {
        throw new Error('Authentication required');
      }
      
      const result = await serverApi.uploadDocument(formData, token);

      clearInterval(progressInterval);

      updateUploadFile(uploadFile.id, { 
        status: 'success', 
        progress: 100 
      });
      setCompletedUploads(prev => prev + 1);
    } catch (error) {
      updateUploadFile(uploadFile.id, { 
        status: 'error', 
        progress: 0,
        error: error instanceof Error ? error.message : 'Upload failed'
      });
    }
  };

  const handleUploadAll = async () => {
    if (uploadFiles.length === 0) return;

    setIsUploading(true);
    
    const pendingFiles = uploadFiles.filter(file => file.status === 'pending');
    
    // Upload files sequentially to avoid overwhelming the server
    for (const file of pendingFiles) {
      await uploadSingleFile(file);
    }
    
    setIsUploading(false);
    
    // Show success message if any uploads completed
    const successCount = uploadFiles.filter(f => f.status === 'success').length;
    if (successCount > 0) {
      // You might want to add a toast notification here
      console.log(`Successfully uploaded ${successCount} documents`);
    }
  };

  const handleClearCompleted = () => {
    setUploadFiles(prev => prev.filter(file => 
      file.status !== 'success' && file.status !== 'error'
    ));
  };

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf': return '📄';
      case 'doc':
      case 'docx': return '📝';
      case 'txt': return '📄';
      case 'md': return '📝';
      default: return '📄';
    }
  };

  const getStatusColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending': return 'text-gray-500';
      case 'uploading': return 'text-blue-500';
      case 'success': return 'text-green-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending': return <FileText className="h-4 w-4" />;
      case 'uploading': return <Upload className="h-4 w-4 animate-pulse" />;
      case 'success': return <CheckCircle className="h-4 w-4" />;
      case 'error': return <AlertTriangle className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const canUpload = user && ['doctor', 'admin'].includes(user.role);

  if (!canUpload) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Only doctors and administrators can upload documents.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Success Notification */}
      {completedUploads > 0 && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            Successfully uploaded {completedUploads} document{completedUploads > 1 ? 's' : ''}! 
            Refresh the page to see the new documents in the list above.
          </AlertDescription>
        </Alert>
      )}

      {/* Upload Zone */}
      <Card 
        className={`border-2 border-dashed transition-colors cursor-pointer ${
          isDragOver 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <CardContent className="p-8">
          <div className="text-center">
            <Upload className={`mx-auto h-12 w-12 ${
              isDragOver ? 'text-blue-500' : 'text-gray-400'
            }`} />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {isDragOver ? 'Drop files here' : 'Upload new documents'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Drag and drop files here, or click to browse
            </p>
            <p className="mt-1 text-xs text-gray-400">
              Supported formats: TXT, MD, PDF, DOC, DOCX (Max 10MB each)
            </p>
            <div className="mt-6">
              <Button variant="outline">
                <Upload className="mr-2 h-4 w-4" />
                Choose Files
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".txt,.md,.pdf,.doc,.docx"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Upload Queue */}
      {uploadFiles.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Upload Queue ({uploadFiles.length})</h3>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleClearCompleted}
                  disabled={isUploading}
                >
                  Clear Completed
                </Button>
                <Button 
                  variant="healthcare" 
                  size="sm"
                  onClick={handleUploadAll}
                  disabled={isUploading || uploadFiles.every(f => f.status !== 'pending')}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  {isUploading ? 'Uploading...' : 'Upload All'}
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              {uploadFiles.map((uploadFile) => (
                <div key={uploadFile.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">
                        {getFileIcon(uploadFile.file.name)}
                      </div>
                      <div>
                        <p className="font-medium">{uploadFile.file.name}</p>
                        <p className="text-sm text-gray-500">
                          {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className={`flex items-center space-x-1 ${getStatusColor(uploadFile.status)}`}>
                        {getStatusIcon(uploadFile.status)}
                        <span className="text-sm capitalize">{uploadFile.status}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeUploadFile(uploadFile.id)}
                        disabled={uploadFile.status === 'uploading'}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {uploadFile.status === 'uploading' && (
                    <div className="mb-3">
                      <Progress value={uploadFile.progress} className="h-2" />
                      <p className="text-xs text-gray-500 mt-1">
                        {uploadFile.progress}% uploaded
                      </p>
                    </div>
                  )}

                  {/* Error Message */}
                  {uploadFile.status === 'error' && uploadFile.error && (
                    <Alert className="mb-3" variant="destructive">
                      <AlertDescription>{uploadFile.error}</AlertDescription>
                    </Alert>
                  )}

                  {/* File Metadata Form */}
                  {uploadFile.status === 'pending' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <Label htmlFor={`title-${uploadFile.id}`}>Title</Label>
                        <Input
                          id={`title-${uploadFile.id}`}
                          value={uploadFile.title}
                          onChange={(e) => updateUploadFile(uploadFile.id, { title: e.target.value })}
                          placeholder="Document title"
                        />
                      </div>

                      <div>
                        <Label>Document Type</Label>
                        <Select 
                          value={uploadFile.documentType} 
                          onValueChange={(value) => updateUploadFile(uploadFile.id, { documentType: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
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
                      </div>

                      <div>
                        <Label>Department</Label>
                        <Select 
                          value={uploadFile.department} 
                          onValueChange={(value) => updateUploadFile(uploadFile.id, { department: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {departments.map((dept) => (
                              <SelectItem key={dept.value} value={dept.value}>
                                {dept.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Patient (Optional)</Label>
                        <Select 
                          value={uploadFile.patientId} 
                          onValueChange={(value) => updateUploadFile(uploadFile.id, { patientId: value })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select patient" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">No associated patient</SelectItem>
                            {patients
                              .filter(p => p.department === uploadFile.department)
                              .map((patient) => (
                                <SelectItem key={patient.id} value={patient.id.toString()}>
                                  {patient.name} - {patient.medical_record_number}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="sm:col-span-2 lg:col-span-4">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id={`sensitive-${uploadFile.id}`}
                            checked={uploadFile.isSensitive}
                            onCheckedChange={(checked) => 
                              updateUploadFile(uploadFile.id, { isSensitive: checked as boolean })
                            }
                          />
                          <Label htmlFor={`sensitive-${uploadFile.id}`} className="flex items-center cursor-pointer">
                            <AlertTriangle className="mr-2 h-4 w-4 text-red-500" />
                            Mark as Sensitive Document
                          </Label>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}