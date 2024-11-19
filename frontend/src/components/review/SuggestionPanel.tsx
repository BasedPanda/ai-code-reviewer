import React, { useState } from 'react';
import { Card, Button } from '../common';
import { MessageCircle, Check, X, ThumbsUp, ThumbsDown } from 'lucide-react';

interface Suggestion {
  id: string;
  type: 'improvement' | 'security' | 'performance' | 'style';
  message: string;
  originalCode: string;
  suggestedCode: string;
  explanation: string;
  status?: 'accepted' | 'rejected';
  confidence: number;
}

interface SuggestionPanelProps {
  suggestions: Suggestion[];
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  selectedFileLocation?: {
    file: string;
    line: number;
  };
}

const SuggestionPanel: React.FC<SuggestionPanelProps> = ({
  suggestions,
  onAccept,
  onReject,
  selectedFileLocation
}) => {
  const [expandedSuggestion, setExpandedSuggestion] = useState<string | null>(null);

  const getTypeColor = (type: Suggestion['type']) => {
    const colors = {
      improvement: 'text-blue-600 bg-blue-50 border-blue-200',
      security: 'text-red-600 bg-red-50 border-red-200',
      performance: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      style: 'text-green-600 bg-green-50 border-green-200'
    };
    return colors[type];
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card 
      title="AI Suggestions"
      subtitle={selectedFileLocation ? 
        `Reviewing ${selectedFileLocation.file}:${selectedFileLocation.line}` :
        "Select a line in the diff to see specific suggestions"
      }
      className="h-full overflow-hidden flex flex-col"
    >
      <div className="overflow-y-auto flex-grow">
        {suggestions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 py-8">
            <MessageCircle className="h-12 w-12 mb-4" />
            <p className="text-sm">No suggestions for this selection</p>
          </div>
        ) : (
          <div className="space-y-4">
            {suggestions.map((suggestion) => (
              <div 
                key={suggestion.id}
                className="border rounded-lg overflow-hidden"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`
                        px-2 py-1 text-xs font-medium rounded-full
                        ${getTypeColor(suggestion.type)}
                      `}>
                        {suggestion.type.charAt(0).toUpperCase() + suggestion.type.slice(1)}
                      </span>
                      <span className={`
                        text-sm font-medium
                        ${getConfidenceColor(suggestion.confidence)}
                      `}>
                        {suggestion.confidence}% confidence
                      </span>
                    </div>
                    {suggestion.status ? (
                      <span className={`
                        text-sm font-medium
                        ${suggestion.status === 'accepted' ? 'text-green-600' : 'text-red-600'}
                      `}>
                        {suggestion.status.charAt(0).toUpperCase() + suggestion.status.slice(1)}
                      </span>
                    ) : (
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onAccept(suggestion.id)}
                          className="text-green-600 hover:text-green-700"
                        >
                          <ThumbsUp className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onReject(suggestion.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <ThumbsDown className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>

                  <p className="mt-2 text-sm text-gray-900">
                    {suggestion.message}
                  </p>

                  <button
                    className="mt-2 text-sm text-blue-600 hover:text-blue-700"
                    onClick={() => setExpandedSuggestion(
                      expandedSuggestion === suggestion.id ? null : suggestion.id
                    )}
                  >
                    {expandedSuggestion === suggestion.id ? 'Show less' : 'Show more'}
                  </button>

                  {expandedSuggestion === suggestion.id && (
                    <div className="mt-4 space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                          Original Code
                        </h4>
                        <pre className="p-2 bg-gray-50 rounded text-sm overflow-x-auto">
                          {suggestion.originalCode}
                        </pre>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                          Suggested Code
                        </h4>
                        <pre className="p-2 bg-gray-50 rounded text-sm overflow-x-auto">
                          {suggestion.suggestedCode}
                        </pre>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">
                          Explanation
                        </h4>
                        <p className="text-sm text-gray-700">
                          {suggestion.explanation}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default SuggestionPanel;