import axios from 'axios';

const API_BASE_URL = 'http://localhost';

export const serverApi = {
  async login(credentials: { username: string; password: string }) {
    // Create form data as the backend expects (username/password fields)
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await axios.post(`${API_BASE_URL}:8001/api/v1/auth/login`, formData, {
      headers: { 
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    return response.data;
  },

  async getCurrentUser(token: string) {
    const response = await axios.get(`${API_BASE_URL}:8001/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async getPatients(token: string) {
    const response = await axios.get(`${API_BASE_URL}:8002/api/v1/patients/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async getDocuments(token: string) {
    const response = await axios.get(`${API_BASE_URL}:8003/api/v1/documents/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async createPatient(token: string, patientData: any) {
    const response = await axios.post(`${API_BASE_URL}:8002/api/v1/patients/`, patientData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async updatePatient(token: string, patientId: string, patientData: any) {
    const response = await axios.put(`${API_BASE_URL}:8002/api/v1/patients/${patientId}`, patientData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async deletePatient(token: string, patientId: string) {
    await axios.delete(`${API_BASE_URL}:8002/api/v1/patients/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  },

  async createDocument(documentData: any, token: string) {
    const response = await axios.post(`${API_BASE_URL}:8003/api/v1/documents/`, documentData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async updateDocument(token: string, documentId: string, documentData: any) {
    const response = await axios.put(`${API_BASE_URL}:8003/api/v1/documents/${documentId}`, documentData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async deleteDocument(token: string, documentId: string) {
    await axios.delete(`${API_BASE_URL}:8003/api/v1/documents/${documentId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  },

  async getAllEmbeddingStatuses(token: string) {
    const response = await axios.get(`${API_BASE_URL}:8003/api/v1/documents/embedding-statuses`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async regenerateEmbeddings(documentId: number, token: string) {
    const response = await axios.post(`${API_BASE_URL}:8003/api/v1/documents/${documentId}/regenerate-embeddings`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async uploadDocument(formData: FormData, token: string) {
    const response = await axios.post(`${API_BASE_URL}:8003/api/v1/documents/upload`, formData, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  async searchDocuments(token: string, searchData: any) {
    const response = await axios.post(`${API_BASE_URL}:8003/api/v1/chat/search`, searchData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async askQuestion(token: string, questionData: any) {
    const response = await axios.post(`${API_BASE_URL}:8003/api/v1/chat/ask`, questionData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async getUsers(token: string) {
    const response = await axios.get(`${API_BASE_URL}:8001/api/v1/users/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async createUser(token: string, userData: any) {
    const response = await axios.post(`${API_BASE_URL}:8001/api/v1/users/`, userData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async updateUser(token: string, userId: string, userData: any) {
    const response = await axios.put(`${API_BASE_URL}:8001/api/v1/users/${userId}`, userData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async deleteUser(token: string, userId: string) {
    await axios.delete(`${API_BASE_URL}:8001/api/v1/users/${userId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }
};