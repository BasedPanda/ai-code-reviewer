// services/api.ts

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

class ApiService {
  private client: AxiosInstance;
  private static instance: ApiService;

  private constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json'
      },
      withCredentials: true // Important for cookie-based auth
    });

    // Add request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('token');
          window.dispatchEvent(new CustomEvent('auth:logout'));
        }
        return Promise.reject(error);
      }
    );
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  // Generic request method
  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.request(config);
      return response.data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unknown error occurred');
    }
  }

  // Convenience methods for different HTTP methods
  public async get<T>(url: string, config?: Omit<AxiosRequestConfig, 'method' | 'url'>) {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  public async post<T>(url: string, data?: any, config?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'>) {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  public async put<T>(url: string, data?: any, config?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'>) {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  public async delete<T>(url: string, config?: Omit<AxiosRequestConfig, 'method' | 'url'>) {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }

  // Specific API endpoints
  public async getPullRequests() {
    return this.get<PullRequest[]>('/api/pull-requests');
  }

  public async getPullRequestDetails(prId: number) {
    return this.get<PullRequestDetail>(`/api/pull-requests/${prId}`);
  }

  public async getReviewSuggestions(prId: number) {
    return this.get<ReviewSuggestion[]>(`/api/pull-requests/${prId}/suggestions`);
  }

  public async updateSuggestionStatus(suggestionId: string, status: 'accepted' | 'rejected') {
    return this.put<ReviewSuggestion>(`/api/suggestions/${suggestionId}`, { status });
  }

  public async addComment(prId: number, lineNumber: number, content: string) {
    return this.post<Comment>(`/api/pull-requests/${prId}/comments`, {
      lineNumber,
      content
    });
  }
}

// Export singleton instance
export const api = ApiService.getInstance();

// Types
export interface PullRequest {
  id: number;
  title: string;
  number: number;
  status: string;
  author: {
    login: string;
    avatarUrl: string;
  };
  createdAt: string;
  repository: {
    name: string;
  };
}

export interface PullRequestDetail extends PullRequest {
  description: string;
  diff: string;
  comments: Comment[];
  reviewers: string[];
}

export interface ReviewSuggestion {
  id: string;
  type: 'improvement' | 'security' | 'performance' | 'style';
  message: string;
  originalCode: string;
  suggestedCode: string;
  explanation: string;
  status?: 'accepted' | 'rejected';
  confidence: number;
}

export interface Comment {
  id: string;
  content: string;
  author: {
    login: string;
    avatarUrl: string;
    isAI?: boolean;
  };
  lineNumber: number;
  createdAt: string;
}