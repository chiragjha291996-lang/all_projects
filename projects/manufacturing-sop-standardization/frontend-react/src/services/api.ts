import axios from 'axios';
import { 
  UploadResponse, 
  AnalysisResult, 
  VectorDBStats, 
  ExactMatchStats, 
  ExactMatchResult, 
  SentenceMatchResult, 
  SemanticComparisonResult, 
  ProcessingStatus, 
  UploadVectorResponse 
} from '../types';

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds timeout for processing
});

export const apiService = {
  // Health check
  async checkHealth(): Promise<{ status: string; message: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Upload files to vector database (new async endpoint)
  async uploadFilesVector(files: FileList): Promise<UploadVectorResponse> {
    const formData = new FormData();
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    const response = await api.post('/upload_vector', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // Check processing status
  async getProcessingStatus(jobId: string): Promise<{ job_id: string; status: ProcessingStatus }> {
    const response = await api.get(`/processing_status/${jobId}`);
    return response.data;
  },

  // Get vector database statistics
  async getVectorStats(): Promise<{ message: string; stats: VectorDBStats }> {
    const response = await api.get('/vector_stats');
    return response.data;
  },

  // Get exact match statistics
  async getExactMatchStats(): Promise<{ message: string; stats: ExactMatchStats }> {
    const response = await api.get('/exact_match_stats');
    return response.data;
  },

  // Compare documents for exact matches (section-level)
  async compareExact(doc1: string, doc2: string): Promise<{ message: string; results: ExactMatchResult }> {
    const response = await api.post('/compare_exact', { doc1, doc2 });
    return response.data;
  },

  // Compare documents for exact matches (sentence-level)
  async compareSentenceLevel(doc1: string, doc2: string): Promise<{ message: string; results: SentenceMatchResult }> {
    const response = await api.post('/compare_sentence_level', { doc1, doc2 });
    return response.data;
  },

  // Compare documents semantically
  async compareSemantic(doc1: string, doc2: string): Promise<{ message: string; results: SemanticComparisonResult }> {
    const response = await api.post('/compare_semantic', { doc1, doc2 });
    return response.data;
  },

  // Get list of documents
  async getDocuments(): Promise<{ documents: string[] }> {
    const response = await api.get('/documents');
    return response.data;
  },

  // Get actual differences between documents
  async getDifferences(doc1: string, doc2: string): Promise<{ message: string; results: any }> {
    const response = await api.post('/get_differences', { doc1, doc2 });
    return response.data;
  },

  // Get page-by-page comparison with enhanced visuals
  async getPageComparison(doc1: string, doc2: string): Promise<{ message: string; results: any }> {
    const response = await api.post('/page_comparison', { doc1, doc2 });
    return response.data;
  },

  // Legacy endpoints (for backward compatibility)
  async uploadFiles(files: FileList): Promise<UploadResponse> {
    const formData = new FormData();
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async processDocuments(): Promise<AnalysisResult> {
    const response = await api.post('/process');
    return response.data;
  },

  async getUploadedFiles(): Promise<{ files: any[]; count: number }> {
    const response = await api.get('/files');
    return response.data;
  },

  async analyzeSimilarity(file1: string, file2: string): Promise<{ similarity_result: any }> {
    const response = await api.post('/similarity', {
      file1,
      file2,
    });
    return response.data;
  },
};

// Helper function to format file size
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Helper function to check if backend is available
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    await apiService.checkHealth();
    return true;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};
