import axios, { AxiosError, AxiosInstance } from 'axios';
import {
  AuthResponse,
  ChatRequest,
  ChatResponse,
  ConversationHistoryResponse,
  ConversationListResponse,
  ConversationResponse,
  MemoryArtifactJobDetailResponse,
  MemoryArtifactJobResponse,
  MemoryCorrectionRequest,
  MemoryCorrectionResponse,
  MemoryExportResponse,
  MemoryListResponse,
  MemoryProvenanceResponse,
  MemoryResponse,
  MemorySearchRequest,
  MemorySearchResponse,
  MemoryTimelineResponse,
  PrivacyExportResponse,
  ProfileResponse,
  TextIngestRequest,
  UserResponse,
} from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60s timeout for LLM / embedding generation
    });

    // Request interceptor to attach JWT token
    this.client.interceptors.request.use((config) => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('her_ai_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    });

    // Response interceptor for logging & error shaping
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<{ detail?: string }>) => {
        const message =
          error.response?.data?.detail ||
          error.message ||
          'An unexpected error occurred while communicating with HER.';
        return Promise.reject(new Error(message));
      }
    );
  }

  // -------------------------------------------------------------------------
  // Auth Endpoints
  // -------------------------------------------------------------------------

  async login(usernameOrEmail: string, password?: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/auth/login', {
      username_or_email: usernameOrEmail,
      password: password || 'HerAiVivekSecure2026!',
    });
    if (typeof window !== 'undefined') {
      localStorage.setItem('her_ai_token', response.data.access_token);
      localStorage.setItem('her_ai_user', JSON.stringify(response.data.user));
    }
    return response.data;
  }

  async register(username: string, email: string, password?: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/auth/register', {
      username,
      email,
      password: password || 'HerAiVivekSecure2026!',
    });
    if (typeof window !== 'undefined') {
      localStorage.setItem('her_ai_token', response.data.access_token);
      localStorage.setItem('her_ai_user', JSON.stringify(response.data.user));
    }
    return response.data;
  }

  async getMe(): Promise<UserResponse> {
    const response = await this.client.get<UserResponse>('/api/auth/me');
    return response.data;
  }

  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('her_ai_token');
      localStorage.removeItem('her_ai_user');
    }
  }

  // -------------------------------------------------------------------------
  // Chat & Conversation Endpoints
  // -------------------------------------------------------------------------

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/api/chat', request);
    return response.data;
  }

  async listConversations(limit = 50): Promise<ConversationListResponse> {
    const response = await this.client.get<ConversationListResponse>('/api/conversations', {
      params: { limit },
    });
    return response.data;
  }

  async getConversation(conversationId: string): Promise<ConversationHistoryResponse> {
    const response = await this.client.get<ConversationHistoryResponse>(
      `/api/conversations/${conversationId}`
    );
    return response.data;
  }

  async createConversation(title?: string): Promise<ConversationResponse> {
    const response = await this.client.post<ConversationResponse>('/api/conversations', {
      title: title || 'New Conversation',
    });
    return response.data;
  }

  async deleteConversation(conversationId: string): Promise<{ deleted: boolean }> {
    const response = await this.client.delete(`/api/conversations/${conversationId}`);
    return response.data;
  }

  async generateTitle(conversationId: string): Promise<{ conversation_id: string; title: string }> {
    const response = await this.client.post(`/api/conversations/${conversationId}/generate-title`);
    return response.data;
  }

  // -------------------------------------------------------------------------
  // Memory Endpoints
  // -------------------------------------------------------------------------

  async listMemories(params?: {
    memory_type?: string;
    is_active?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<MemoryListResponse> {
    const response = await this.client.get<MemoryListResponse>('/api/memories', {
      params: {
        is_active: params?.is_active ?? true,
        limit: params?.limit ?? 50,
        offset: params?.offset ?? 0,
        ...(params?.memory_type ? { memory_type: params.memory_type } : {}),
      },
    });
    return response.data;
  }

  async searchMemories(request: MemorySearchRequest): Promise<MemorySearchResponse> {
    const response = await this.client.post<MemorySearchResponse>('/api/memories/search', request);
    return response.data;
  }

  async getMemory(memoryId: string): Promise<MemoryResponse> {
    const response = await this.client.get<MemoryResponse>(`/api/memories/${memoryId}`);
    return response.data;
  }

  async deactivateMemory(memoryId: string): Promise<{ deactivated: boolean; id: string }> {
    const response = await this.client.post(`/api/memories/${memoryId}/deactivate`);
    return response.data;
  }

  async deleteMemory(memoryId: string): Promise<{ deleted: boolean; id: string }> {
    const response = await this.client.delete(`/api/memories/${memoryId}`);
    return response.data;
  }

  async exportMemories(): Promise<MemoryExportResponse> {
    const response = await this.client.get<MemoryExportResponse>('/api/memories/export');
    return response.data;
  }

  // -------------------------------------------------------------------------
  // Milestone 12 Timeline, Provenance & Correction
  // -------------------------------------------------------------------------

  async getTimeline(params?: {
    order?: 'asc' | 'desc';
    precision?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<MemoryTimelineResponse> {
    const response = await this.client.get<MemoryTimelineResponse>('/api/memories/timeline', {
      params: {
        order: params?.order ?? 'asc',
        limit: params?.limit ?? 100,
        offset: params?.offset ?? 0,
        ...(params?.precision ? { precision: params.precision } : {}),
        ...(params?.start_date ? { start_date: params.start_date } : {}),
        ...(params?.end_date ? { end_date: params.end_date } : {}),
      },
    });
    return response.data;
  }

  async getProvenance(memoryId: string): Promise<MemoryProvenanceResponse> {
    const response = await this.client.get<MemoryProvenanceResponse>(
      `/api/memories/${memoryId}/provenance`
    );
    return response.data;
  }

  async correctMemory(
    memoryId: string,
    payload: MemoryCorrectionRequest
  ): Promise<MemoryCorrectionResponse> {
    const response = await this.client.post<MemoryCorrectionResponse>(
      `/api/memories/${memoryId}/correct`,
      payload
    );
    return response.data;
  }

  // -------------------------------------------------------------------------
  // Ingestion & Jobs
  // -------------------------------------------------------------------------

  async uploadFile(
    file: File,
    artifactType = 'document',
    contextNotes = ''
  ): Promise<MemoryArtifactJobResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('artifact_type', artifactType);
    if (contextNotes) {
      formData.append('context_notes', contextNotes);
    }

    const response = await this.client.post<MemoryArtifactJobResponse>(
      '/api/memories/ingest/file',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async ingestText(payload: TextIngestRequest): Promise<MemoryArtifactJobResponse> {
    const response = await this.client.post<MemoryArtifactJobResponse>(
      '/api/memories/ingest/text',
      payload
    );
    return response.data;
  }

  async getJobStatus(jobId: string): Promise<MemoryArtifactJobDetailResponse> {
    const response = await this.client.get<MemoryArtifactJobDetailResponse>(
      `/api/memories/ingest/${jobId}`
    );
    return response.data;
  }

  // -------------------------------------------------------------------------
  // Profile & Settings
  // -------------------------------------------------------------------------

  async getProfile(): Promise<ProfileResponse> {
    const response = await this.client.get<ProfileResponse>('/api/profile');
    return response.data;
  }

  async updateUsername(username: string): Promise<UserResponse> {
    const response = await this.client.patch<UserResponse>('/api/profile', { username });
    return response.data;
  }

  async setPreference(key: string, value: Record<string, unknown>): Promise<void> {
    await this.client.put('/api/profile/preferences', { key, value });
  }

  async deletePreference(key: string): Promise<void> {
    await this.client.delete(`/api/profile/preferences/${key}`);
  }

  async getPrivacyExport(): Promise<PrivacyExportResponse> {
    const response = await this.client.get<PrivacyExportResponse>('/api/profile/export');
    return response.data;
  }
}

export const api = new ApiClient();
