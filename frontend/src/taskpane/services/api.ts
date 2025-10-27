import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// API Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// ============ WORD API ============

export interface RewriteRequest {
  text: string;
  instruction: string;
  style?: 'formal' | 'casual' | 'academic' | 'persuasive' | 'concise';
  context?: string;
  use_context?: boolean;
}

export interface AnalyzeRequest {
  text: string;
  analysis_type: 'general' | 'style' | 'grammar' | 'readability' | 'sentiment';
  include_suggestions?: boolean;
}

export interface SummarizeRequest {
  text: string;
  summary_type: 'concise' | 'detailed' | 'bullets';
  max_length?: number;
  document_id?: string;
}

export interface GenerateRequest {
  prompt: string;
  context?: string;
  style?: string;
  length?: 'short' | 'medium' | 'long';
  document_id?: string;
}

export interface QueryRequest {
  query: string;
  document_id?: string;
  max_results?: number;
  bypass_cache?: boolean;
}

export interface DocumentUploadRequest {
  content: string;
  filename: string;
  document_type: 'word' | 'excel';
  metadata?: Record<string, any>;
}

// Word LLM API
export const wordAPI = {
  rewrite: (data: RewriteRequest) =>
    apiClient.post('/api/llm/rewrite', data),

  analyze: (data: AnalyzeRequest) =>
    apiClient.post('/api/llm/analyze', data),

  summarize: (data: SummarizeRequest) =>
    apiClient.post('/api/llm/summarize', data),

  generate: (data: GenerateRequest) =>
    apiClient.post('/api/llm/generate', data),

  grammarCheck: (text: string) =>
    apiClient.post('/api/llm/grammar-check', { text }),

  paraphrase: (text: string, num_variations: number = 3) =>
    apiClient.post('/api/llm/paraphrase', { text, num_variations }),

  compare: (document_id_1: string, document_id_2: string, comparison_type: string = 'content') =>
    apiClient.post('/api/llm/compare', { document_id_1, document_id_2, comparison_type }),

  extractOutline: (text: string) =>
    apiClient.post('/api/llm/extract-outline', { text })
};

// Word Query API
export const queryAPI = {
  search: (data: QueryRequest) =>
    apiClient.post('/api/query/search', data),

  ask: (data: QueryRequest) =>
    apiClient.post('/api/query/ask', data)
};

// Document Management API
export const documentAPI = {
  upload: (data: DocumentUploadRequest) =>
    apiClient.post('/api/documents/upload', data),

  list: (document_type?: 'word' | 'excel') =>
    apiClient.get('/api/documents/list', { params: { document_type } }),

  get: (document_id: string) =>
    apiClient.get(`/api/documents/${document_id}`),

  delete: (document_id: string) =>
    apiClient.delete(`/api/documents/${document_id}`),

  search: (query: string, document_type?: string) =>
    apiClient.post('/api/documents/search', { query, document_type })
};

// Context API
export const contextAPI = {
  extract: (text: string, context_type: 'local' | 'section' | 'global' = 'local') =>
    apiClient.post('/api/context/extract', { text, context_type }),

  getDocumentContext: (document_id: string) =>
    apiClient.get(`/api/context/document/${document_id}`),

  clearCache: () =>
    apiClient.post('/api/context/clear-cache')
};

// ============ EXCEL API ============

export interface ExcelRange {
  values: any[][];
  sheet_name: string;
  address: string;
  workbook_name?: string;
  has_headers?: boolean;
}

export interface FormulaRequest {
  description: string;
  context: ExcelRange;
  reference_columns?: string[];
}

export interface DataQueryRequest {
  query: string;
  context: ExcelRange;
  query_type?: 'insight' | 'formula' | 'visualization';
}

export interface ChartRecommendationRequest {
  context: ExcelRange;
  purpose?: string;
}

// Excel Query API
export const excelQueryAPI = {
  query: (data: DataQueryRequest) =>
    apiClient.post('/api/excel/query', data),

  formula: (data: FormulaRequest) =>
    apiClient.post('/api/excel/formula', data),

  insight: (context: ExcelRange) =>
    apiClient.post('/api/excel/insight', { context }),

  chart: (data: ChartRecommendationRequest) =>
    apiClient.post('/api/excel/chart', data)
};

// Excel LLM API
export const excelLLMAPI = {
  analyzeComprehensive: (context: ExcelRange, include_correlations: boolean = true, include_predictions: boolean = false) =>
    apiClient.post('/api/excel/llm/analyze-comprehensive', {
      context,
      include_correlations,
      include_predictions
    }),

  generateReport: (context: ExcelRange, report_type: 'executive' | 'detailed' | 'technical' = 'executive', include_charts: boolean = true) =>
    apiClient.post('/api/excel/llm/generate-report', {
      context,
      report_type,
      include_charts
    }),

  suggestTransformations: (context: ExcelRange) =>
    apiClient.post('/api/excel/llm/suggest-transformations', { context }),

  predictTrends: (context: ExcelRange, target_column: string, periods: number = 5) =>
    apiClient.post('/api/excel/llm/predict-trends', {
      context,
      target_column,
      periods
    }),

  compareDatasets: (dataset1: ExcelRange, dataset2: ExcelRange, comparison_type: string = 'comprehensive') =>
    apiClient.post('/api/excel/llm/compare-datasets', {
      dataset1,
      dataset2,
      comparison_type
    }),

  explainData: (context: ExcelRange, focus?: 'summary' | 'patterns' | 'quality' | 'business') =>
    apiClient.post('/api/excel/llm/explain-data', { context, focus })
};

// Health Check
export const healthAPI = {
  check: () => apiClient.get('/health')
};

export default apiClient;
