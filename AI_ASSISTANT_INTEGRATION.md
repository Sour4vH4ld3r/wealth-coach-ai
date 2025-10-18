# 🤖 AI Assistant Integration Guide
## React Native + Streaming Response + Typewriter Effect

> Complete implementation guide for integrating the Wealth Coach AI Assistant with real-time streaming responses and typewriter effect in React Native with React Native Paper.

---

## 📋 Table of Contents

1. [Backend API Overview](#backend-api-overview)
2. [WebSocket Connection](#websocket-connection)
3. [React Native Implementation](#react-native-implementation)
4. [Typewriter Effect](#typewriter-effect)
5. [Complete Example](#complete-example)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Backend API Overview

### WebSocket Endpoint

```
ws://192.168.1.3:8000/ws/chat?token=YOUR_JWT_TOKEN
```

### Authentication

Include JWT token as a query parameter when connecting to the WebSocket.

### Message Format

**Client → Server** (Send message):
```json
{
  "type": "message",
  "content": "What is my current balance?",
  "conversation_id": "optional-conversation-id"
}
```

**Server → Client** (Streaming response):
```json
{
  "type": "response",
  "content": "Your current balance is $6000.00",
  "done": false,
  "timestamp": "2025-10-17T10:00:00.000Z"
}
```

**Server → Client** (Final message):
```json
{
  "type": "response",
  "content": "Your current balance is $6000.00",
  "done": true,
  "timestamp": "2025-10-17T10:00:00.000Z"
}
```

---

## 🔌 WebSocket Connection

### 1. Install Dependencies

```bash
npm install react-native-paper
# WebSocket is built-in to React Native
```

### 2. WebSocket Hook (useAIChat.js)

Create a custom hook to manage WebSocket connection:

```javascript
import { useState, useEffect, useRef, useCallback } from 'react';

export const useAIChat = (authToken) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // WebSocket connection
  const connect = useCallback(() => {
    if (!authToken) {
      console.error('No auth token provided');
      return;
    }

    // Replace with your actual server IP
    const WS_URL = `ws://192.168.1.3:8000/ws/chat?token=${authToken}`;

    try {
      wsRef.current = new WebSocket(WS_URL);

      wsRef.current.onopen = () => {
        console.log('✅ WebSocket Connected');
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingMessage(data);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket Error:', error);
        setIsConnected(false);
      };

      wsRef.current.onclose = () => {
        console.log('🔌 WebSocket Disconnected');
        setIsConnected(false);

        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          connect();
        }, 3000);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }, [authToken]);

  // Handle incoming messages
  const handleIncomingMessage = (data) => {
    switch (data.type) {
      case 'connected':
        console.log('Connected:', data.message);
        break;

      case 'response':
        setIsTyping(!data.done);

        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];

          // If last message is from AI and not done, update it
          if (lastMessage && lastMessage.sender === 'ai' && !lastMessage.done) {
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
        console.error('Server error:', data.message);
        break;

      case 'pong':
        // Heartbeat response
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  };

  // Send message
  const sendMessage = useCallback(
    (content) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.error('WebSocket not connected');
        return false;
      }

      // Add user message to UI immediately
      const userMessage = {
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

      wsRef.current.send(JSON.stringify(payload));
      return true;
    },
    []
  );

  // Heartbeat (ping every 30 seconds)
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    return () => clearInterval(interval);
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
```

---

## 🎨 Typewriter Effect

### TypewriterText Component

Create a component with animated typewriter effect:

```javascript
import React, { useState, useEffect } from 'react';
import { Text } from 'react-native-paper';

export const TypewriterText = ({
  text,
  speed = 30, // ms per character
  onComplete,
  style
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    } else if (currentIndex === text.length && onComplete) {
      onComplete();
    }
  }, [currentIndex, text, speed, onComplete]);

  // Reset when text changes
  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
  }, [text]);

  return (
    <Text style={style}>
      {displayedText}
      {currentIndex < text.length && <Text>▌</Text>}
    </Text>
  );
};
```

---

## 📱 React Native Implementation

### Main Chat Screen Component

```javascript
import React, { useState, useRef } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  TextInput,
  Button,
  Card,
  Text,
  ActivityIndicator,
  Chip,
  Portal,
  Snackbar,
} from 'react-native-paper';
import { useAIChat } from './hooks/useAIChat';
import { TypewriterText } from './components/TypewriterText';

export const AIChatScreen = ({ authToken }) => {
  const [inputText, setInputText] = useState('');
  const [showSnackbar, setShowSnackbar] = useState(false);
  const flatListRef = useRef(null);

  const { messages, isConnected, isTyping, sendMessage } = useAIChat(authToken);

  const handleSend = () => {
    if (!inputText.trim()) return;

    const success = sendMessage(inputText.trim());

    if (success) {
      setInputText('');
      // Scroll to bottom after sending
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } else {
      setShowSnackbar(true);
    }
  };

  const renderMessage = ({ item }) => {
    const isUser = item.sender === 'user';

    return (
      <View
        style={[
          styles.messageContainer,
          isUser ? styles.userMessage : styles.aiMessage,
        ]}
      >
        <Card style={isUser ? styles.userCard : styles.aiCard}>
          <Card.Content>
            {isUser ? (
              <Text style={styles.messageText}>{item.content}</Text>
            ) : (
              // Use typewriter effect for AI messages
              item.done ? (
                <Text style={styles.messageText}>{item.content}</Text>
              ) : (
                <TypewriterText
                  text={item.content}
                  speed={20}
                  style={styles.messageText}
                />
              )
            )}
          </Card.Content>
        </Card>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={100}
    >
      {/* Connection Status */}
      <View style={styles.statusBar}>
        <Chip
          icon={isConnected ? 'check-circle' : 'alert-circle'}
          mode="flat"
          style={[
            styles.statusChip,
            isConnected ? styles.connectedChip : styles.disconnectedChip,
          ]}
        >
          {isConnected ? 'Connected' : 'Disconnected'}
        </Chip>
      </View>

      {/* Messages List */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        onContentSizeChange={() =>
          flatListRef.current?.scrollToEnd({ animated: true })
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={styles.emptyText}>
              👋 Hello! I'm your Wealth Coach AI Assistant.
            </Text>
            <Text variant="bodyMedium" style={styles.emptySubtext}>
              Ask me anything about your finances!
            </Text>
          </View>
        }
      />

      {/* Typing Indicator */}
      {isTyping && (
        <View style={styles.typingIndicator}>
          <ActivityIndicator size="small" />
          <Text variant="bodySmall" style={styles.typingText}>
            AI is typing...
          </Text>
        </View>
      )}

      {/* Input Area */}
      <View style={styles.inputContainer}>
        <TextInput
          mode="outlined"
          placeholder="Ask me anything..."
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          multiline
          maxLength={500}
          style={styles.input}
          right={
            <TextInput.Affix
              text={`${inputText.length}/500`}
              textStyle={styles.charCount}
            />
          }
          disabled={!isConnected || isTyping}
        />
        <Button
          mode="contained"
          onPress={handleSend}
          disabled={!inputText.trim() || !isConnected || isTyping}
          style={styles.sendButton}
          icon="send"
        >
          Send
        </Button>
      </View>

      {/* Snackbar for errors */}
      <Portal>
        <Snackbar
          visible={showSnackbar}
          onDismiss={() => setShowSnackbar(false)}
          duration={3000}
          action={{
            label: 'Dismiss',
            onPress: () => setShowSnackbar(false),
          }}
        >
          Failed to send message. Please check connection.
        </Snackbar>
      </Portal>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  statusBar: {
    padding: 8,
    alignItems: 'center',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  statusChip: {
    height: 28,
  },
  connectedChip: {
    backgroundColor: '#e8f5e9',
  },
  disconnectedChip: {
    backgroundColor: '#ffebee',
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    flexGrow: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: '600',
  },
  emptySubtext: {
    textAlign: 'center',
    color: '#666',
  },
  messageContainer: {
    marginBottom: 12,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
  },
  aiMessage: {
    alignSelf: 'flex-start',
  },
  userCard: {
    backgroundColor: '#1976d2',
  },
  aiCard: {
    backgroundColor: '#fff',
    elevation: 2,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    paddingLeft: 16,
    backgroundColor: '#fff',
  },
  typingText: {
    marginLeft: 8,
    color: '#666',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 8,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    marginRight: 8,
    maxHeight: 100,
  },
  charCount: {
    fontSize: 10,
    color: '#666',
  },
  sendButton: {
    marginBottom: 4,
  },
});
```

---

## 💡 Complete Example

### App.js Integration

```javascript
import React, { useState, useEffect } from 'react';
import { Provider as PaperProvider } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AIChatScreen } from './screens/AIChatScreen';

export default function App() {
  const [authToken, setAuthToken] = useState(null);

  useEffect(() => {
    // Load auth token from AsyncStorage
    loadAuthToken();
  }, []);

  const loadAuthToken = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      setAuthToken(token);
    } catch (error) {
      console.error('Failed to load auth token:', error);
    }
  };

  if (!authToken) {
    return null; // Show login screen
  }

  return (
    <PaperProvider>
      <AIChatScreen authToken={authToken} />
    </PaperProvider>
  );
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **WebSocket Connection Failed**

**Error**: `WebSocket connection to 'ws://192.168.1.3:8000/ws/chat' failed`

**Solutions**:
- ✅ Ensure backend server is running
- ✅ Verify IP address is correct (use `ifconfig` on Mac/Linux or `ipconfig` on Windows)
- ✅ Check firewall settings
- ✅ Make sure you're on the same network

#### 2. **Authentication Error (1008)**

**Error**: `WebSocket closed with code 1008: Authentication failed`

**Solutions**:
- ✅ Verify JWT token is valid
- ✅ Check token expiration
- ✅ Ensure token is passed correctly as query parameter

#### 3. **Messages Not Displaying**

**Solutions**:
- ✅ Check WebSocket `onmessage` handler
- ✅ Verify JSON parsing
- ✅ Check state updates in `handleIncomingMessage`

#### 4. **Typewriter Effect Too Fast/Slow**

**Solution**:
```javascript
<TypewriterText
  text={item.content}
  speed={50} // Adjust this value (ms per character)
/>
```

#### 5. **Auto-Scroll Not Working**

**Solution**:
```javascript
// Add delay to ensure render completes
setTimeout(() => {
  flatListRef.current?.scrollToEnd({ animated: true });
}, 100);
```

---

## 🚀 Performance Optimization

### 1. Memoize Message Components

```javascript
import React, { memo } from 'react';

const MessageItem = memo(({ item }) => {
  // ... render logic
}, (prevProps, nextProps) => {
  return prevProps.item.id === nextProps.item.id &&
         prevProps.item.content === nextProps.item.content &&
         prevProps.item.done === nextProps.item.done;
});
```

### 2. Limit Message History

```javascript
const MAX_MESSAGES = 50;

const handleIncomingMessage = (data) => {
  setMessages((prev) => {
    const updated = [...prev, newMessage];
    // Keep only last 50 messages
    return updated.slice(-MAX_MESSAGES);
  });
};
```

### 3. Debounce Scroll

```javascript
import { useMemo } from 'react';
import debounce from 'lodash.debounce';

const scrollToBottom = useMemo(
  () => debounce(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, 100),
  []
);
```

---

## 📊 Testing

### Test WebSocket Connection

```javascript
// Test in browser console or React Native debugger
const ws = new WebSocket('ws://192.168.1.3:8000/ws/chat?token=YOUR_TOKEN');

ws.onopen = () => console.log('✅ Connected');
ws.onmessage = (e) => console.log('📩 Message:', e.data);
ws.onerror = (e) => console.error('❌ Error:', e);

// Send test message
ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello AI!'
}));
```

---

## 🔐 Security Best Practices

1. **Never hardcode tokens** - Always load from secure storage
2. **Use HTTPS/WSS in production** - Encrypt WebSocket connections
3. **Validate server certificate** - Prevent man-in-the-middle attacks
4. **Implement timeout handling** - Close stale connections
5. **Rate limit client-side** - Prevent spam/abuse

---

## 📚 Additional Resources

- [React Native Paper Documentation](https://callstack.github.io/react-native-paper/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [React Native AsyncStorage](https://react-native-async-storage.github.io/async-storage/)

---

## 🎯 Next Steps

1. ✅ Implement AI service integration in backend
2. ✅ Add conversation history storage
3. ✅ Implement message reactions
4. ✅ Add file/image sharing
5. ✅ Support voice input
6. ✅ Add conversation export

---

**Created**: October 2025
**Last Updated**: October 17, 2025
**Version**: 1.0.0
