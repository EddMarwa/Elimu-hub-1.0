'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tokens?: number;
  processingTime?: number;
}

interface GenerativeAIProps {
  apiBaseUrl?: string;
  userId?: string;
}

export default function GenerativeAI({ 
  apiBaseUrl = 'http://localhost:8000/api/v1',
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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

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
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiBaseUrl}/list-topics`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTopics(data.topics || []);
      }
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
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

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      let response;
      
      if (mode === 'rag') {
        // RAG mode - use existing chat endpoint
        response = await fetch(`${apiBaseUrl}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            question: input.trim(),
            topic: selectedTopic
          })
        });
      } else if (mode === 'chat') {
        // Chat completion mode
        response = await fetch(`${apiBaseUrl}/llm/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            messages: messages.concat(userMessage).map(msg => ({
              role: msg.role,
              content: msg.content
            })),
            max_tokens: maxTokens,
            temperature: temperature
          })
        });
      } else {
        // Completion mode
        response = await fetch(`${apiBaseUrl}/llm/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
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
        // Add source information if available
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

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const clearConversation = () => {
    setMessages([]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 bg-white rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-bold">🧠</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">Elimu Hub AI</h1>
              <p className="text-blue-100 text-sm">Generative AI Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xl">✨</span>
            <span className="text-sm">{messages.length} messages</span>
          </div>
        </div>
      </div>

      {/* Mode Selection */}
      <div className="border-b bg-gray-50 p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex gap-2">
            <button
              onClick={() => setMode('chat')}
              className={`px-3 py-1 rounded-full text-sm ${
                mode === 'chat' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Chat Mode
            </button>
            <button
              onClick={() => setMode('completion')}
              className={`px-3 py-1 rounded-full text-sm ${
                mode === 'completion' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Completion
            </button>
            <button
              onClick={() => setMode('rag')}
              className={`px-3 py-1 rounded-full text-sm ${
                mode === 'rag' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Knowledge Base
            </button>
          </div>

          {mode === 'rag' && (
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="px-3 py-1 border rounded-md text-sm"
            >
              <option value="">Select Topic...</option>
              {topics.map(topic => (
                <option key={topic.id} value={topic.name}>
                  {topic.name}
                </option>
              ))}
            </select>
          )}

          <div className="flex gap-2 items-center text-sm">
            <label>Temp:</label>
            <input
              type="range"
              min="0.1"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-16"
            />
            <span>{temperature}</span>
          </div>

          <div className="flex gap-2 items-center text-sm">
            <label>Tokens:</label>
            <input
              type="number"
              min="50"
              max="2048"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="w-20 px-2 py-1 border rounded"
            />
          </div>

          <button
            onClick={clearConversation}
            className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <div className="h-12 w-12 mx-auto mb-4 text-gray-300 text-3xl">🧠</div>
            <h3 className="text-lg font-medium mb-2">Welcome to Elimu Hub AI</h3>
            <p className="text-sm">
              {mode === 'chat' && "Start a conversation with the AI assistant"}
              {mode === 'completion' && "Enter a prompt for text completion"}
              {mode === 'rag' && "Ask questions about your uploaded documents"}
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              <div className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {message.timestamp.toLocaleTimeString()}
                {message.tokens && ` • ${message.tokens} tokens`}
                {message.processingTime && ` • ${message.processingTime.toFixed(2)}s`}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-600">Generating response...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                mode === 'chat' ? "Type your message..." :
                mode === 'completion' ? "Enter your prompt..." :
                "Ask a question about your documents..."
              }
              className="w-full p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
              disabled={isLoading}
            />
            {mode === 'rag' && !selectedTopic && (
              <div className="absolute top-2 right-2 text-xs text-red-500">
                Select a topic first
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim() || (mode === 'rag' && !selectedTopic)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
  );
}
