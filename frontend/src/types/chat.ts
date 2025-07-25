export interface ChatMessage {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
  chatSessionId?: string
}

export interface ChatHistory {
  id: string
  title: string
  timestamp: Date
  lastMessage: string
  chatSessionId: string
}

export interface UploadedDocument {
  id: string
  filename: string
  topic: string
  uploadedAt: string
  chatSessionId?: string
}

export interface ChatSession {
  id: string
  title: string
  documents: UploadedDocument[]
  createdAt: Date
} 