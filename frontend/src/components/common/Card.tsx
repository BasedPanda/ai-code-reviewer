import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  className?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  className = '',
  children,
  footer,
  onClick
}) => {
  const cardClasses = `
    bg-white rounded-lg shadow-sm border border-gray-200
    hover:shadow-md transition-shadow duration-200
    ${onClick ? 'cursor-pointer' : ''}
    ${className}
  `;

  return (
    <div 
      className={cardClasses}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
    >
      {(title || subtitle) && (
        <div className="p-4 border-b border-gray-200">
          {title && (
            <h3 className="text-lg font-medium text-gray-900">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">
              {subtitle}
            </p>
          )}
        </div>
      )}
      
      <div className="p-4">
        {children}
      </div>

      {footer && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 rounded-b-lg">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;