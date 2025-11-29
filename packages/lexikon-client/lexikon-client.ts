/**
 * Lexikon HTTP Client
 *
 * TypeScript client library for consuming Lexikon REST API
 * Provides interfaces for all 6 SPRINT 2-4 features:
 * - Feature 1: Semantic Search API
 * - Feature 2: Ontology Reasoning API
 * - Feature 3: Bulk Import API
 * - Feature 4: Vocabulary Extraction API
 * - Feature 5: HITL Workflow API
 * - Feature 6: Analytics & Metrics API
 *
 * Usage:
 *   const client = new LexikonClient('http://localhost:8000', accessToken);
 *   const results = await client.semanticSearch('web semantic data');
 */

interface ClientConfig {
  baseUrl: string;
  accessToken?: string;
  refreshToken?: string;
  retryAttempts?: number;
  retryDelay?: number;
  timeout?: number;
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

// ============================================================================
// FEATURE 1: Semantic Search API
// ============================================================================

interface SearchTermRequest {
  query: string;
  threshold?: number; // 0.0-1.0, default 0.5
  top_k?: number; // 1-50, default 10
}

interface SearchResult {
  term_id: string;
  name: string;
  definition: string;
  similarity: number;
  domain?: string;
  level?: string;
}

interface SearchResponse {
  success: boolean;
  data: {
    query: string;
    results: SearchResult[];
    execution_time_ms: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

// ============================================================================
// FEATURE 2: Ontology Reasoning API
// ============================================================================

interface CreateRelationRequest {
  source_term_id: string;
  target_term_id: string;
  relation_type: 'broader' | 'narrower' | 'equivalent' | 'related' | 'part_of' | 'has_part';
  confidence?: number; // 0.0-1.0, default 1.0
  relation_metadata?: Record<string, unknown>;
}

interface RelationResponse {
  id: string;
  source_term_id: string;
  target_term_id: string;
  relation_type: string;
  confidence: number;
  created_at: string;
  created_by: string;
}

interface InferenceRequest {
  source_term_id: string;
  rules?: ('transitive' | 'symmetric' | 'equivalence' | 'inverse')[];
  max_depth?: number; // 1-10, default 3
}

interface InferredRelation {
  source_term_id: string;
  source_term_name: string;
  target_term_id: string;
  target_term_name: string;
  relation_type: string;
  confidence: number;
  inference_path: string[];
}

interface InferenceResponse {
  success: boolean;
  data: {
    source_term_id: string;
    inferred_relations: InferredRelation[];
    execution_time_ms: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

// ============================================================================
// FEATURE 3: Bulk Import API
// ============================================================================

interface BulkImportRequest {
  content: string; // JSON, CSV, or RDF/Turtle content
  format: 'json' | 'csv' | 'skos'; // RDF/SKOS
  mode?: 'create_only' | 'update_only' | 'upsert'; // default: upsert
}

interface ImportStats {
  created: number;
  updated: number;
  skipped: number;
  total: number;
  errors?: Array<{
    row_index: number;
    error: string;
  }>;
}

interface BulkImportResponse {
  success: boolean;
  data: {
    import_stats: ImportStats;
    execution_time_ms: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

// ============================================================================
// FEATURE 4: Vocabulary Extraction API
// ============================================================================

interface ExtractionRequest {
  content: string; // 10-100,000 characters
  patterns?: ('parentheses' | 'bold' | 'glossary' | 'inline')[];
  language?: 'fr' | 'en' | 'es'; // default: en
}

interface ExtractedTerm {
  text: string;
  definition: string;
  pattern: string;
  confidence: number;
}

interface ExtractionResponse {
  success: boolean;
  data: {
    extracted_terms: ExtractedTerm[];
    execution_time_ms: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

// ============================================================================
// FEATURE 5: HITL Workflow API
// ============================================================================

type ReviewType = 'relation_quality' | 'term_clarity' | 'embedding_accuracy';
type ReviewStatus = 'pending' | 'approved' | 'rejected' | 'skipped';

interface CreateReviewRequest {
  term_id: string;
  review_type: ReviewType;
}

interface ReviewResponse {
  id: string;
  term_id: string;
  review_type: ReviewType;
  status: ReviewStatus;
  created_at: string;
  user_id: string;
}

interface ApproveReviewRequest {
  feedback?: string;
  confidence_score?: number; // 0.0-1.0
}

interface RejectReviewRequest {
  feedback: string;
  confidence_score?: number; // 0.0-1.0
}

interface ReviewQueueResponse {
  success: boolean;
  data: {
    reviews: ReviewResponse[];
    total: number;
    page: number;
    limit: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

interface QueueMetrics {
  pending: number;
  approved: number;
  rejected: number;
  total: number;
}

// ============================================================================
// FEATURE 6: Analytics & Metrics API
// ============================================================================

interface UsageMetrics {
  total_terms: number;
  terms_by_level: Record<string, number>;
  terms_by_status: Record<string, number>;
  total_relations: number;
}

interface OntologyHealthMetrics {
  embedding_coverage_percent: number;
  relation_coverage_percent: number;
  avg_confidence: number;
  distinct_domains: number;
}

interface GrowthMetrics {
  period_days: number;
  terms_added: number;
  relations_added: number;
  daily_term_average: number;
  daily_relation_average: number;
}

interface DriftDetectionResult {
  status: 'healthy' | 'drifting';
  isolated_terms_count: number;
  threshold: number;
  isolated_term_ids: string[];
}

// ============================================================================
// Main Lexikon Client Class
// ============================================================================

export class LexikonClient {
  private config: Required<ClientConfig>;
  private headers: Record<string, string>;

  constructor(config: ClientConfig) {
    this.config = {
      baseUrl: config.baseUrl.replace(/\/$/, ''), // Remove trailing slash
      accessToken: config.accessToken || '',
      refreshToken: config.refreshToken || '',
      retryAttempts: config.retryAttempts || 3,
      retryDelay: config.retryDelay || 1000,
      timeout: config.timeout || 30000,
    };

    this.headers = {
      'Content-Type': 'application/json',
    };

    if (this.config.accessToken) {
      this.headers['Authorization'] = `Bearer ${this.config.accessToken}`;
    }
  }

  /**
   * Set authentication token
   */
  setToken(accessToken: string, refreshToken?: string): void {
    this.config.accessToken = accessToken;
    this.headers['Authorization'] = `Bearer ${accessToken}`;
    if (refreshToken) {
      this.config.refreshToken = refreshToken;
    }
  }

  /**
   * Internal HTTP request handler with retry logic
   */
  private async request<T>(
    method: string,
    path: string,
    body?: Record<string, unknown>,
    retryCount = 0
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const options: RequestInit = {
        method,
        headers: this.headers,
        signal: controller.signal,
      };

      if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(url, options);

      if (response.status === 401 && this.config.refreshToken) {
        // Token expired, try to refresh
        await this.refreshAccessToken();
        return this.request<T>(method, path, body, retryCount);
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new LexikonError(
          `HTTP ${response.status}: ${(errorData as any).error?.message || response.statusText}`,
          response.status,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof LexikonError) {
        throw error;
      }

      if (retryCount < this.config.retryAttempts) {
        await new Promise((resolve) => setTimeout(resolve, this.config.retryDelay));
        return this.request<T>(method, path, body, retryCount + 1);
      }

      throw new LexikonError(
        `Request failed: ${error instanceof Error ? error.message : String(error)}`,
        0,
        { original_error: error }
      );
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Refresh access token using refresh token
   */
  private async refreshAccessToken(): Promise<void> {
    if (!this.config.refreshToken) {
      throw new LexikonError('No refresh token available', 401);
    }

    try {
      const response = await fetch(`${this.config.baseUrl}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.refreshToken}`,
        },
        body: JSON.stringify({ refresh_token: this.config.refreshToken }),
      });

      if (!response.ok) {
        throw new LexikonError('Token refresh failed', response.status);
      }

      const data = await response.json();
      this.setToken(data.access_token, data.refresh_token);
    } catch (error) {
      throw new LexikonError(
        `Failed to refresh token: ${error instanceof Error ? error.message : String(error)}`,
        401
      );
    }
  }

  // ========================================================================
  // FEATURE 1: Semantic Search API
  // ========================================================================

  /**
   * Search for terms by semantic similarity
   */
  async semanticSearch(query: string, options?: Partial<SearchTermRequest>): Promise<SearchResponse> {
    const body: SearchTermRequest = {
      query,
      threshold: options?.threshold ?? 0.5,
      top_k: options?.top_k ?? 10,
    };

    return this.request<SearchResponse>('POST', '/api/terms/search', body);
  }

  // ========================================================================
  // FEATURE 2: Ontology Reasoning API
  // ========================================================================

  /**
   * Create a relation between two terms
   */
  async createRelation(request: CreateRelationRequest): Promise<RelationResponse> {
    return this.request<RelationResponse>('POST', '/api/ontology/relations', request);
  }

  /**
   * Infer new relations using reasoning rules
   */
  async inferRelations(request: InferenceRequest): Promise<InferenceResponse> {
    return this.request<InferenceResponse>('POST', '/api/ontology/infer', request);
  }

  /**
   * Get relations for a term
   */
  async getRelations(
    termId: string,
    direction: 'outgoing' | 'incoming' | 'both' = 'both'
  ): Promise<{ relations: RelationResponse[] }> {
    return this.request('GET', `/api/ontology/relations/${termId}?direction=${direction}`);
  }

  /**
   * Delete a relation
   */
  async deleteRelation(relationId: string): Promise<{ success: boolean }> {
    return this.request('DELETE', `/api/ontology/relations/${relationId}`);
  }

  // ========================================================================
  // FEATURE 3: Bulk Import API
  // ========================================================================

  /**
   * Import terms from JSON, CSV, or RDF/SKOS format
   */
  async bulkImport(request: BulkImportRequest): Promise<BulkImportResponse> {
    return this.request<BulkImportResponse>('POST', '/api/vocabularies/bulk-import', request);
  }

  /**
   * Import from JSON array
   */
  async importFromJSON(
    terms: Array<{ name: string; definition: string; [key: string]: unknown }>,
    mode: 'create_only' | 'update_only' | 'upsert' = 'upsert'
  ): Promise<BulkImportResponse> {
    return this.bulkImport({
      content: JSON.stringify(terms),
      format: 'json',
      mode,
    });
  }

  /**
   * Import from CSV (name,definition,domain,level,status)
   */
  async importFromCSV(
    csv: string,
    mode: 'create_only' | 'update_only' | 'upsert' = 'upsert'
  ): Promise<BulkImportResponse> {
    return this.bulkImport({
      content: csv,
      format: 'csv',
      mode,
    });
  }

  // ========================================================================
  // FEATURE 4: Vocabulary Extraction API
  // ========================================================================

  /**
   * Extract terms from document content
   */
  async extractVocabulary(
    content: string,
    options?: Partial<ExtractionRequest>
  ): Promise<ExtractionResponse> {
    const request: ExtractionRequest = {
      content,
      patterns: options?.patterns ?? ['parentheses', 'bold', 'glossary', 'inline'],
      language: options?.language ?? 'en',
    };

    return this.request<ExtractionResponse>('POST', '/api/vocabularies/extract', request);
  }

  // ========================================================================
  // FEATURE 5: HITL Workflow API
  // ========================================================================

  /**
   * Create a review request for a term
   */
  async createReview(request: CreateReviewRequest): Promise<ReviewResponse> {
    return this.request<ReviewResponse>('POST', '/api/hitl/reviews', request);
  }

  /**
   * Get pending reviews
   */
  async getReviewQueue(
    status: ReviewStatus = 'pending',
    limit = 20
  ): Promise<ReviewQueueResponse> {
    return this.request<ReviewQueueResponse>(
      'GET',
      `/api/hitl/queue?status=${status}&limit=${limit}`
    );
  }

  /**
   * Approve a review
   */
  async approveReview(reviewId: string, request: ApproveReviewRequest): Promise<ReviewResponse> {
    return this.request<ReviewResponse>('POST', `/api/hitl/reviews/${reviewId}/approve`, request);
  }

  /**
   * Reject a review
   */
  async rejectReview(reviewId: string, request: RejectReviewRequest): Promise<ReviewResponse> {
    return this.request<ReviewResponse>('POST', `/api/hitl/reviews/${reviewId}/reject`, request);
  }

  /**
   * Get queue metrics
   */
  async getQueueMetrics(): Promise<{ data: QueueMetrics }> {
    return this.request('GET', '/api/hitl/queue/metrics');
  }

  // ========================================================================
  // FEATURE 6: Analytics & Metrics API
  // ========================================================================

  /**
   * Get usage metrics
   */
  async getUsageMetrics(days = 30): Promise<{ data: UsageMetrics }> {
    return this.request('GET', `/api/metrics/usage?days=${days}`);
  }

  /**
   * Get ontology health metrics
   */
  async getOntologyHealth(): Promise<{ data: OntologyHealthMetrics }> {
    return this.request('GET', '/api/metrics/ontology-health');
  }

  /**
   * Get growth metrics
   */
  async getGrowthMetrics(days = 30): Promise<{ data: GrowthMetrics }> {
    return this.request('GET', `/api/metrics/growth?days=${days}`);
  }

  /**
   * Detect vocabulary drift
   */
  async detectVocabularyDrift(threshold = 0.8): Promise<{ data: DriftDetectionResult }> {
    return this.request('GET', `/api/metrics/drift-detection?threshold=${threshold}`);
  }
}

// ============================================================================
// Error Handling
// ============================================================================

export class LexikonError extends Error {
  constructor(
    message: string,
    public statusCode: number = 0,
    public details: Record<string, unknown> = {}
  ) {
    super(message);
    this.name = 'LexikonError';
  }

  isAuthError(): boolean {
    return this.statusCode === 401 || this.statusCode === 403;
  }

  isNotFoundError(): boolean {
    return this.statusCode === 404;
  }

  isValidationError(): boolean {
    return this.statusCode === 422;
  }
}

// ============================================================================
// Export Types
// ============================================================================

export type {
  ClientConfig,
  ApiResponse,
  SearchTermRequest,
  SearchResult,
  SearchResponse,
  CreateRelationRequest,
  RelationResponse,
  InferenceRequest,
  InferredRelation,
  InferenceResponse,
  BulkImportRequest,
  ImportStats,
  BulkImportResponse,
  ExtractionRequest,
  ExtractedTerm,
  ExtractionResponse,
  CreateReviewRequest,
  ReviewResponse,
  ApproveReviewRequest,
  RejectReviewRequest,
  ReviewQueueResponse,
  QueueMetrics,
  UsageMetrics,
  OntologyHealthMetrics,
  GrowthMetrics,
  DriftDetectionResult,
};
