export interface StreamSource {
  label: string;
  filename: string;
  page: number;
  section: string;
  doc_id: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status?: 'generating' | 'done' | 'interrupted' | 'failed';
  sources?: StreamSource[];
  attachments?: any[];
  created_at?: string;
}
