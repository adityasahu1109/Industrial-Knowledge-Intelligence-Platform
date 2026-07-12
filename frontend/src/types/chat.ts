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
  sources?: StreamSource[];
  attachments?: any[];
}
