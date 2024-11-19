import React, { useState } from 'react';
import { Card } from '../common';
import { File, Plus, Minus, MessageSquare } from 'lucide-react';

interface DiffLine {
  type: 'added' | 'removed' | 'unchanged';
  content: string;
  lineNumber: {
    old: number | null;
    new: number | null;
  };
  hasComments?: boolean;
}

interface DiffFile {
  filename: string;
  language: string;
  hunks: {
    header: string;
    lines: DiffLine[];
  }[];
}

interface CodeDiffProps {
  files: DiffFile[];
  onLineClick?: (filename: string, lineNumber: number) => void;
  selectedLine?: {
    filename: string;
    lineNumber: number;
  };
}

const CodeDiff: React.FC<CodeDiffProps> = ({
  files,
  onLineClick,
  selectedLine
}) => {
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set(files.map(f => f.filename)));

  const toggleFile = (filename: string) => {
    setExpandedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(filename)) {
        newSet.delete(filename);
      } else {
        newSet.add(filename);
      }
      return newSet;
    });
  };

  const getLineBackground = (type: DiffLine['type'], isSelected: boolean) => {
    if (isSelected) return 'bg-blue-100';
    switch (type) {
      case 'added':
        return 'bg-green-50';
      case 'removed':
        return 'bg-red-50';
      default:
        return 'bg-white';
    }
  };

  const getLineNumber = (line: DiffLine) => {
    return (
      <div className="select-none text-gray-500 text-right pr-3 w-[4.5rem]">
        {line.lineNumber.old !== null && (
          <span className="inline-block w-[2rem]">{line.lineNumber.old}</span>
        )}
        {line.lineNumber.new !== null && (
          <span className="inline-block w-[2rem] ml-1">{line.lineNumber.new}</span>
        )}
      </div>
    );
  };

  return (
    <Card className="overflow-hidden">
      <div className="divide-y divide-gray-200">
        {files.map((file) => (
          <div key={file.filename} className="overflow-hidden">
            <div
              className="px-4 py-2 bg-gray-50 flex items-center justify-between cursor-pointer hover:bg-gray-100"
              onClick={() => toggleFile(file.filename)}
            >
              <div className="flex items-center space-x-2">
                <File className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-900">
                  {file.filename}
                </span>
                <span className="text-xs text-gray-500">
                  {file.language}
                </span>
              </div>
            </div>

            {expandedFiles.has(file.filename) && (
              <div className="overflow-x-auto">
                <pre className="text-sm leading-5">
                  {file.hunks.map((hunk, hunkIndex) => (
                    <div key={hunkIndex}>
                      <div className="bg-gray-100 px-4 py-1 text-gray-700 text-xs">
                        {hunk.header}
                      </div>
                      {hunk.lines.map((line, lineIndex) => {
                        const isSelected = selectedLine?.filename === file.filename && 
                          selectedLine?.lineNumber === line.lineNumber.new;
                        
                        return (
                          <div
                            key={`${hunkIndex}-${lineIndex}`}
                            className={`
                              flex hover:bg-gray-100 ${getLineBackground(line.type, isSelected)}
                              ${onLineClick && line.lineNumber.new ? 'cursor-pointer' : ''}
                            `}
                            onClick={() => {
                              if (onLineClick && line.lineNumber.new) {
                                onLineClick(file.filename, line.lineNumber.new);
                              }
                            }}
                          >
                            {getLineNumber(line)}
                            <div className="w-4 flex-shrink-0 text-gray-400">
                              {line.type === 'added' && <Plus className="h-4 w-4 text-green-600" />}
                              {line.type === 'removed' && <Minus className="h-4 w-4 text-red-600" />}
                            </div>
                            <div className="flex-grow px-2 whitespace-pre font-mono">
                              {line.content}
                            </div>
                            {line.hasComments && (
                              <div className="flex-shrink-0 px-2">
                                <MessageSquare className="h-4 w-4 text-blue-500" />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ))}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};

export default CodeDiff;