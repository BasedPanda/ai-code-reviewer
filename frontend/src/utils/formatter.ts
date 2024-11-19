// utils/formatters.ts

// Date & Time formatting
export const formatDate = (date: string | Date, format: 'short' | 'long' = 'short'): string => {
    const d = new Date(date);
    
    if (format === 'short') {
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric'
      }).format(d);
    }
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(d);
  };
  
  export const formatRelativeTime = (date: string | Date): string => {
    const now = new Date();
    const then = new Date(date);
    const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000);
    
    if (diffInSeconds < 60) {
      return 'just now';
    }
    
    const intervals = {
      year: 31536000,
      month: 2592000,
      week: 604800,
      day: 86400,
      hour: 3600,
      minute: 60
    };
    
    for (const [unit, seconds] of Object.entries(intervals)) {
      const interval = Math.floor(diffInSeconds / seconds);
      if (interval >= 1) {
        return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
      }
    }
    
    return 'just now';
  };
  
  // Number formatting
  export const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };
  
  export const formatPercentage = (value: number, decimals: number = 1): string => {
    return `${(value * 100).toFixed(decimals)}%`;
  };
  
  // Time duration formatting
  export const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (hours < 24) {
      return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
    }
    
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    
    if (remainingHours === 0) {
      return `${days}d`;
    }
    
    return `${days}d ${remainingHours}h`;
  };
  
  // File size formatting
  export const formatFileSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };
  
  // Code diff formatting
  export const formatDiffStats = (additions: number, deletions: number): string => {
    const parts = [];
    if (additions > 0) parts.push(`+${additions}`);
    if (deletions > 0) parts.push(`-${deletions}`);
    return parts.join(', ');
  };
  
  // Repository name formatting
  export const formatRepoName = (fullName: string): { owner: string; name: string } => {
    const [owner, name] = fullName.split('/');
    return { owner, name };
  };
  
  // Branch name formatting
  export const formatBranchName = (branch: string): string => {
    return branch.replace(/^refs\/heads\//, '');
  };
  
  // Suggestion type formatting
  export const formatSuggestionType = (type: string): string => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };
  
  // Confidence score formatting
  export const formatConfidenceScore = (score: number): {
    label: string;
    color: string;
  } => {
    if (score >= 90) {
      return { label: 'High', color: 'text-green-600' };
    }
    if (score >= 70) {
      return { label: 'Medium', color: 'text-yellow-600' };
    }
    return { label: 'Low', color: 'text-red-600' };
  };
  
  // URL formatting
  export const formatGitHubUrl = (type: 'pr' | 'issue' | 'commit', repo: string, id: string | number): string => {
    const baseUrl = 'https://github.com';
    switch (type) {
      case 'pr':
        return `${baseUrl}/${repo}/pull/${id}`;
      case 'issue':
        return `${baseUrl}/${repo}/issues/${id}`;
      case 'commit':
        return `${baseUrl}/${repo}/commit/${id}`;
      default:
        return baseUrl;
    }
  };
  
  // Status formatting for display
  export const formatStatus = (status: string): {
    label: string;
    color: string;
    bgColor: string;
  } => {
    const statusMap: Record<string, { label: string; color: string; bgColor: string }> = {
      pending: {
        label: 'Pending',
        color: 'text-yellow-700',
        bgColor: 'bg-yellow-100'
      },
      reviewing: {
        label: 'In Review',
        color: 'text-blue-700',
        bgColor: 'bg-blue-100'
      },
      completed: {
        label: 'Completed',
        color: 'text-green-700',
        bgColor: 'bg-green-100'
      },
      failed: {
        label: 'Failed',
        color: 'text-red-700',
        bgColor: 'bg-red-100'
      }
    };
  
    return statusMap[status.toLowerCase()] || {
      label: status,
      color: 'text-gray-700',
      bgColor: 'bg-gray-100'
    };
  };