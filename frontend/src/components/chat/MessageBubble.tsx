'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import { ChatMessage, Subject } from '@/types/chat'

interface MessageBubbleProps {
  message: ChatMessage
}

const subjectColors: Record<Subject, string> = {
  Mathematics: 'bg-green-100 text-green-800',
  English: 'bg-yellow-100 text-yellow-800',
  Science: 'bg-blue-100 text-blue-800',
  Kiswahili: 'bg-orange-100 text-orange-800',
  History: 'bg-purple-100 text-purple-800'
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  if (message.isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[70%] bg-gradient-to-r from-green-600 to-yellow-500 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-lg border border-green-500">
          <p className="text-sm font-medium">{message.content}</p>
          <p className="text-xs text-green-100 mt-1 opacity-90">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[70%] bg-white rounded-2xl rounded-bl-md px-4 py-3 shadow-lg border-2 border-gray-200">
        {message.subject && (
          <div className={cn(
            'inline-block px-2 py-1 rounded-full text-xs font-medium mb-2',
            subjectColors[message.subject]
          )}>
            {message.subject}
          </div>
        )}
        <div className="flex items-start gap-2">
          <div className="flex-1">
            <p className="text-sm text-gray-900 font-medium">{message.content}</p>
            <p className="text-xs text-gray-500 mt-1">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
          </div>
          <button
            onClick={copyToClipboard}
            className="text-gray-500 hover:text-gray-700 transition-colors p-1 rounded hover:bg-gray-100"
            title="Copy message"
          >
            {copied ? (
              <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  )
} 