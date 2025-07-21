'use client';

import { useState, useRef, useEffect } from 'react';
import { FiUser, FiTrash2, FiMenu, FiX, FiBox, FiEdit2, FiCheck } from 'react-icons/fi';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tokens?: number;
  processingTime?: number;
}

interface ChatHistoryItem {
  id: string;
  title: string;
  created: string;
  messages: Message[];
}

interface GenerativeAIProps {
  apiBaseUrl?: string;
  userId?: string;
}

const CHAT_HISTORY_KEY = 'elimu_generative_ai_chats';

export default function GenerativeAI({ 
  apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  userId 
}: GenerativeAIProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'chat' | 'completion' | 'rag'>('chat');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(512);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [topics, setTopics] = useState<Array<{id: number, name: string}>>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [activeChatId, setActiveChatId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Load chat history from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(CHAT_HISTORY_KEY);
    if (stored) {
      const parsed: ChatHistoryItem[] = JSON.parse(stored);
      setChatHistory(parsed);
      if (parsed.length > 0) {
        setActiveChatId(parsed[0].id);
        setMessages(parsed[0].messages.map(m => ({ ...m, timestamp: new Date(m.timestamp) })));
      }
    }
  }, []);

  // Save chat history to localStorage
  useEffect(() => {
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(chatHistory));
  }, [chatHistory]);

  // Fetch available topics
  useEffect(() => {
    fetchTopics();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchTopics = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/list-topics`);
      if (response.ok) {
        const data = await response.json();
        setTopics(data.topics || []);
      }
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
  };

  const startNewChat = () => {
    const newId = Date.now().toString();
    const newChat: ChatHistoryItem = {
      id: newId,
      title: 'New Chat',
      created: new Date().toISOString(),
      messages: []
    };
    setChatHistory(prev => [newChat, ...prev]);
    setActiveChatId(newId);
    setMessages([]);
  };

  const saveCurrentChat = (msgs: Message[]) => {
    setChatHistory(prev => prev.map(chat =>
      chat.id === activeChatId
        ? { ...chat, messages: msgs, title: msgs[0]?.content?.slice(0, 30) || 'New Chat' }
        : chat
    ));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    saveCurrentChat(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      let response;
      if (mode === 'rag') {
        response = await fetch(`${apiBaseUrl}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            question: input.trim(),
            topic: selectedTopic
          })
        });
      } else if (mode === 'chat') {
        response = await fetch(`${apiBaseUrl}/llm/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            messages: newMessages.map(msg => ({
              role: msg.role,
              content: msg.content
            })),
            max_tokens: maxTokens,
            temperature: temperature
          })
        });
      } else {
        response = await fetch(`${apiBaseUrl}/llm/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            prompt: input.trim(),
            max_tokens: maxTokens,
            temperature: temperature
          })
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      let assistantContent = '';
      let tokens = 0;
      let processingTime = 0;

      if (mode === 'rag') {
        assistantContent = data.answer;
        if (data.sources && data.sources.length > 0) {
          assistantContent += '\n\n**Sources:**\n' + data.sources.join('\n');
        }
      } else if (mode === 'chat') {
        assistantContent = data.choices[0].message.content;
        tokens = data.usage?.total_tokens || 0;
      } else {
        assistantContent = data.choices[0].text;
        tokens = data.usage?.total_tokens || 0;
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date(),
        tokens,
        processingTime
      };

      const updatedMessages = [...newMessages, assistantMessage];
      setMessages(updatedMessages);
      saveCurrentChat(updatedMessages);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      const updatedMessages = [...messages, errorMessage];
      setMessages(updatedMessages);
      saveCurrentChat(updatedMessages);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    saveCurrentChat([]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const handleSelectChat = (id: string) => {
    const chat = chatHistory.find(c => c.id === id);
    if (chat) {
      setActiveChatId(id);
      setMessages(chat.messages.map(m => ({ ...m, timestamp: new Date(m.timestamp) })));
    }
    setSidebarOpen(false);
  };

  const handleDeleteChat = (id: string) => {
    setChatHistory(prev => prev.filter(c => c.id !== id));
    if (activeChatId === id) {
      if (chatHistory.length > 1) {
        const next = chatHistory.find(c => c.id !== id);
        if (next) {
          setActiveChatId(next.id);
          setMessages(next.messages.map(m => ({ ...m, timestamp: new Date(m.timestamp) })));
        } else {
          setActiveChatId('');
          setMessages([]);
        }
      } else {
        setActiveChatId('');
        setMessages([]);
      }
    }
  };

  const handleEditChatTitle = (id: string, title: string) => {
    setEditingChatId(id);
    setEditTitle(title);
  };

  const handleSaveChatTitle = (id: string) => {
    setChatHistory(prev => prev.map(chat =>
      chat.id === id ? { ...chat, title: editTitle.trim() || 'Untitled Chat' } : chat
    ));
    setEditingChatId(null);
    setEditTitle('');
  };

  // --- Redesigned UI with sidebar, avatars, and responsiveness ---
  return (
    <div className="flex h-screen max-w-5xl mx-auto bg-gradient-to-br from-green-50 via-white to-yellow-50 border border-green-100 rounded-xl shadow-lg md:flex-row flex-col relative">
      {/* Sidebar */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-0'} bg-white border-r border-green-100 rounded-l-xl flex flex-col overflow-hidden z-20 fixed md:static top-0 left-0 h-full md:h-auto ${sidebarOpen ? 'block' : 'hidden md:block'}`}>
        <div className="flex items-center justify-between p-4 border-b border-green-100 bg-gradient-to-r from-green-50 to-yellow-50">
          <div className="flex items-center gap-2">
            <div className="bg-green-100 rounded-full p-2">
              <FiUser className="text-green-700 w-6 h-6" />
            </div>
            <span className="font-semibold text-green-800 text-sm">Account</span>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="p-1 rounded hover:bg-green-50">
            <FiX className="w-5 h-5 text-green-700" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <button
            onClick={startNewChat}
            className="w-full py-2 bg-gradient-to-r from-green-200 to-yellow-100 text-green-900 font-semibold rounded-none border-b border-green-100 hover:bg-green-50 transition"
          >
            + New Chat
          </button>
          <div className="divide-y divide-green-50">
            {chatHistory.length === 0 && (
              <div className="text-center text-green-400 py-8">No chats yet</div>
            )}
            {chatHistory.map(chat => (
              <div
                key={chat.id}
                className={`flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-green-50 transition ${activeChatId === chat.id ? 'bg-green-100' : ''}`}
                onClick={() => handleSelectChat(chat.id)}
              >
                <div className="flex-1 min-w-0">
                  {editingChatId === chat.id ? (
                    <input
                      className="truncate font-medium text-green-900 text-sm bg-yellow-50 border border-yellow-200 rounded px-1 py-0.5 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                      value={editTitle}
                      onChange={e => setEditTitle(e.target.value)}
                      onBlur={() => handleSaveChatTitle(chat.id)}
                      onKeyDown={e => { if (e.key === 'Enter') handleSaveChatTitle(chat.id); }}
                      autoFocus
                    />
                  ) : (
                    <span className="truncate font-medium text-green-900 text-sm">{chat.title}</span>
                  )}
                  <div className="text-xs text-green-500 truncate">{new Date(chat.created).toLocaleString()}</div>
                </div>
                <button
                  onClick={e => { e.stopPropagation(); handleEditChatTitle(chat.id, chat.title); }}
                  className="ml-1 p-1 rounded hover:bg-yellow-50"
                  title="Rename chat"
                >
                  <FiEdit2 className="w-4 h-4 text-yellow-600" />
                </button>
                <button
                  onClick={e => { e.stopPropagation(); handleDeleteChat(chat.id); }}
                  className="ml-2 p-1 rounded hover:bg-red-50"
                  title="Delete chat"
                >
                  <FiTrash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sidebar open button (floating) */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="fixed top-6 left-2 z-30 bg-white border border-green-200 rounded-full p-2 shadow-lg hover:bg-green-50 transition md:top-6 md:left-2"
          title="Open sidebar"
        >
          <FiMenu className="w-6 h-6 text-green-700" />
        </button>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full md:ml-0 ml-0 md:pl-0 pl-0">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-yellow-400 text-white p-4 rounded-t-xl shadow-md flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 bg-white rounded-full flex items-center justify-center shadow">
              <span className="text-green-600 font-bold text-2xl">🌱</span>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Elimu Hub AI</h1>
              <p className="text-green-50 text-xs">Generative AI Assistant</p>
            </div>
          </div>
          <button
            onClick={clearConversation}
            className="px-3 py-1 bg-white text-green-700 border border-green-200 rounded-full text-xs font-semibold hover:bg-green-50 transition"
          >
            Clear
          </button>
        </div>

        {/* Mode Selection */}
        <div className="border-b bg-white p-4 rounded-b-xl">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex gap-2">
              <button
                onClick={() => setMode('chat')}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition-all border ${mode === 'chat' ? 'bg-green-600 text-white border-green-600 shadow' : 'bg-white text-green-700 border-green-200 hover:bg-green-50'}`}
              >
                Chat
              </button>
              <button
                onClick={() => setMode('completion')}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition-all border ${mode === 'completion' ? 'bg-yellow-500 text-white border-yellow-500 shadow' : 'bg-white text-yellow-700 border-yellow-200 hover:bg-yellow-50'}`}
              >
                Completion
              </button>
              <button
                onClick={() => setMode('rag')}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition-all border ${mode === 'rag' ? 'bg-gradient-to-r from-green-600 to-yellow-400 text-white border-green-600 shadow' : 'bg-white text-green-700 border-green-200 hover:bg-green-50'}`}
              >
                Knowledge Base
              </button>
            </div>

            {mode === 'rag' && (
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="px-3 py-1 border-2 border-green-200 rounded-md text-xs bg-white text-green-800 focus:ring-2 focus:ring-green-400"
              >
                <option value="">Select Topic...</option>
                {topics.map(topic => (
                  <option key={topic.id} value={topic.name}>
                    {topic.name}
                  </option>
                ))}
              </select>
            )}

            <div className="flex gap-2 items-center text-xs">
              <label className="text-green-700">Temp:</label>
              <input
                type="range"
                min="0.1"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-16 accent-green-600"
              />
              <span className="text-green-700 font-semibold">{temperature}</span>
            </div>

            <div className="flex gap-2 items-center text-xs">
              <label className="text-yellow-700">Tokens:</label>
              <input
                type="number"
                min="50"
                max="2048"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                className="w-20 px-2 py-1 border-2 border-yellow-200 rounded bg-white text-yellow-800"
              />
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-2 sm:p-4 space-y-4 bg-gradient-to-br from-white via-green-50 to-yellow-50">
          {messages.length === 0 && (
            <div className="text-center text-green-600 mt-8">
              <div className="h-12 w-12 mx-auto mb-4 text-4xl bg-gradient-to-br from-green-200 to-yellow-200 rounded-full flex items-center justify-center shadow">🌱</div>
              <h3 className="text-lg font-semibold mb-2">Welcome to Elimu Hub AI</h3>
              <p className="text-sm text-green-700">
                {mode === 'chat' && "Start a conversation with the AI assistant."}
                {mode === 'completion' && "Enter a prompt for text completion."}
                {mode === 'rag' && "Ask questions about your uploaded documents."}
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} items-end gap-2`}
            >
              {/* Avatar */}
              {message.role === 'assistant' ? (
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center shadow text-green-700">
                  <FiBox className="w-5 h-5" />
                </div>
              ) : (
                <div className="flex-shrink-0 w-8 h-8 bg-yellow-200 rounded-full flex items-center justify-center shadow text-yellow-700 font-bold text-lg">
                  {userId ? userId[0].toUpperCase() : 'U'}
                </div>
              )}
              <div
                className={`max-w-[70vw] sm:max-w-[70%] p-3 rounded-2xl shadow border-2 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-green-600 to-yellow-400 text-white border-green-200'
                    : 'bg-white text-green-900 border-green-100'
                }`}
              >
                <div className="whitespace-pre-wrap text-base font-medium">{message.content}</div>
                <div className={`text-xs mt-2 ${
                  message.role === 'user' ? 'text-green-50' : 'text-green-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                  {message.tokens && ` • ${message.tokens} tokens`}
                  {message.processingTime && ` • ${message.processingTime.toFixed(2)}s`}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start items-end gap-2">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center shadow text-green-700">
                <FiBox className="w-5 h-5" />
              </div>
              <div className="bg-white p-3 rounded-2xl border-2 border-green-100 shadow flex items-center gap-2">
                <div className="h-4 w-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-green-700 font-semibold">Generating response...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t-2 border-green-100 bg-gradient-to-r from-white to-green-50 p-4 rounded-b-xl">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  mode === 'chat' ? "Type your message... (Press Enter to send)" :
                  mode === 'completion' ? "Enter your prompt for the AI..." :
                  "Ask a question about your documents... (Select a topic first)"
                }
                className="w-full p-3 border-2 border-green-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-green-400 bg-gradient-to-r from-white to-green-50 text-green-900 placeholder-green-500 font-medium shadow"
                rows={2}
                disabled={isLoading}
              />
              {mode === 'rag' && !selectedTopic && (
                <div className="absolute top-2 right-2 text-xs text-yellow-600 bg-yellow-100 px-2 py-1 rounded shadow">
                  Select a topic first
                </div>
              )}
            </div>
            <button
              type="submit"
              disabled={isLoading || !input.trim() || (mode === 'rag' && !selectedTopic)}
              className="px-5 py-2 bg-gradient-to-r from-yellow-400 to-green-500 text-white rounded-xl font-bold shadow hover:from-green-600 hover:to-yellow-500 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <span className="text-lg">➤</span>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
