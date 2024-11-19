// services/websocket.ts

import { EventEmitter } from 'events';

interface WebSocketMessage {
  type: string;
  payload: any;
}

interface WebSocketServiceOptions {
  url: string;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

class WebSocketService extends EventEmitter {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private reconnectAttempts: number;
  private reconnectInterval: number;
  private reconnectCount = 0;
  private reconnectTimeoutId?: NodeJS.Timeout;
  private url: string;

  private constructor(options: WebSocketServiceOptions) {
    super();
    this.url = options.url;
    this.reconnectAttempts = options.reconnectAttempts || 5;
    this.reconnectInterval = options.reconnectInterval || 3000;
  }

  public static getInstance(options: WebSocketServiceOptions): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService(options);
    }
    return WebSocketService.instance;
  }

  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      this.ws = new WebSocket(this.url);
      this.setupEventListeners();
    } catch (error) {
      this.emit('error', error);
      this.attemptReconnect();
    }
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.emit('connected');
      this.reconnectCount = 0;
    };

    this.ws.onclose = () => {
      this.emit('disconnected');
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      this.emit('error', error);
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        this.emit('error', new Error('Failed to parse WebSocket message'));
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'pr_update':
        this.emit('prUpdate', message.payload);
        break;
      case 'new_suggestion':
        this.emit('newSuggestion', message.payload);
        break;
      case 'new_comment':
        this.emit('newComment', message.payload);
        break;
      case 'suggestion_status_change':
        this.emit('suggestionStatusChange', message.payload);
        break;
      default:
        this.emit('message', message);
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectCount < this.reconnectAttempts) {
      this.reconnectTimeoutId = setTimeout(() => {
        this.reconnectCount++;
        this.connect();
      }, this.reconnectInterval);
    } else {
      this.emit('error', new Error('Maximum reconnection attempts reached'));
    }
  }

  public disconnect(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public send(type: string, payload: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = { type, payload };
      this.ws.send(JSON.stringify(message));
    } else {
      this.emit('error', new Error('WebSocket is not connected'));
    }
  }

  // Convenience methods for specific message types
  public subscribeToPR(prId: number): void {
    this.send('subscribe_pr', { prId });
  }

  public unsubscribeFromPR(prId: number): void {
    this.send('unsubscribe_pr', { prId });
  }

  public sendComment(prId: number, comment: string, lineNumber?: number): void {
    this.send('new_comment', {
      prId,
      comment,
      lineNumber
    });
  }

  public markSuggestionStatus(
    suggestionId: string,
    status: 'accepted' | 'rejected'
  ): void {
    this.send('suggestion_status', {
      suggestionId,
      status
    });
  }

  public requestAnalysis(prId: number): void {
    this.send('request_analysis', { prId });
  }
}

// Create and export websocket service instance
const wsService = WebSocketService.getInstance({
  url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
});

// Export type for event handling
export type WebSocketEventMap = {
  connected: () => void;
  disconnected: () => void;
  error: (error: Error) => void;
  prUpdate: (payload: any) => void;
  newSuggestion: (payload: any) => void;
  newComment: (payload: any) => void;
  suggestionStatusChange: (payload: any) => void;
  message: (message: WebSocketMessage) => void;
};

export { wsService, WebSocketService };