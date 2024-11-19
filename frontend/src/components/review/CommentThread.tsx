import React, { useState } from 'react';
import { Card, Button } from '../common';
import { Send, MessageSquare } from 'lucide-react';

interface Comment {
  id: string;
  author: {
    name: string;
    avatarUrl: string;
    isAI?: boolean;
  };
  content: string;
  timestamp: string;
}

interface CommentThreadProps {
  comments: Comment[];
  onAddComment: (content: string) => void;
  selectedLocation?: {
    file: string;
    line: number;
  };
}

const CommentThread: React.FC<CommentThreadProps> = ({
  comments,
  onAddComment,
  selectedLocation
}) => {
  const [newComment, setNewComment] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim()) {
      onAddComment(newComment.trim());
      setNewComment('');
    }
  };

  return (
    <Card 
      title="Discussion"
      subtitle={selectedLocation ? 
        `Comments for ${selectedLocation.file}:${selectedLocation.line}` :
        "Select a line in the diff to see comments"
      }
      className="h-full flex flex-col"
    >
      <div className="flex-grow overflow-y-auto mb-4">
        {comments.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 py-8">
            <MessageSquare className="h-12 w-12 mb-4" />
            <p className="text-sm">No comments yet</p>
            <p className="text-xs mt-2">Start the discussion by adding a comment</p>
          </div>
        ) : (
          <div className="space-y-4">
            {comments.map((comment) => (
              <div
                key={comment.id}
                className={`flex items-start space-x-3 ${
                  comment.author.isAI ? 'bg-blue-50 p-3 rounded-lg' : ''
                }`}
              >
                <img
                  src={comment.author.avatarUrl}
                  alt={comment.author.name}
                  className="w-8 h-8 rounded-full"
                />
                <div className="flex-grow">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-900">
                      {comment.author.name}
                    </span>
                    {comment.author.isAI && (
                      <span className="px-2 py-0.5 text-xs font-medium text-blue-600 bg-blue-100 rounded-full">
                        AI
                      </span>
                    )}
                    <span className="text-xs text-gray-500">
                      {new Date(comment.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="mt-1 text-sm text-gray-700 whitespace-pre-wrap">
                    {comment.content}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="mt-4 border-t pt-4">
        <div className="flex items-start space-x-2">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment..."
            className="flex-grow min-h-[80px] p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            disabled={!selectedLocation}
          />
          <Button
            type="submit"
            disabled={!newComment.trim() || !selectedLocation}
            className="flex-shrink-0"
          >
            <Send className="h-4 w-4 mr-2" />
            Send
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default CommentThread;