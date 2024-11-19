// App.tsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from './components/common';
import useGitHubAuth from './hooks/useGitHubAuth';
import { AlertCircle, Github } from 'lucide-react';

// Lazy load components
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Review = React.lazy(() => import('./pages/Review'));
const Settings = React.lazy(() => import('./pages/Settings'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

const App: React.FC = () => {
  const { isAuthenticated, user, loading, error, login } = useGitHubAuth();

  // Loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Authentication error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Alert variant="destructive" className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Login page
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
        <div className="max-w-md w-full space-y-8 text-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              AI Code Review Assistant
            </h1>
            <p className="text-gray-600">
              Enhance your code reviews with AI-powered insights and suggestions
            </p>
          </div>
          
          <Button
            onClick={login}
            size="lg"
            className="w-full"
          >
            <Github className="mr-2 h-5 w-5" />
            Continue with GitHub
          </Button>
          
          <p className="text-sm text-gray-500">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    );
  }

  // Main application layout
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation Header */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                {/* Logo */}
                <div className="flex-shrink-0 flex items-center">
                  <span className="text-xl font-bold text-gray-900">
                    Code Review AI
                  </span>
                </div>
                
                {/* Navigation Links */}
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <NavLink to="/">Dashboard</NavLink>
                  <NavLink to="/reviews">Reviews</NavLink>
                  <NavLink to="/settings">Settings</NavLink>
                </div>
              </div>

              {/* User Menu */}
              <div className="flex items-center">
                <div className="flex items-center space-x-3">
                  <img
                    src={user?.avatarUrl}
                    alt={user?.name}
                    className="h-8 w-8 rounded-full"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    {user?.name}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <React.Suspense
            fallback={
              <div className="flex items-center justify-center h-64">
                <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/reviews/:prId" element={<Review />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
          </React.Suspense>
        </main>
      </div>
    </Router>
  );
};

// Navigation Link Component
const NavLink: React.FC<{ to: string; children: React.ReactNode }> = ({
  to,
  children
}) => {
  const isActive = window.location.pathname === to;
  
  return (
    <a
      href={to}
      className={`
        inline-flex items-center px-1 pt-1 text-sm font-medium
        ${isActive
          ? 'border-b-2 border-blue-500 text-gray-900'
          : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
        }
      `}
    >
      {children}
    </a>
  );
};

export default App;