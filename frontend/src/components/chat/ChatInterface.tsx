'use client'

import { useState, useEffect } from 'react'
import { ChatMessage, ChatHistory, Subject } from '@/types/chat'
import Sidebar from './Sidebar'
import ChatWindow from './ChatWindow'
import ChatInput from './ChatInput'

export default function ChatInterface() {
  const [currentSubject, setCurrentSubject] = useState<Subject>('Mathematics')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

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
          topic: currentSubject
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

  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
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
        subject: currentSubject
      }

      setMessages(prev => [...prev, aiMessage])

      // Update chat history
      const newChatHistory: ChatHistory = {
        id: Date.now().toString(),
        title: content.length > 30 ? content.substring(0, 30) + '...' : content,
        subject: currentSubject,
        timestamp: new Date(),
        lastMessage: aiResponse.length > 50 ? aiResponse.substring(0, 50) + '...' : aiResponse
      }

      setChatHistory(prev => [newChatHistory, ...prev.slice(0, 9)]) // Keep only 10 most recent
    } catch (error) {
      console.error('Error generating AI response:', error)
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble responding right now. Please try again.",
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubjectChange = (subject: Subject) => {
    setCurrentSubject(subject)
    setMessages([]) // Clear messages when subject changes
  }

  const handleChatSelect = (chatId: string) => {
    // In a real app, this would load the specific chat
    console.log('Loading chat:', chatId)
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar - hidden on mobile by default */}
      <div className="hidden md:block">
        <Sidebar
          currentSubject={currentSubject}
          onSubjectChange={handleSubjectChange}
          chatHistory={chatHistory}
          onChatSelect={handleChatSelect}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
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

      {/* Mobile sidebar overlay */}
      {!isSidebarCollapsed && (
        <div className="md:hidden fixed inset-0 z-30">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setIsSidebarCollapsed(true)} />
          <div className="absolute left-0 top-0 h-full w-80 bg-white">
            <Sidebar
              currentSubject={currentSubject}
              onSubjectChange={handleSubjectChange}
              chatHistory={chatHistory}
              onChatSelect={handleChatSelect}
              isCollapsed={false}
              onToggleCollapse={() => setIsSidebarCollapsed(true)}
            />
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <ChatWindow
          messages={messages}
          currentSubject={currentSubject}
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