'use client'

import { useState, KeyboardEvent, useRef } from 'react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading?: boolean
  disabled?: boolean
  currentSubject?: string
}

export default function ChatInput({ onSendMessage, isLoading = false, disabled = false, currentSubject = 'General' }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSend = () => {
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Check if file is PDF
    if (file.type !== 'application/pdf') {
      alert('Please select a PDF file only.')
      return
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.')
      return
    }

    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('topic', currentSubject)

      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`)
      }

      const result = await response.json()
      
      // Send a message indicating successful upload
      onSendMessage(`📄 Successfully uploaded "${file.name}" to ${currentSubject} topic. You can now ask questions about this document!`)
      
    } catch (error) {
      console.error('Upload error:', error)
      alert('Failed to upload file. Please try again.')
    } finally {
      setIsUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const triggerFileUpload = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileUpload}
        className="hidden"
        aria-label="Upload PDF file"
        title="Upload PDF file"
      />
      
      <div className="flex items-end gap-3">
        {/* Upload button */}
        <button
          onClick={triggerFileUpload}
          disabled={isUploading || isLoading || disabled}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white rounded-lg px-4 py-3 transition-all disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-lg"
          title="Upload PDF document"
        >
          {isUploading ? (
            <>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce animate-delay-100"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce animate-delay-200"></div>
              </div>
              <span className="text-sm hidden sm:inline">Uploading...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span className="hidden sm:inline">📄 PDF</span>
            </>
          )}
        </button>

        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Press Enter to send)"
            className="w-full resize-none border-2 border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-gradient-to-r from-gray-50 to-white text-gray-900 placeholder-gray-500 min-h-11 max-h-30"
            rows={1}
            disabled={disabled || isLoading}
          />
        </div>
        <button
          onClick={handleSend}
          disabled={!message.trim() || isLoading || disabled}
          className="bg-yellow-500 hover:bg-green-600 disabled:bg-gray-400 text-white rounded-lg px-4 py-3 transition-all disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-lg"
        >
          {isLoading ? (
            <>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce animate-delay-100"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce animate-delay-200"></div>
              </div>
              <span className="text-sm">Sending...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <span className="hidden sm:inline">Send</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
} 