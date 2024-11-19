// hooks/useWebSocket.ts

import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  payload: any;
}

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  autoReconnect?: boolean;
}

const useWebSocket = ({
  url,
  onMessage,
  reconnectAttempts = 5,
  reconnectInterval = 3000,
  autoReconnect = true
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);
  const reconnectTimeoutId = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectCount.current = 0;
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        if (autoReconnect && reconnectCount.current < reconnectAttempts) {
          reconnectTimeoutId.current = setTimeout(() => {
            reconnectCount.current += 1;
            connect();
          }, reconnectInterval);
        }
      };

      ws.current.onerror = (event) => {
        setError(new Error('WebSocket error occurred'));
      };

      ws.current.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(data);
        } catch (err) {
          setError(new Error('Failed to parse WebSocket message'));
        }
      };
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to connect to WebSocket'));
    }
  }, [url, onMessage, autoReconnect, reconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutId.current) {
      clearTimeout(reconnectTimeoutId.current);
    }
    
    if (ws.current) {
      ws.current.close();
    }
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (ws.current && isConnected) {
      ws.current.send(JSON.stringify(message));
    } else {
      setError(new Error('WebSocket is not connected'));
    }
  }, [isConnected]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    error,
    sendMessage,
    reconnect: connect,
    disconnect
  };
};

export default useWebSocket;