// User and Authentication Types
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'doctor' | 'nurse' | 'admin';
  department: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role: 'doctor' | 'nurse' | 'admin';
  department: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface AuthContext {
  user: User | null;
  token: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  isLoading: boolean;
  isAuthenticated: boolean;
}

// Patient Types
export interface Patient {
  id: number;
  name: string;
  date_of_birth: string | null;
  medical_record_number: string;
  department: string;
  assigned_doctor_id: number | null;
  is_active: boolean;
  created_at: string;
  assigned_doctor?: User;
}

export interface PatientCreate {
  name: string;
  date_of_birth?: string;
  medical_record_number: string;
  department: string;
  assigned_doctor_id?: number;
}

export interface PatientUpdate extends Partial<PatientCreate> {
  is_active?: boolean;
}

// Document Types
export interface Document {
  id: number;
  title: string;
  content: string;
  document_type: string;
  patient_id: number | null;
  department: string;
  created_by_id: number;
  is_sensitive: boolean;
  created_at: string;
  patient?: Patient;
  created_by?: User;
}

export interface DocumentCreate {
  title: string;
  content: string;
  document_type: string;
  patient_id?: number;
  department: string;
  is_sensitive?: boolean;
}

export interface DocumentUpdate extends Partial<DocumentCreate> {}

// Chat and RAG Types
export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: SearchResult[];
  token_count?: number;
}

export interface ChatRequest {
  message: string;
  context_patient_id?: number;
  context_department?: string;
  max_results?: number;
}

export interface ChatResponse {
  response: string;
  sources: SearchResult[];
  token_count: number;
  context_used: boolean;
}

export interface SearchRequest {
  query: string;
  document_types?: string[];
  department?: string;
  limit?: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total_results: number;
}

export interface SearchResult {
  id: number;
  title: string;
  content_chunk: string;
  document_type: string;
  department: string;
  similarity_score: number;
  created_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Form Types
export interface FormField {
  label: string;
  name: string;
  type: 'text' | 'email' | 'password' | 'select' | 'textarea' | 'date' | 'checkbox';
  placeholder?: string;
  required?: boolean;
  options?: { label: string; value: string }[];
  validation?: any; // Zod schema
}

// UI Component Types
export interface NavItem {
  label: string;
  href: string;
  icon?: any;
  roles?: string[];
  children?: NavItem[];
}

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => React.ReactNode;
}

export interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  dismissible?: boolean;
}

// Utility Types
export type Role = 'doctor' | 'nurse' | 'admin';

export type Department = 
  | 'cardiology' 
  | 'neurology' 
  | 'pediatrics' 
  | 'oncology' 
  | 'emergency' 
  | 'endocrinology' 
  | 'general';

export type DocumentType = 
  | 'medical_record' 
  | 'protocol' 
  | 'policy' 
  | 'guideline' 
  | 'research' 
  | 'report';

export type Status = 'active' | 'inactive' | 'pending' | 'urgent';

// Environment Variables
export interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_AUTH_SERVICE_PORT: string;
  readonly VITE_PATIENT_SERVICE_PORT: string;
  readonly VITE_RAG_SERVICE_PORT: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_DEBUG: string;
}

export interface ImportMeta {
  readonly env: ImportMetaEnv;
}