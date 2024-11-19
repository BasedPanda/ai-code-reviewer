import React from 'react';
import { Card, Loading } from '../common';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Clock, GitPullRequest, Check, AlertCircle } from 'lucide-react';

interface AnalyticsSummaryProps {
  isLoading?: boolean;
  data?: {
    totalReviews: number;
    averageTimeToReview: number;
    successRate: number;
    recentActivity: {
      date: string;
      reviews: number;
      suggestions: number;
    }[];
  };
}

const AnalyticsSummary: React.FC<AnalyticsSummaryProps> = ({
  isLoading = false,
  data
}) => {
  const stats = [
    {
      name: 'Total Reviews',
      value: data?.totalReviews || 0,
      icon: GitPullRequest,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100'
    },
    {
      name: 'Avg. Review Time',
      value: data ? `${Math.round(data.averageTimeToReview)}m` : '0m',
      icon: Clock,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-100'
    },
    {
      name: 'Success Rate',
      value: data ? `${Math.round(data.successRate)}%` : '0%',
      icon: Check,
      color: 'text-green-500',
      bgColor: 'bg-green-100'
    }
  ];

  if (isLoading) {
    return (
      <Card className="h-full">
        <Loading text="Loading analytics..." />
      </Card>
    );
  }

  return (
    <Card 
      title="Analytics Summary" 
      subtitle="Overview of review performance"
      className="h-full"
    >
      <div className="grid grid-cols-3 gap-4 mb-6">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="p-4 rounded-lg border border-gray-200"
          >
            <div className="flex items-center space-x-2">
              <div className={`p-2 rounded-full ${stat.bgColor}`}>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {stat.name}
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stat.value}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data?.recentActivity}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <XAxis 
              dataKey="date" 
              tickFormatter={(date) => new Date(date).toLocaleDateString()} 
            />
            <YAxis />
            <Tooltip />
            <Bar dataKey="reviews" fill="#3B82F6" name="Reviews" />
            <Bar dataKey="suggestions" fill="#10B981" name="Suggestions" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};

export default AnalyticsSummary;