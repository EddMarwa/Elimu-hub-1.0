'use client'

import { useState, useEffect } from 'react'
import { ChatMessage, ChatHistory, UploadedDocument } from '@/types/chat'
import Sidebar from './Sidebar'
import ChatWindow from './ChatWindow'
import ChatInput from './ChatInput'

export default function ChatInterface() {
  const [currentChatSessionId, setCurrentChatSessionId] = useState<string>('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  // Initialize a new chat session on component mount
  useEffect(() => {
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    setCurrentChatSessionId(sessionId)
  }, [])

  // Real AI response function using backend API
  const generateAIResponse = async (userMessage: string): Promise<string> => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: userMessage,
          chatSessionId: currentChatSessionId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.status === 'error') {
        return data.message || "I'm having trouble processing your request right now."
      }

      return data.answer || "I couldn't generate a response. Please try again."
      
    } catch (error) {
      console.error('Error calling AI API:', error)
      return "I'm experiencing technical difficulties. Please try again later."
    }
  }

  // Document upload handler
  const handleDocumentUpload = async (file: File, topic: string): Promise<void> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('topic', topic)
    formData.append('chatSessionId', currentChatSessionId)

    const response = await fetch('http://localhost:8000/api/v1/upload', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`)
    }

    const result = await response.json()
    
    // Add to uploaded documents list
    const newDocument: UploadedDocument = {
      id: result.id.toString(),
      filename: result.filename,
      topic: result.topic || topic,
      uploadedAt: result.uploaded_at,
      chatSessionId: currentChatSessionId
    }
    
    setUploadedDocuments(prev => [...prev, newDocument])
  }

  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date(),
      chatSessionId: currentChatSessionId
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const aiResponse = await generateAIResponse(content)
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: aiResponse,
        isUser: false,
        timestamp: new Date(),
        chatSessionId: currentChatSessionId
      }

      setMessages(prev => [...prev, aiMessage])

      // Update chat history
      const newChatHistory: ChatHistory = {
        id: Date.now().toString(),
        title: content.length > 30 ? content.substring(0, 30) + '...' : content,
        timestamp: new Date(),
        lastMessage: aiResponse.length > 50 ? aiResponse.substring(0, 50) + '...' : aiResponse,
        chatSessionId: currentChatSessionId
      }

      setChatHistory(prev => [newChatHistory, ...prev.slice(0, 9)]) // Keep only 10 most recent
    } catch (error) {
      console.error('Error generating AI response:', error)
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble responding right now. Please try again.",
        isUser: false,
        timestamp: new Date(),
        chatSessionId: currentChatSessionId
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleChatSelect = (chatId: string) => {
    // Create a new session when selecting a different chat
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    setCurrentChatSessionId(sessionId)
    setMessages([]) // Clear messages when starting new chat
    setUploadedDocuments([]) // Clear uploaded documents for new session
    
    // Auto-collapse sidebar on mobile after selection
    if (window.innerWidth < 768) {
      setIsSidebarCollapsed(true)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar - responsive width and adaptive layout */}
      <div className={`hidden md:block transition-all duration-300 ${
        isSidebarCollapsed ? 'w-16' : 'w-80 max-w-[25vw]'
      }`}>
        <Sidebar
          chatHistory={chatHistory}
          onChatSelect={handleChatSelect}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          uploadedDocuments={uploadedDocuments}
          onDocumentUpload={handleDocumentUpload}
          currentChatSessionId={currentChatSessionId}
        />
      </div>

      {/* Mobile sidebar toggle */}
      <div className="md:hidden absolute top-4 left-4 z-20">
        <button
          onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          className="p-2 bg-white rounded-lg shadow-md border border-gray-200"
          aria-label="Toggle sidebar"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Mobile sidebar overlay - improved positioning and transitions */}
      {!isSidebarCollapsed && (
        <div className="md:hidden fixed inset-0 z-30 transition-opacity duration-200">
          <div className="absolute inset-0 bg-black bg-opacity-50 transition-opacity" onClick={() => setIsSidebarCollapsed(true)} />
          <div className="absolute left-0 top-0 h-full w-80 max-w-[85vw] bg-white transform transition-transform duration-300 shadow-xl">
            <Sidebar
              chatHistory={chatHistory}
              onChatSelect={handleChatSelect}
              isCollapsed={false}
              onToggleCollapse={() => setIsSidebarCollapsed(true)}
              uploadedDocuments={uploadedDocuments}
              onDocumentUpload={handleDocumentUpload}
              currentChatSessionId={currentChatSessionId}
            />
          </div>
        </div>
      )}

      {/* Main Chat Area - responsive flex layout */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Chat header with adaptive spacing */}
        <div className="md:hidden flex items-center justify-between p-4 bg-white border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Elimu Hub Chat</h2>
          <span className="text-sm text-gray-600">
            {chatHistory.length > 0 ? `${chatHistory.length} chat${chatHistory.length > 1 ? 's' : ''}` : 'New chat'}
          </span>
        </div>
        
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
        />
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
} 