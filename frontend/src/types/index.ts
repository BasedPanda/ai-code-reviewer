// types/index.ts

// GitHub related types
export interface GitHubUser {
    login: string;
    avatarUrl: string;
    name: string;
    email: string;
  }
  
  export interface Repository {
    id: number;
    name: string;
    fullName: string;
    private: boolean;
    description: string;
    defaultBranch: string;
  }
  
  // Pull Request related types
  export interface PullRequest {
    id: number;
    number: number;
    title: string;
    description: string;
    status: 'open' | 'closed' | 'merged';
    reviewStatus: 'pending' | 'reviewing' | 'completed' | 'failed';
    author: GitHubUser;
    repository: Repository;
    baseBranch: string;
    headBranch: string;
    createdAt: string;
    updatedAt: string;
    totalComments: number;
    totalSuggestions: number;
  }
  
  export interface PullRequestFile {
    filename: string;
    status: 'added' | 'modified' | 'removed';
    additions: number;
    deletions: number;
    changes: number;
    patch: string;
    language: string;
  }
  
  // Code Review related types
  export interface CodeComment {
    id: string;
    pullRequestId: number;
    author: GitHubUser;
    content: string;
    filename: string;
    lineNumber: number;
    position: number;
    createdAt: string;
    updatedAt: string;
    isAIGenerated: boolean;
    parentId?: string;
    reactions?: CommentReaction[];
  }
  
  export interface CommentReaction {
    id: string;
    user: GitHubUser;
    emoji: string;
    createdAt: string;
  }
  
  export interface CodeSuggestion {
    id: string;
    pullRequestId: number;
    type: 'improvement' | 'security' | 'performance' | 'style';
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
    filename: string;
    lineStart: number;
    lineEnd: number;
    originalCode: string;
    suggestedCode: string;
    explanation: string;
    status: 'pending' | 'accepted' | 'rejected';
    confidence: number;
    createdAt: string;
    updatedAt: string;
  }
  
  // Analytics related types
  export interface AnalyticsSummary {
    totalReviews: number;
    averageTimeToReview: number;
    suggestionsGenerated: number;
    suggestionsAccepted: number;
    suggestionsByType: {
      improvement: number;
      security: number;
      performance: number;
      style: number;
    };
    topIssues: {
      type: string;
      count: number;
      examples: string[];
    }[];
    recentActivity: ActivityPoint[];
  }
  
  export interface ActivityPoint {
    date: string;
    reviews: number;
    suggestions: number;
    comments: number;
  }
  
  // WebSocket related types
  export interface WebSocketMessage<T = any> {
    type: WebSocketMessageType;
    payload: T;
  }
  
  export type WebSocketMessageType =
    | 'pr_update'
    | 'new_suggestion'
    | 'new_comment'
    | 'suggestion_status_change'
    | 'analysis_complete'
    | 'error';
  
  // API Response types
  export interface ApiResponse<T> {
    data: T;
    meta?: {
      total?: number;
      page?: number;
      perPage?: number;
    };
  }
  
  export interface ApiError {
    message: string;
    code: string;
    details?: Record<string, any>;
  }
  
  // UI Component types
  export interface PaginationParams {
    page: number;
    perPage: number;
    total: number;
  }
  
  export interface SortParams {
    field: string;
    direction: 'asc' | 'desc';
  }
  
  export interface FilterParams {
    status?: PullRequest['status'][];
    reviewStatus?: PullRequest['reviewStatus'][];
    author?: string;
    repository?: string;
    dateRange?: {
      start: string;
      end: string;
    };
  }