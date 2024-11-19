import React from 'react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
  text?: string;
  className?: string;
}

const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  fullScreen = false,
  text = 'Loading...',
  className = ''
}) => {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const textStyles = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  const containerStyles = fullScreen
    ? 'fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50'
    : 'flex flex-col items-center justify-center';

  return (
    <div className={`${containerStyles} ${className}`}>
      <div className="relative">
        {/* Outer spinning circle */}
        <div
          className={`
            ${sizeStyles[size]}
            border-4 border-gray-200 border-t-blue-600
            rounded-full animate-spin
          `}
        />
        
        {/* Inner pulsing circle */}
        <div
          className={`
            absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2
            ${size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-4 w-4' : 'h-6 w-6'}
            bg-blue-600 rounded-full animate-pulse
          `}
        />
      </div>
      
      {text && (
        <p className={`
          mt-2 text-gray-600 font-medium
          ${textStyles[size]}
        `}>
          {text}
        </p>
      )}
    </div>
  );
};

export default Loading;