// main.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { wsService } from './services/websocket';

// Initialize WebSocket service
wsService.connect();

// Handle WebSocket reconnection on visibility change
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    wsService.connect();
  }
});

// Create root element if it doesn't exist
const rootElement = document.getElementById('root') || document.createElement('div');
if (!rootElement.id) {
  rootElement.id = 'root';
  document.body.appendChild(rootElement);
}

// Add base styles
const style = document.createElement('style');
style.textContent = `
  @tailwind base;
  @tailwind components;
  @tailwind utilities;

  html, body {
    @apply antialiased;
    @apply bg-gray-50;
    @apply text-gray-900;
  }

  #root {
    @apply min-h-screen;
  }

  :root {
    --font-sans: 'Inter var', system-ui, -apple-system, BlinkMacSystemFont,
      'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif,
      'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
  }
`;
document.head.appendChild(style);

// Create and render root
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Application error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-xl font-bold text-red-600 mb-4">
              Something went wrong
            </h1>
            <p className="text-gray-600 mb-4">
              We're sorry, but something went wrong. Please try refreshing the page.
            </p>
            {this.state.error && (
              <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
                {this.state.error.toString()}
              </pre>
            )}
            <button
              onClick={() => window.location.reload()}
              className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Handle hot module replacement
if (import.meta.hot) {
  import.meta.hot.accept();
}