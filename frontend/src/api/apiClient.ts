import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface CVData {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  experience: any[];
  education: any[];
  languages: string[];
  raw_text: string;
}

export interface JobOffer {
  id: number;
  title: string;
  // Old format fields
  company?: string;
  location?: string;
  type?: string;
  description?: string;
  // New format fields
  organization?: string;
  locations_derived?: string[] | string;
  remote_derived?: string;
  employment_type?: string;
  description_text?: string;
  seniority?: string;
  // Common fields
  requirements?: string[];
  salary?: string;
  posted_date?: string;
  application_email: string;
  match_score?: number;
  similarity_score?: number;
}

export interface MotivationLetter {
  job_data: JobOffer;
  motivation_letter: string;
  match_explanation: {
    match_score: number;
    similarity_score: number;
    matching_skills: string[];
    job_title: string;
    company: string;
    explanation: string;
  };
}

export interface ApplicationResult {
  success: boolean;
  message: string;
  job_id: number;
  job_title: string;
  company: string;
  recipient_email: string;
}

// Upload CV
export const uploadCV = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/upload-cv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Get job offers
export const getJobOffers = async (filters?: {
  job_type?: string;
  location?: string;
  keyword?: string;
}) => {
  const params = new URLSearchParams();
  if (filters?.job_type) params.append('job_type', filters.job_type);
  if (filters?.location) params.append('location', filters.location);
  if (filters?.keyword) params.append('keyword', filters.keyword);

  const response = await apiClient.get(`/job-offers?${params.toString()}`);
  return response.data;
};

// Match offers with CV
export const matchOffers = async (cvData: CVData, filters?: {
  job_type?: string;
  location?: string;
  top_n?: number;
}) => {
  const response = await apiClient.post('/match-offers', {
    cv_data: cvData,
    job_type: filters?.job_type,
    location: filters?.location,
    top_n: filters?.top_n || 10,
  });

  return response.data;
};

// Generate motivation letter
export const generateMotivationLetter = async (
  cvData: CVData,
  jobId: number,
  customMessage?: string
) => {
  const response = await apiClient.post('/generate-letter', {
    cv_data: cvData,
    job_id: jobId,
    custom_message: customMessage || '',
  });

  return response.data;
};

// Submit application
export const submitApplication = async (
  cvData: CVData,
  jobId: number,
  motivationLetter: string
) => {
  const response = await apiClient.post('/apply', {
    cv_data: cvData,
    job_id: jobId,
    motivation_letter: motivationLetter,
  });

  return response.data;
};

// Get specific job
export const getJob = async (jobId: number) => {
  const response = await apiClient.get(`/job/${jobId}`);
  return response.data;
};

// Get application history
export const getApplicationHistory = async () => {
  const response = await apiClient.get('/applications');
  return response.data;
};

// OAuth API calls
export interface OAuthStatus {
  connected: boolean;
  email?: string;
  connected_at?: string;
  message: string;
}

export const getGoogleAuthStatus = async (): Promise<{ success: boolean; data: OAuthStatus }> => {
  const response = await apiClient.get('/auth/google/status');
  return response.data;
};

export const initiateGoogleAuth = (): void => {
  window.location.href = `${API_BASE_URL}/auth/google`;
};

export const disconnectGoogleAuth = async (): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.post('/auth/google/disconnect');
  return response.data;
};

export default apiClient;
