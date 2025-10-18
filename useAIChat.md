import { useState, useEffect, useRef, useCallback } from 'react';
import { CrashLogger } from '../utils/crashLogger';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  done?: boolean;
  timestamp: string;
}

interface UseAIChatReturn {
  messages: Message[];
  isConnected: boolean;
  isTyping: boolean;
  sendMessage: (content: string) => boolean;
  reconnect: () => void;
}

export const useAIChat = (authToken: string | null): UseAIChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // WebSocket connection
  const connect = useCallback(() => {
    if (!authToken) {
      console.log('[useAIChat] No auth token provided');
      CrashLogger.warn('No auth token for WebSocket', 'useAIChat.connect');
      return;
    }

    // WebSocket URL for production backend
    const WS_URL = `wss://api.wealthwarriorshub.in/ws/chat?token=${authToken}`;

    try {
      wsRef.current = new WebSocket(WS_URL);

      wsRef.current.onopen = () => {
        console.log('[useAIChat] ✅ WebSocket Connected');
        setIsConnected(true);
        CrashLogger.info('WebSocket connected successfully', 'useAIChat.connect');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingMessage(data);
        } catch (error) {
          console.error('[useAIChat] Failed to parse message:', error);
          CrashLogger.log(error as Error, 'useAIChat.onmessage');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('[useAIChat] ❌ WebSocket Error:', error);
        setIsConnected(false);
        CrashLogger.warn('WebSocket error occurred', 'useAIChat.onerror');
      };

      wsRef.current.onclose = (event) => {
        console.log('[useAIChat] 🔌 WebSocket Disconnected');
        console.log('[useAIChat] Close code:', event.code);
        console.log('[useAIChat] Close reason:', event.reason || 'No reason provided');

        // Log common close codes for debugging
        const closeCodeMeaning = {
          1000: 'Normal closure',
          1001: 'Going away (e.g., server shutdown)',
          1002: 'Protocol error',
          1003: 'Unsupported data type',
          1006: 'Abnormal closure (no close frame)',
          1007: 'Invalid frame payload data',
          1008: 'Policy violation',
          1009: 'Message too big',
          1010: 'Missing extension',
          1011: 'Internal server error',
          1015: 'TLS handshake failure',
        };

        console.log('[useAIChat] Close meaning:', closeCodeMeaning[event.code as keyof typeof closeCodeMeaning] || 'Unknown code');
        CrashLogger.warn(`WebSocket closed with code ${event.code}: ${event.reason || 'No reason'}`, 'useAIChat.onclose');

        setIsConnected(false);

        // Auto-reconnect after 2 seconds
        console.log('Disconnected, reconnecting in 2s...');
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('[useAIChat] 🔄 Attempting to reconnect...');
          CrashLogger.info('WebSocket reconnecting', 'useAIChat.onclose');
          connect();
        }, 2000);
      };
    } catch (error) {
      console.error('[useAIChat] WebSocket connection error:', error);
      CrashLogger.log(error as Error, 'useAIChat.connect');
    }
  }, [authToken]);

  // Handle incoming messages
  const handleIncomingMessage = (data: any) => {
    console.log('[useAIChat] 📥 Received message type:', data.type);

    switch (data.type) {
      case 'connected':
        console.log('[useAIChat] ✅ Server confirmed connection:', data.message);
        break;

      case 'response':
        console.log('[useAIChat] 💬 AI response chunk - done:', data.done, 'length:', data.content?.length);
        setIsTyping(!data.done);

        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];

          // If last message is from AI and not done, update it
          if (lastMessage && lastMessage.sender === 'ai' && !lastMessage.done) {
            console.log('[useAIChat] 🔄 Updating existing AI message');
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...lastMessage,
              content: data.content,
              done: data.done,
              timestamp: data.timestamp,
            };
            return updated;
          } else {
            // Create new message
            console.log('[useAIChat] ✨ Creating new AI message');
            return [
              ...prev,
              {
                id: Date.now().toString(),
                sender: 'ai',
                content: data.content,
                done: data.done,
                timestamp: data.timestamp,
              },
            ];
          }
        });
        break;

      case 'error':
        console.error('[useAIChat] ❌ Server error:', data.message);
        CrashLogger.warn(`WebSocket server error: ${data.message}`, 'useAIChat.handleIncomingMessage');
        break;

      case 'pong':
        console.log('[useAIChat] 🏓 Pong received - connection alive');
        break;

      default:
        console.log('[useAIChat] ⚠️ Unknown message type:', data.type);
    }
  };

  // Send message
  const sendMessage = useCallback(
    (content: string): boolean => {
      // Log WebSocket state before sending
      const readyStateNames = {
        [WebSocket.CONNECTING]: 'CONNECTING',
        [WebSocket.OPEN]: 'OPEN',
        [WebSocket.CLOSING]: 'CLOSING',
        [WebSocket.CLOSED]: 'CLOSED',
      };

      const currentState = wsRef.current?.readyState;
      console.log('[useAIChat] 📤 Attempting to send message');
      console.log('[useAIChat] WebSocket state:', currentState !== undefined ? readyStateNames[currentState] : 'NULL');

      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.error('[useAIChat] ❌ WebSocket not connected - cannot send message');
        console.error('[useAIChat] Current state:', currentState !== undefined ? readyStateNames[currentState] : 'NULL');
        CrashLogger.warn('Attempted to send message without connection', 'useAIChat.sendMessage');
        return false;
      }

      // Add user message to UI immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        sender: 'user',
        content: content,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsTyping(true);

      // Send to server
      const payload = {
        type: 'message',
        content: content,
      };

      console.log('[useAIChat] 📨 Sending payload:', { type: payload.type, contentLength: content.length });

      try {
        wsRef.current.send(JSON.stringify(payload));
        console.log('[useAIChat] ✅ Message sent successfully');
        console.log('[useAIChat] WebSocket state after send:', readyStateNames[wsRef.current.readyState]);
        return true;
      } catch (error) {
        console.error('[useAIChat] ❌ Failed to send message:', error);
        console.error('[useAIChat] WebSocket state after error:', wsRef.current ? readyStateNames[wsRef.current.readyState] : 'NULL');
        CrashLogger.log(error as Error, 'useAIChat.sendMessage');
        return false;
      }
    },
    []
  );

  // Heartbeat (ping every 30 seconds)
  useEffect(() => {
    if (!isConnected) {
      console.log('[useAIChat] ⏸️ Heartbeat paused - not connected');
      return;
    }

    console.log('[useAIChat] 💓 Heartbeat started - ping every 30 seconds');

    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        try {
          console.log('[useAIChat] 🏓 Sending ping...');
          wsRef.current.send(JSON.stringify({ type: 'ping' }));
        } catch (error) {
          console.error('[useAIChat] ❌ Failed to send ping:', error);
        }
      } else {
        console.warn('[useAIChat] ⚠️ Cannot send ping - WebSocket not OPEN');
      }
    }, 30000);

    return () => {
      console.log('[useAIChat] 💓 Heartbeat stopped');
      clearInterval(interval);
    };
  }, [isConnected]);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    messages,
    isConnected,
    isTyping,
    sendMessage,
    reconnect: connect,
  };
};
