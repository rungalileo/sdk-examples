import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Patient,
  PatientCreate,
  PatientUpdate,
  Document,
  DocumentCreate,
  DocumentUpdate,
  ChatRequest,
  ChatResponse,
  SearchRequest,
  SearchResponse,
  ApiError
} from './types';

class ApiClient {
  private authApi: AxiosInstance;
  private patientApi: AxiosInstance;
  private ragApi: AxiosInstance;

  constructor() {
    const baseURL = import.meta.env.VITE_API_BASE_URL;
    const authPort = import.meta.env.VITE_AUTH_SERVICE_PORT;
    const patientPort = import.meta.env.VITE_PATIENT_SERVICE_PORT;
    const ragPort = import.meta.env.VITE_RAG_SERVICE_PORT;

    // Auth Service API
    this.authApi = axios.create({
      baseURL: `${baseURL}:${authPort}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Patient Service API
    this.patientApi = axios.create({
      baseURL: `${baseURL}:${patientPort}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // RAG Service API
    this.ragApi = axios.create({
      baseURL: `${baseURL}:${ragPort}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptors to include auth tokens
    this.setupInterceptors();
  }

  private setupInterceptors() {
    const requestInterceptor = (config: any) => {
      const token = localStorage.getItem('authToken');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    };

    const responseInterceptor = (response: AxiosResponse) => response;

    const errorInterceptor = (error: any) => {
      if (error.response?.status === 401) {
        // Token expired or invalid, clear auth and redirect to login
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    };

    // Apply interceptors to all API instances
    [this.authApi, this.patientApi, this.ragApi].forEach(api => {
      api.interceptors.request.use(requestInterceptor);
      api.interceptors.response.use(responseInterceptor, errorInterceptor);
    });
  }

  // Authentication Methods
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await this.authApi.post<AuthResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async register(userData: RegisterRequest): Promise<User> {
    try {
      const response = await this.authApi.post<User>('/auth/register', userData);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await this.authApi.get<User>('/auth/me');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    try {
      const response = await this.authApi.post<AuthResponse>('/auth/refresh');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async getUsers(): Promise<User[]> {
    try {
      const response = await this.authApi.get<User[]>('/users/');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Patient Methods
  async getPatients(): Promise<Patient[]> {
    try {
      const response = await this.patientApi.get<Patient[]>('/patients/');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async getPatient(id: number): Promise<Patient> {
    try {
      const response = await this.patientApi.get<Patient>(`/patients/${id}`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async createPatient(patientData: PatientCreate): Promise<Patient> {
    try {
      const response = await this.patientApi.post<Patient>('/patients/', patientData);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async updatePatient(id: number, patientData: PatientUpdate): Promise<Patient> {
    try {
      const response = await this.patientApi.put<Patient>(`/patients/${id}`, patientData);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async deletePatient(id: number): Promise<void> {
    try {
      await this.patientApi.delete(`/patients/${id}`);
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Document Methods
  async getDocuments(): Promise<Document[]> {
    try {
      const response = await this.ragApi.get<Document[]>('/documents/');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async getDocument(id: number): Promise<Document> {
    try {
      const response = await this.ragApi.get<Document>(`/documents/${id}`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async createDocument(documentData: DocumentCreate): Promise<Document> {
    try {
      const response = await this.ragApi.post<Document>('/documents/', documentData);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async updateDocument(id: number, documentData: DocumentUpdate): Promise<Document> {
    try {
      const response = await this.ragApi.put<Document>(`/documents/${id}`, documentData);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async deleteDocument(id: number): Promise<void> {
    try {
      await this.ragApi.delete(`/documents/${id}`);
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Chat and RAG Methods
  async searchDocuments(searchRequest: SearchRequest): Promise<SearchResponse> {
    try {
      const response = await this.ragApi.post<SearchResponse>('/chat/search', searchRequest);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async askQuestion(chatRequest: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.ragApi.post<ChatResponse>('/chat/ask', chatRequest);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async getConversationHistory(): Promise<any> {
    try {
      const response = await this.ragApi.get('/chat/conversation-history');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async submitFeedback(responseId: string, rating: number, feedback?: string): Promise<any> {
    try {
      const response = await this.ragApi.post('/chat/feedback', {
        response_id: responseId,
        rating,
        feedback
      });
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // File Upload Method
  async uploadFile(file: File, documentData: Partial<DocumentCreate>): Promise<Document> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Add document metadata
      Object.entries(documentData).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, value.toString());
        }
      });

      const response = await this.ragApi.post<Document>('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Health Check Methods
  async healthCheck(): Promise<{ [service: string]: any }> {
    const results: { [service: string]: any } = {};

    try {
      const authHealth = await this.authApi.get('/health');
      results.auth = authHealth.data;
    } catch (error: any) {
      results.auth = { status: 'unhealthy', error: error.message };
    }

    try {
      const patientHealth = await this.patientApi.get('/health');
      results.patient = patientHealth.data;
    } catch (error: any) {
      results.patient = { status: 'unhealthy', error: error.message };
    }

    try {
      const ragHealth = await this.ragApi.get('/health');
      results.rag = ragHealth.data;
    } catch (error: any) {
      results.rag = { status: 'unhealthy', error: error.message };
    }

    return results;
  }

  private handleError(error: any): never {
    const apiError: ApiError = {
      detail: error.response?.data?.detail || error.message || 'An error occurred',
      status_code: error.response?.status || 500,
    };
    throw apiError;
  }
}

// Create singleton instance
export const api = new ApiClient();

// Export individual service APIs for direct access if needed
export const authApi = (api as any).authApi;
export const patientApi = (api as any).patientApi;
export const ragApi = (api as any).ragApi;