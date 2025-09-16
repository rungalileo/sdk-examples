import axios from 'axios';

const API_BASE_URL = 'http://localhost';

export const clientApi = {
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

  async getCurrentUser(token: string) {
    const response = await axios.get(`${API_BASE_URL}:8001/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  }
};
