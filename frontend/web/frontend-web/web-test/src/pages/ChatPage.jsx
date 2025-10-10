import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Send,
  TrendingUp,
  LogOut,
  User,
  Bot,
  Loader2,
  ChevronDown,
} from 'lucide-react';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [user, setUser] = useState(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [skip, setSkip] = useState(0);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (!token) {
      navigate('/login');
      return;
    }
    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Load most recent session and its messages
    loadRecentSession();
  }, [navigate]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadRecentSession = async () => {
    try {
      const token = localStorage.getItem('token');

      // Get the most recent session
      const sessionsResponse = await fetch('/api/v1/chat/sessions?limit=1', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (sessionsResponse.ok) {
        const sessionsData = await sessionsResponse.json();
        if (sessionsData.sessions && sessionsData.sessions.length > 0) {
          const recentSession = sessionsData.sessions[0];
          setSessionId(recentSession.session_id);

          // Load messages for this session
          await loadMessages(recentSession.session_id, 0);
        }
      }
    } catch (error) {
      console.error('Error loading recent session:', error);
    }
  };

  const loadMessages = async (sid, skipCount) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `/api/v1/chat/sessions/${sid}/messages?skip=${skipCount}&limit=10`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();

        // Convert backend format to frontend format
        const formattedMessages = data.messages.map((msg) => ({
          id: `${msg.timestamp}-${msg.role}`,
          text: msg.content,
          sender: msg.role === 'user' ? 'user' : 'ai',
          timestamp: msg.timestamp,
        }));

        if (skipCount === 0) {
          // Initial load
          setMessages(formattedMessages);
        } else {
          // Prepend older messages
          setMessages((prev) => [...formattedMessages, ...prev]);
        }

        setHasMore(data.has_more);
        setSkip(skipCount + data.messages.length);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const loadMoreMessages = async () => {
    if (!sessionId || isLoadingMore || !hasMore) return;

    setIsLoadingMore(true);
    const previousScrollHeight = messagesContainerRef.current?.scrollHeight || 0;

    await loadMessages(sessionId, skip);

    // Maintain scroll position after loading
    setTimeout(() => {
      if (messagesContainerRef.current) {
        const newScrollHeight = messagesContainerRef.current.scrollHeight;
        messagesContainerRef.current.scrollTop = newScrollHeight - previousScrollHeight;
      }
      setIsLoadingMore(false);
    }, 100);
  };

  const handleScroll = () => {
    if (!messagesContainerRef.current) return;

    const { scrollTop } = messagesContainerRef.current;

    // Load more when scrolled to top
    if (scrollTop === 0 && hasMore && !isLoadingMore) {
      loadMoreMessages();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isStreaming) return;

    const userMessage = {
      id: `${Date.now()}-user`,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInputMessage('');
    setIsStreaming(true);

    const aiMessageId = `${Date.now()}-ai`;
    const aiMessage = {
      id: aiMessageId,
      text: '',
      sender: 'ai',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, aiMessage]);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/chat/message/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
          use_rag: true,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';
      let newSessionId = sessionId;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const parsed = JSON.parse(data);

              if (parsed.type === 'token' && parsed.content) {
                fullResponse += parsed.content;
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === aiMessageId ? { ...msg, text: fullResponse } : msg
                  )
                );
              } else if (parsed.type === 'session_id') {
                newSessionId = parsed.session_id;
                setSessionId(newSessionId);
              }
            } catch (e) {
              console.error('Parse error:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessageId
            ? { ...msg, text: 'Sorry, I encountered an error. Please try again.' }
            : msg
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="border-b border-white/10 bg-black/30 backdrop-blur-xl px-3 sm:px-6 py-3 sm:py-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-2 sm:space-x-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-r from-primary-500 to-purple-600 flex items-center justify-center glow">
            <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
          </div>
          <h1 className="text-base sm:text-xl font-semibold text-white">
            WealthWarriors AI
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center space-x-3 px-3 py-2 rounded-lg bg-white/5 border border-white/10">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-primary-500/20 to-purple-500/20 flex items-center justify-center border border-primary-500/30">
              <User className="w-4 h-4 text-primary-400" />
            </div>
            <div className="text-sm text-white font-medium">
              {user?.full_name || user?.email || 'User'}
            </div>
          </div>
          <Button onClick={handleLogout} variant="outline" size="sm">
            <LogOut className="w-4 h-4 sm:mr-2" />
            <span className="hidden sm:inline">Logout</span>
          </Button>
        </div>
      </div>

      {/* Messages Container */}
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-4 sm:space-y-6 scrollbar-thin"
      >
        {/* Load More Indicator */}
        {hasMore && (
          <div className="flex justify-center">
            <Button
              onClick={loadMoreMessages}
              disabled={isLoadingMore}
              variant="outline"
              size="sm"
              className="bg-black/30 backdrop-blur-sm"
            >
              {isLoadingMore ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4 mr-2 rotate-180" />
                  Load older messages
                </>
              )}
            </Button>
          </div>
        )}

        {/* Empty State */}
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center px-4">
            <div className="text-center max-w-md animate-fade-in">
              <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 mb-4 sm:mb-6 glow animate-float">
                <TrendingUp className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-2 sm:mb-3 text-shadow">
                Welcome to WealthWarriors AI
              </h2>
              <p className="text-sm sm:text-base text-white/70 mb-4 sm:mb-6">
                I'm here to help you with financial advice, investment strategies, budgeting tips, and more.
                Ask me anything about your finances!
              </p>
              <div className="space-y-2">
                <Button
                  onClick={() => setInputMessage('How should I start investing?')}
                  variant="outline"
                  className="w-full justify-start text-left h-auto py-3 text-sm sm:text-base"
                >
                  <span className="mr-2">💡</span>
                  How should I start investing?
                </Button>
                <Button
                  onClick={() => setInputMessage('Help me create a budget')}
                  variant="outline"
                  className="w-full justify-start text-left h-auto py-3 text-sm sm:text-base"
                >
                  <span className="mr-2">📊</span>
                  Help me create a budget
                </Button>
                <Button
                  onClick={() => setInputMessage('What is a good emergency fund size?')}
                  variant="outline"
                  className="w-full justify-start text-left h-auto py-3 text-sm sm:text-base"
                >
                  <span className="mr-2">🏦</span>
                  What is a good emergency fund size?
                </Button>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start gap-3 ${
                message.sender === 'user' ? 'justify-end' : ''
              } animate-slide-up`}
            >
              {message.sender === 'ai' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent-foreground flex items-center justify-center flex-shrink-0 shadow-lg ring-2 ring-primary/20">
                  <Bot className="w-5 h-5 text-primary-foreground" />
                </div>
              )}
              <Card
                className={`max-w-[85%] sm:max-w-[80%] ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground border-primary/50'
                    : 'bg-card/80 backdrop-blur-sm border-border'
                }`}
              >
                <CardContent className="p-3 sm:p-4">
                  {message.text ? (
                    <div className="whitespace-pre-wrap break-words text-sm sm:text-base leading-relaxed">
                      {message.text}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                      <span className="text-muted-foreground text-sm">Thinking...</span>
                    </div>
                  )}
                </CardContent>
              </Card>
              {message.sender === 'user' && (
                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0 ring-2 ring-secondary/50">
                  <User className="w-5 h-5 text-secondary-foreground" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-white/10 bg-black/30 backdrop-blur-xl p-3 sm:p-4 shadow-2xl">
        <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
          <div className="flex items-end gap-2 sm:gap-3">
            <div className="flex-1">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me about your finances..."
                disabled={isStreaming}
                className="h-11 sm:h-12 text-sm sm:text-base"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
              />
            </div>
            <Button
              type="submit"
              disabled={isStreaming || !inputMessage.trim()}
              size="icon"
              className="h-11 w-11 sm:h-12 sm:w-12 flex-shrink-0"
            >
              {isStreaming ? (
                <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
              ) : (
                <Send className="w-4 h-4 sm:w-5 sm:h-5" />
              )}
            </Button>
          </div>
          <p className="text-xs text-white/50 mt-2 text-center hidden sm:block">
            Press Enter to send, Shift + Enter for new line
          </p>
        </form>
      </div>
    </div>
  );
};

export default ChatPage;
