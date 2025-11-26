/**
 * Lexikon HTTP Client for cognitive-twin integration
 * Provides type-safe access to all Lexikon REST APIs (SPRINT 2-4 features)
 *
 * Usage:
 * const client = new LexikonClient({
 *   baseUrl: 'http://localhost:8000',
 *   token: 'eyJhbGc...'
 * });
 *
 * // Semantic Search (Feature 1)
 * const results = await client.semanticSearch('query', { threshold: 0.7 });
 *
 * // Ontology Reasoning (Feature 2)
 * const relations = await client.createRelation(sourceId, targetId, 'broader');
 * const inferred = await client.inferRelations(sourceId, ['transitive']);
 *
 * // Vocabulary Extraction (Feature 4)
 * const extracted = await client.extractVocabulary(content, ['parentheses', 'bold']);
 *
 * // Bulk Import (Feature 3)
 * const stats = await client.bulkImport(content, 'json', 'upsert');
 *
 * // HITL Workflow (Feature 5)
 * const queue = await client.getReviewQueue();
 * await client.approveReview(reviewId, feedback, 0.95);
 *
 * // Analytics (Feature 6)
 * const metrics = await client.getUsageMetrics();
 */

export interface LexikonConfig {
  baseUrl: string;
  token?: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
}

export interface SearchResult {
  term_id: string;
  name: string;
  definition?: string;
  similarity: number;
  execution_time_ms: number;
}

export interface SearchResponse {
  success: boolean;
  data: {
    results: SearchResult[];
    total: number;
    execution_time_ms: number;
  };
}

export interface RelationResponse {
  id: string;
  source_term_id: string;
  target_term_id: string;
  relation_type: string;
  confidence: number;
  created_at: string;
}

export interface InferredRelation {
  source_term_id: string;
  target_term_id: string;
  relation_type: string;
  confidence: number;
  path_length: number;
  inferred_via: string[];
}

export interface InferenceResponse {
  success: boolean;
  data: {
    inferred_relations: InferredRelation[];
    total_inferred: number;
  };
}

export interface ExtractedTerm {
  text: string;
  definition: string;
  pattern: string;
  confidence: number;
}

export interface ExtractionResponse {
  success: boolean;
  data: {
    extracted_terms: ExtractedTerm[];
    total_extracted: number;
    execution_time_ms: number;
  };
}

export interface ImportStats {
  created: number;
  updated: number;
  skipped: number;
  total: number;
  errors?: string[];
}

export interface BulkImportResponse {
  success: boolean;
  data: {
    import_stats: ImportStats;
  };
}

export interface ReviewItem {
  id: string;
  term_id: string;
  review_type: string;
  status: string;
  feedback?: string;
  created_at: string;
}

export interface QueueResponse {
  success: boolean;
  data: ReviewItem[];
  total: number;
}

export interface QueueMetrics {
  pending: number;
  approved: number;
  rejected: number;
  total: number;
}

export interface UsageMetrics {
  total_terms: number;
  terms_by_level: Record<string, number>;
  terms_by_status: Record<string, number>;
  total_relations: number;
}

export interface OntologyHealthMetrics {
  embedding_coverage_percent: number;
  relation_coverage_percent: number;
  avg_confidence: number;
  distinct_domains: number;
}

export interface GrowthMetrics {
  terms_added: number;
  relations_added: number;
  daily_average_terms: number;
  daily_average_relations: number;
}

export interface DriftDetectionResult {
  status: 'healthy' | 'drifting';
  isolated_terms_count: number;
  isolated_terms: string[];
  threshold: number;
}

export interface LexikonError extends Error {
  statusCode?: number;
  response?: any;
  retryable: boolean;
}

/**
 * Lexikon HTTP Client
 * Type-safe client for all Lexikon REST APIs
 */
export class LexikonClient {
  private baseUrl: string;
  private token?: string;
  private timeout: number;
  private retryAttempts: number;
  private retryDelay: number;

  constructor(config: LexikonConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.token = config.token;
    this.timeout = config.timeout || 30000;
    this.retryAttempts = config.retryAttempts || 3;
    this.retryDelay = config.retryDelay || 1000;
  }

  /**
   * Update authentication token
   */
  setToken(token: string) {
    this.token = token;
  }

  /**
   * Make HTTP request with retry logic
   */
  private async request<T>(
    method: string,
    endpoint: string,
    body?: any,
    options?: { retryable?: boolean }
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    let lastError: LexikonError | null = null;
    const isRetryable = options?.retryable !== false;
    const maxAttempts = isRetryable ? this.retryAttempts : 1;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const response = await fetch(url, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined,
          signal: AbortSignal.timeout(this.timeout),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const error: LexikonError = new Error(
            errorData?.error?.message || `HTTP ${response.status}: ${response.statusText}`
          ) as LexikonError;
          error.statusCode = response.status;
          error.response = errorData;
          error.retryable = response.status >= 500 || response.status === 429;

          // Don't retry on 401/403
          if (response.status === 401 || response.status === 403) {
            throw error;
          }

          if (!error.retryable || attempt === maxAttempts) {
            throw error;
          }

          lastError = error;
          await this.delay(this.retryDelay * attempt);
          continue;
        }

        return await response.json();
      } catch (error) {
        if (error instanceof LexikonError) {
          throw error;
        }

        const clientError: LexikonError = new Error(
          error instanceof Error ? error.message : 'Unknown error'
        ) as LexikonError;
        clientError.retryable =
          error instanceof TypeError && error.message.includes('fetch');

        if (!clientError.retryable || attempt === maxAttempts) {
          throw clientError;
        }

        lastError = clientError;
        await this.delay(this.retryDelay * attempt);
      }
    }

    throw lastError || new Error('Request failed after retries');
  }

  private async delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * FEATURE 1: Semantic Search API
   * Search terms by semantic similarity
   */
  async semanticSearch(
    query: string,
    options?: {
      threshold?: number;
      topK?: number;
    }
  ): Promise<SearchResult[]> {
    const response = await this.request<SearchResponse>('POST', '/api/terms/search', {
      query,
      threshold: options?.threshold ?? 0.5,
      top_k: options?.topK ?? 10,
    });

    return response.data.results;
  }

  /**
   * FEATURE 2: Ontology Reasoning - Create Relations
   * Create a new relation between terms
   */
  async createRelation(
    sourceTermId: string,
    targetTermId: string,
    relationType: string,
    confidence?: number
  ): Promise<RelationResponse> {
    const response = await this.request<RelationResponse>(
      'POST',
      '/api/ontology/relations',
      {
        source_term_id: sourceTermId,
        target_term_id: targetTermId,
        relation_type: relationType,
        confidence: confidence ?? 1.0,
      }
    );

    return response;
  }

  /**
   * FEATURE 2: Ontology Reasoning - Query Relations
   * Get relations for a term
   */
  async getRelations(
    termId: string,
    direction?: 'outgoing' | 'incoming' | 'both'
  ): Promise<RelationResponse[]> {
    const response = await this.request<{ success: boolean; data: RelationResponse[] }>(
      'GET',
      `/api/ontology/relations/${termId}?direction=${direction || 'both'}`
    );

    return response.data;
  }

  /**
   * FEATURE 2: Ontology Reasoning - Delete Relation
   * Delete a term relation
   */
  async deleteRelation(relationId: string): Promise<void> {
    await this.request('DELETE', `/api/ontology/relations/${relationId}`);
  }

  /**
   * FEATURE 2: Ontology Reasoning - Infer Relations
   * Use reasoning engine to infer new relations
   */
  async inferRelations(
    sourceTermId: string,
    rules?: string[],
    maxDepth?: number
  ): Promise<InferredRelation[]> {
    const response = await this.request<InferenceResponse>(
      'POST',
      '/api/ontology/infer',
      {
        source_term_id: sourceTermId,
        rules: rules || ['transitive', 'symmetric'],
        max_depth: maxDepth || 3,
      }
    );

    return response.data.inferred_relations;
  }

  /**
   * FEATURE 4: Vocabulary Extraction
   * Extract terms from document content
   */
  async extractVocabulary(
    content: string,
    patterns?: string[],
    language?: string
  ): Promise<ExtractedTerm[]> {
    const response = await this.request<ExtractionResponse>(
      'POST',
      '/api/vocabularies/extract',
      {
        content,
        patterns: patterns || ['parentheses', 'bold', 'glossary'],
        language: language || 'fr',
      }
    );

    return response.data.extracted_terms;
  }

  /**
   * FEATURE 3: Bulk Import
   * Import terms from JSON, CSV, or RDF/SKOS
   */
  async bulkImport(
    content: string,
    format: 'json' | 'csv' | 'skos',
    mode?: 'create_only' | 'update_only' | 'upsert'
  ): Promise<ImportStats> {
    const response = await this.request<BulkImportResponse>(
      'POST',
      '/api/vocabularies/bulk-import',
      {
        content,
        format,
        mode: mode || 'upsert',
      }
    );

    return response.data.import_stats;
  }

  /**
   * FEATURE 5: HITL Workflow - Get Review Queue
   * Get pending reviews
   */
  async getReviewQueue(
    status?: string,
    limit?: number
  ): Promise<ReviewItem[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (limit) params.append('limit', String(limit));

    const response = await this.request<QueueResponse>(
      'GET',
      `/api/hitl/queue?${params.toString()}`
    );

    return response.data;
  }

  /**
   * FEATURE 5: HITL Workflow - Create Review Request
   * Create a review request for quality assurance
   */
  async createReview(
    termId: string,
    reviewType: string
  ): Promise<{ id: string }> {
    const response = await this.request<{ success: boolean; data: { id: string } }>(
      'POST',
      '/api/hitl/reviews',
      {
        term_id: termId,
        review_type: reviewType,
      }
    );

    return response.data;
  }

  /**
   * FEATURE 5: HITL Workflow - Approve Review
   * Approve a review with feedback
   */
  async approveReview(
    reviewId: string,
    feedback?: string,
    confidence?: number
  ): Promise<void> {
    await this.request('POST', `/api/hitl/reviews/${reviewId}/approve`, {
      feedback,
      confidence_score: confidence,
    });
  }

  /**
   * FEATURE 5: HITL Workflow - Reject Review
   * Reject a review with feedback
   */
  async rejectReview(
    reviewId: string,
    feedback?: string,
    confidence?: number
  ): Promise<void> {
    await this.request('POST', `/api/hitl/reviews/${reviewId}/reject`, {
      feedback,
      confidence_score: confidence,
    });
  }

  /**
   * FEATURE 5: HITL Workflow - Queue Metrics
   * Get review queue statistics
   */
  async getQueueMetrics(): Promise<QueueMetrics> {
    const response = await this.request<{ success: boolean; data: QueueMetrics }>(
      'GET',
      '/api/hitl/queue/metrics'
    );

    return response.data;
  }

  /**
   * FEATURE 6: Analytics - Usage Metrics
   * Get vocabulary usage statistics
   */
  async getUsageMetrics(days?: number): Promise<UsageMetrics> {
    const response = await this.request<{ success: boolean; data: UsageMetrics }>(
      'GET',
      `/api/metrics/usage${days ? `?days=${days}` : ''}`
    );

    return response.data;
  }

  /**
   * FEATURE 6: Analytics - Ontology Health
   * Get ontology quality metrics
   */
  async getOntologyHealth(): Promise<OntologyHealthMetrics> {
    const response = await this.request<{ success: boolean; data: OntologyHealthMetrics }>(
      'GET',
      '/api/metrics/ontology-health'
    );

    return response.data;
  }

  /**
   * FEATURE 6: Analytics - Growth Metrics
   * Get growth tracking over time
   */
  async getGrowthMetrics(days?: number): Promise<GrowthMetrics> {
    const response = await this.request<{ success: boolean; data: GrowthMetrics }>(
      'GET',
      `/api/metrics/growth${days ? `?days=${days}` : ''}`
    );

    return response.data;
  }

  /**
   * FEATURE 6: Analytics - Vocabulary Drift Detection
   * Identify isolated/drifting terms
   */
  async detectDrift(threshold?: number): Promise<DriftDetectionResult> {
    const response = await this.request<{ success: boolean; data: DriftDetectionResult }>(
      'GET',
      `/api/metrics/drift-detection${threshold ? `?threshold=${threshold}` : ''}`
    );

    return response.data;
  }
}

/**
 * Factory function for easier instantiation
 */
export function createLexikonClient(config: LexikonConfig): LexikonClient {
  return new LexikonClient(config);
}

export default LexikonClient;
