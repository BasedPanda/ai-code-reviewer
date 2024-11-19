import React from 'react';
import { Card, Loading, Button } from '../common';
import { Clock, GitPullRequest, Check, AlertCircle } from 'lucide-react';

interface PullRequest {
  id: number;
  title: string;
  number: number;
  createdAt: string;
  status: 'pending' | 'reviewing' | 'completed' | 'failed';
  author: {
    login: string;
    avatarUrl: string;
  };
  repository: {
    name: string;
  };
}

interface PRListProps {
  isLoading?: boolean;
  pullRequests: PullRequest[];
  onSelectPR: (pr: PullRequest) => void;
}

const PRList: React.FC<PRListProps> = ({ 
  isLoading = false, 
  pullRequests = [],
  onSelectPR 
}) => {
  const getStatusIcon = (status: PullRequest['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="text-yellow-500" size={20} />;
      case 'reviewing':
        return <GitPullRequest className="text-blue-500" size={20} />;
      case 'completed':
        return <Check className="text-green-500" size={20} />;
      case 'failed':
        return <AlertCircle className="text-red-500" size={20} />;
    }
  };

  const getStatusText = (status: PullRequest['status']) => {
    const statusMap = {
      pending: 'Awaiting Review',
      reviewing: 'In Review',
      completed: 'Review Complete',
      failed: 'Review Failed'
    };
    return statusMap[status];
  };

  if (isLoading) {
    return (
      <Card className="h-full">
        <Loading text="Loading pull requests..." />
      </Card>
    );
  }

  return (
    <Card 
      title="Pull Requests" 
      subtitle="Recent pull requests pending review"
      className="h-full"
      footer={
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">
            Showing {pullRequests.length} pull requests
          </span>
          <Button variant="ghost" size="sm">
            View All
          </Button>
        </div>
      }
    >
      <div className="divide-y divide-gray-200 -my-4">
        {pullRequests.map((pr) => (
          <div 
            key={pr.id}
            className="py-4 cursor-pointer hover:bg-gray-50 px-4 -mx-4"
            onClick={() => onSelectPR(pr)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <img 
                  src={pr.author.avatarUrl} 
                  alt={pr.author.login}
                  className="w-8 h-8 rounded-full"
                />
                <div>
                  <h4 className="text-sm font-medium text-gray-900">
                    {pr.repository.name} #{pr.number}
                  </h4>
                  <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                    {pr.title}
                  </p>
                  <div className="mt-2 flex items-center space-x-2">
                    <span className="text-xs text-gray-500">
                      by {pr.author.login}
                    </span>
                    <span className="text-xs text-gray-500">•</span>
                    <span className="text-xs text-gray-500">
                      {new Date(pr.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(pr.status)}
                <span className="text-sm text-gray-600">
                  {getStatusText(pr.status)}
                </span>
              </div>
            </div>
          </div>
        ))}
        
        {pullRequests.length === 0 && (
          <div className="py-12 text-center">
            <GitPullRequest className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No pull requests
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              No pull requests are currently pending review.
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default PRList;