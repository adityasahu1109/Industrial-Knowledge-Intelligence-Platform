export interface DocumentItem {
  doc_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'complete' | 'failed';
  chunk_count: number;
  entity_count: number;
}
