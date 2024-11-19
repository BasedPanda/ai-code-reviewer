import React from 'react';
import { Card, Button } from '../common';
import { MessageSquare, ThumbsUp, ThumbsDown } from 'lucide-react';

interface Suggestion {
  id: string;
  type: 'improvement' | 'security' | 'performance' | 'style';
  message: string;
  code: string;
  file: string;
  line: number;
  isAccepted?: boolean;
}

interface ReviewSuggestionsProps {
  suggestions: Suggestion[];
  onAcceptSuggestion: (id: string) => void;
  onRejectSuggestion: (id: string) => void;
}

const ReviewSuggestions: React.FC<ReviewSuggestionsProps> = ({
  suggestions,
  onAcceptSuggestion,
  onRejectSuggestion
}) => {
  const getTypeStyles = (type: Suggestion['type']) => {
    const styles = {
      improvement: {
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        label: 'Improvement'
      },
      security: {
        bg: 'bg-red-100',
        text: 'text-red-800',
        label: 'Security'
      },
      performance: {
        bg: 'bg-yellow-100',
        text: 'text-yellow-800',
        label: 'Performance'
      },
      style: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        label: 'Style'
      }
    };
    return styles[type];
  };

  return (
    <Card 
      title="Review Suggestions" 
      subtitle="AI-generated suggestions for your code"
      className="h-full"
    >
      <div className="space-y-4">
        {suggestions.map((suggestion) => {
          const typeStyle = getTypeStyles(suggestion.type);
          
          return (
            <div 
              key={suggestion.id}
              className="p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className={`
                    inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${typeStyle.bg} ${typeStyle.text}
                  `}>
                    {typeStyle.label}
                  </span>
                  <p className="mt-2 text-sm text-gray-900">
                    {suggestion.message}
                  </p>
                  <div className="mt-2 p-2 bg-gray-50 rounded text-xs font-mono overflow-x-auto">
                    {suggestion.code}
                  </div>
                  <p className="mt-2 text-xs text-gray-500">
                    {suggestion.file}:{suggestion.line}
                  </p>
                </div>

                {suggestion.isAccepted === undefined ? (
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onAcceptSuggestion(suggestion.id)}
                      className="text-green-600 hover:text-green-700"
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRejectSuggestion(suggestion.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <span className={`
                    text-sm font-medium
                    ${suggestion.isAccepted ? 'text-green-600' : 'text-red-600'}
                  `}>
                    {suggestion.isAccepted ? 'Accepted' : 'Rejected'}
                  </span>
                )}
              </div>
            </div>
          );
        })}

        {suggestions.length === 0 && (
          <div className="py-12 text-center">
            <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No suggestions
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              No review suggestions available at the moment.
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ReviewSuggestions;