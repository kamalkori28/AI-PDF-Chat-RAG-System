export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  full_name: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type DocumentRecord = {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  sha256: string;
  status: "queued" | "processing" | "ready" | "failed";
  chunk_count: number;
  error_message?: string | null;
  document_metadata?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type UploadResponse = {
  documents: DocumentRecord[];
};

export type Citation = {
  label: string;
  document_id: string;
  filename: string;
  page: number;
  chunk_id: string;
  score: number;
  preview: string;
};

export type ChatRequest = {
  message: string;
  session_id?: string | null;
  document_ids?: string[] | null;
  top_k: number;
  hybrid: boolean;
};

export type MessageRecord = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[] | null;
  created_at: string;
};

export type ChatSession = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: MessageRecord[];
};

export type HistoryResponse = {
  sessions: ChatSession[];
};

export type StreamMetadata = {
  session_id: string;
  citations: Citation[];
};

export type StreamError = {
  detail: string;
  status_code: number;
};
