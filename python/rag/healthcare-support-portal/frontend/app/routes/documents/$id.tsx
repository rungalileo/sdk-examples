import { useLoaderData, Link } from 'react-router';
import { 
  ArrowLeft, 
  Download, 
  Edit, 
  Calendar, 
  User as UserIcon, 
  MapPin, 
  FileText,
  AlertCircle,
  Shield,
  Eye
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { EmbeddingStatus } from '@/components/embeddings/EmbeddingStatus';
import { formatDateTime, getDepartmentColor } from '@/lib/utils';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { serverApi } from '@/lib/api.server';
import type { Document, User } from '@/lib/types';
import type { LoaderFunctionArgs } from 'react-router';

interface DocumentDetailData {
  user: User;
  document: Document;
  embeddingStatus: any;
}

// Loader function - fetch individual document data
export async function loader({ request, params }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const user = await requireAuth(request);
    
    const documentId = params.id;
    if (!documentId || isNaN(Number(documentId))) {
      throw new Response('Invalid document ID', { status: 400 });
    }
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load document and embedding status
    const [document, embeddingStatus] = await Promise.all([
      serverApi.getDocument(parseInt(documentId), token),
      serverApi.getEmbeddingStatus(parseInt(documentId), token).catch(() => null)
    ]);

    return {
      user,
      document,
      embeddingStatus
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

export default function DocumentDetail() {
  const { user, document, embeddingStatus } = useLoaderData<DocumentDetailData>();

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

  const handleDownload = () => {
    // Create a blob with the document content
    const blob = new Blob([document.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `${document.title}.txt`;
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm" asChild>
            <Link to="/documents">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Documents
            </Link>
          </Button>
          <div>
            <div className="flex items-center space-x-3">
              <div className="text-3xl">
                {getDocumentIcon(document.document_type)}
              </div>
              <div>
                <h1 className="text-2xl font-bold leading-7 text-gray-900">
                  {document.title}
                </h1>
                <div className="flex items-center space-x-2 mt-1">
                  <Badge variant="outline" className="capitalize">
                    {document.document_type.replace('_', ' ')}
                  </Badge>
                  {document.is_sensitive && (
                    <Badge variant="destructive">
                      <AlertCircle className="mr-1 h-3 w-3" />
                      Sensitive
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleDownload}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
          {(user?.role === 'admin' || document.created_by_id === user?.id) && (
            <Button size="sm">
              <Edit className="mr-2 h-4 w-4" />
              Edit Document
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Document Content */}
          <Card>
            <CardHeader>
              <CardTitle>Document Content</CardTitle>
              <CardDescription>
                Full content of the document
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none">
                <div className="whitespace-pre-wrap text-gray-900 font-mono text-sm leading-relaxed">
                  {document.content}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Embedding Status */}
          {embeddingStatus && (
            <Card>
              <CardHeader>
                <CardTitle>AI Processing Status</CardTitle>
                <CardDescription>
                  Vector embedding status for AI-powered search and chat
                </CardDescription>
              </CardHeader>
              <CardContent>
                <EmbeddingStatus
                  documentId={document.id}
                  hasEmbeddings={embeddingStatus?.has_embeddings ?? false}
                  embeddingCount={embeddingStatus?.embedding_count ?? 0}
                  canRegenerate={user?.role === 'admin' || user?.role === 'doctor'}
                />
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Document Information */}
          <Card className={getDepartmentColor(document.department)}>
            <CardHeader>
              <CardTitle className="text-lg">Document Details</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Type</dt>
                  <dd className="mt-1 text-sm text-gray-900 capitalize">
                    {document.document_type.replace('_', ' ')}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Department</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center capitalize">
                    <MapPin className="mr-2 h-4 w-4 text-gray-400" />
                    {document.department}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Created</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Calendar className="mr-2 h-4 w-4 text-gray-400" />
                    {formatDateTime(document.created_at)}
                  </dd>
                </div>

                {document.created_by && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Created By</dt>
                    <dd className="mt-1 text-sm text-gray-900 flex items-center">
                      <UserIcon className="mr-2 h-4 w-4 text-gray-400" />
                      {document.created_by.username}
                    </dd>
                  </div>
                )}

                <div>
                  <dt className="text-sm font-medium text-gray-500">Sensitivity</dt>
                  <dd className="mt-1">
                    {document.is_sensitive ? (
                      <Badge variant="destructive">
                        <Shield className="mr-1 h-3 w-3" />
                        Sensitive Document
                      </Badge>
                    ) : (
                      <Badge variant="outline">
                        <Eye className="mr-1 h-3 w-3" />
                        Standard Access
                      </Badge>
                    )}
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {/* Associated Patient */}
          {document.patient && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Associated Patient</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-4">
                  <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <UserIcon className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {document.patient.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      MRN: {document.patient.medical_record_number}
                    </p>
                    <Badge variant="outline" className="mt-1">
                      {document.patient.department}
                    </Badge>
                  </div>
                </div>
                <div className="mt-4">
                  <Button asChild variant="outline" size="sm" className="w-full">
                    <Link to={`/patients/${document.patient.id}`}>
                      View Patient Details
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start" onClick={handleDownload}>
                <Download className="mr-2 h-4 w-4" />
                Download Document
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                <Link to={`/chat?document=${document.id}`}>
                  <FileText className="mr-2 h-4 w-4" />
                  Chat About Document
                </Link>
              </Button>
              {(user?.role === 'admin' || document.created_by_id === user?.id) && (
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Document
                </Button>
              )}
              <Button variant="outline" size="sm" className="w-full justify-start" asChild>
                <Link to="/documents">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Documents
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}