type MessageCallback = (data: any) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private callbacks: Map<string, MessageCallback[]> = new Map();

  private heartbeatInterval: any = null;
  private reconnectTimeout: any = null;
  private currentUrl: string = '';

  connect(url: string) {
    this.currentUrl = url;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.socket) {
      console.log('Closing existing WebSocket connection...');
      this.socket.onopen = null;
      this.socket.onmessage = null;
      this.socket.onerror = null;
      this.socket.onclose = null;
      this.socket.close();
      this.socket = null;
    }

    console.log(`Connecting to WebSocket: ${url}`);
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log('WebSocket Connected');
      if (this.callbacks.has('connected')) {
        this.callbacks.get('connected')?.forEach(cb => cb({}));
      }
      this.startHeartbeat();
    };

    this.socket.onmessage = (event) => {
      try {
        const { event: eventName, data } = JSON.parse(event.data);
        if (this.callbacks.has(eventName)) {
          this.callbacks.get(eventName)?.forEach(cb => cb(data));
        }
      } catch (err) {
        console.error('Error parsing WS message:', err);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
      // Let onclose handle it
    };

    this.socket.onclose = () => {
      this.stopHeartbeat();
      if (this.callbacks.has('disconnected')) {
        this.callbacks.get('disconnected')?.forEach(cb => cb({}));
      }

      console.log('WebSocket disconnected. Reconnecting in 3s...');

      if (!this.reconnectTimeout) {
        this.reconnectTimeout = setTimeout(() => {
          this.reconnectTimeout = null;
          this.connect(this.currentUrl);
        }, 3000);
      }
    };
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ event: 'ping', data: {} }));
      }
    }, 15000); // Send ping every 15s
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  on(event: string, callback: MessageCallback) {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, []);
    }
    this.callbacks.get(event)?.push(callback);
  }

  off(event: string, callback: MessageCallback) {
    const eventCallbacks = this.callbacks.get(event);
    if (eventCallbacks) {
      this.callbacks.set(event, eventCallbacks.filter(cb => cb !== callback));
    }
  }

  clearListeners(event?: string) {
    if (event) {
      this.callbacks.delete(event);
    } else {
      this.callbacks.clear();
    }
  }
}

export const wsService = new WebSocketService();
