export type Subject = 'Mathematics' | 'English' | 'Science' | 'Kiswahili' | 'History'

export interface ChatMessage {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
  subject?: Subject
}

export interface ChatHistory {
  id: string
  title: string
  subject: Subject
  timestamp: Date
  lastMessage: string
} 