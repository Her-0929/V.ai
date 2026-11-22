/**
 * HER AI — Comprehensive TypeScript Type Definitions
 * Aligned 1:1 with Backend Pydantic Schemas (FastAPI v0.4.0)
 */

// ---------------------------------------------------------------------------
// Authentication & User Profile
// ---------------------------------------------------------------------------

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface PreferenceResponse {
  id: string;
  key: string;
  value: Record<string, unknown>;
  updated_at: string;
}

export interface ProfileResponse {
  user: UserResponse;
  preferences: PreferenceResponse[];
  memory_count: number;
  conversation_count: number;
}

export interface PrivacyExportResponse {
  user: UserResponse;
  preferences: PreferenceResponse[];
  memories: Record<string, unknown>[];
  total_memories: number;
  exported_at: string;
}

// ---------------------------------------------------------------------------
// Conversations & Messages
// ---------------------------------------------------------------------------

export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_metadata?: {
    emotional_context?: EmotionalContextResponse;
    memory_count?: number;
    model?: string;
    [key: string]: unknown;
  } | null;
  created_at: string;
}

export interface ConversationResponse {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  conversations: ConversationResponse[];
  total: number;
}

export interface ConversationHistoryResponse {
  conversation: ConversationResponse;
  messages: MessageResponse[];
  total_messages: number;
}

// ---------------------------------------------------------------------------
// Chat & RAG Grounding
// ---------------------------------------------------------------------------

export interface EmotionalContextResponse {
  emotion: string;
  intensity: 'LOW' | 'MEDIUM' | 'HIGH' | string;
  confidence: number;
  should_acknowledge: boolean;
}

export interface RetrievedMemoryInfo {
  id?: string;
  content: string;
  memory_type?: string;
  similarity?: number;
  importance?: number;
  confidence?: number;
  event_date?: string | null;
  event_date_precision?: string;
  source_created_at?: string | null;
  [key: string]: unknown;
}

export interface ChatRequest {
  user_id?: string | null;
  conversation_id?: string | null;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  retrieved_memories: RetrievedMemoryInfo[];
  memory_count: number;
  model: string;
  emotional_context?: EmotionalContextResponse | null;
}

// ---------------------------------------------------------------------------
// Memories & Timeline
// ---------------------------------------------------------------------------

export type MemoryType =
  | 'personal_info'
  | 'personality_trait'
  | 'communication_preference'
  | 'like'
  | 'dislike'
  | 'hobby'
  | 'interest'
  | 'career_goal'
  | 'dream'
  | 'ambition'
  | 'life_event'
  | 'relationship'
  | 'emotional_experience'
  | 'important_conversation'
  | 'daily_experience'
  | 'future_plan'
  | 'learning_progress'
  | 'milestone'
  | 'general';

export type TemporalPrecision = 'day' | 'month' | 'year' | 'decade' | 'unknown';
export type MemoryStatus = 'active' | 'superseded' | 'disputed';

export interface MemoryResponse {
  id: string;
  user_id: string;
  memory_type: MemoryType | string;
  content: string;
  importance: number;
  confidence: number;
  is_active: boolean;
  event_date?: string | null;
  event_date_precision: TemporalPrecision | string;
  source_created_at?: string | null;
  status: MemoryStatus | string;
  superseded_by_id?: string | null;
  access_scope: string;
  version: number;
  memory_metadata?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  last_accessed_at?: string | null;
}

export interface MemoryListResponse {
  memories: MemoryResponse[];
  total: number;
}

export interface MemorySearchRequest {
  query: string;
  limit?: number;
  min_similarity?: number;
}

export interface MemorySearchResult {
  id: string;
  content: string;
  memory_type: string;
  importance: number;
  confidence: number;
  similarity: number;
  event_date?: string | null;
  event_date_precision: string;
  status: string;
}

export interface MemorySearchResponse {
  results: MemorySearchResult[];
  query: string;
  total: number;
}

export interface MemoryExportResponse {
  user_id: string;
  total_memories: number;
  memories: MemoryResponse[];
  exported_at: string;
}

export interface MemoryTimelineItem {
  id: string;
  content: string;
  memory_type: string;
  importance: number;
  confidence: number;
  event_date?: string | null;
  event_date_precision: string;
  formatted_date: string;
  source_created_at?: string | null;
  status: string;
  version: number;
  primary_source_type: string;
  primary_source_location?: string | null;
}

export interface MemoryTimelineResponse {
  items: MemoryTimelineItem[];
  total: number;
  limit: number;
  offset: number;
}

// ---------------------------------------------------------------------------
// Provenance & Correction
// ---------------------------------------------------------------------------

export interface ArtifactProvenanceInfo {
  artifact_id: string;
  filename: string;
  artifact_type: string;
  checksum_sha256: string;
}

export interface MemorySourceInfo {
  source_id: string;
  source_type: string;
  source_location?: string | null;
  excerpt?: string | null;
  created_at: string;
  artifact?: ArtifactProvenanceInfo | null;
}

export interface MemoryHistoryEntry {
  memory_id: string;
  version: number;
  status: string;
  is_active: boolean;
  created_at: string;
  superseded_at?: string | null;
  superseded_reason?: string | null;
}

export interface MemoryProvenanceResponse {
  memory_id: string;
  content: string;
  memory_type: string;
  importance: number;
  confidence: number;
  event_date?: string | null;
  event_date_precision: string;
  version: number;
  status: string;
  superseded_by_id?: string | null;
  sources: MemorySourceInfo[];
  history: MemoryHistoryEntry[];
}

export interface MemoryCorrectionRequest {
  content: string;
  memory_type?: MemoryType | null;
  importance?: number | null;
  confidence?: number | null;
  event_date?: string | null;
  event_date_precision?: TemporalPrecision | null;
  reason: string;
}

export interface MemoryCorrectionResponse {
  success: boolean;
  old_memory: MemoryResponse;
  new_memory: MemoryResponse;
  correction_reason: string;
}

// ---------------------------------------------------------------------------
// Ingestion & Jobs
// ---------------------------------------------------------------------------

export type ArtifactType = 'note' | 'letter' | 'document' | 'photo' | 'audio_transcript';

export interface TextIngestRequest {
  title: string;
  content: string;
  artifact_type?: ArtifactType;
  context_notes?: string | null;
}

export interface MemoryArtifactJobResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | string;
  artifact_type: string;
  filename: string;
  file_size_bytes: number;
  checksum_sha256: string;
  retry_count: number;
  created_at: string;
  message: string;
}

export interface MemoryArtifactJobDetailResponse {
  job_id: string;
  user_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | string;
  artifact_type: string;
  filename: string;
  file_size_bytes: number;
  checksum_sha256: string;
  retry_count: number;
  error_message?: string | null;
  context_notes?: string | null;
  created_at: string;
  processed_at?: string | null;
  extracted_memories_count: number;
  extracted_memory_ids: string[];
}
