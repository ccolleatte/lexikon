/**
 * Example: Integrating Lexikon Client with Cognitive Twin
 *
 * This example shows how to use the Lexikon HTTP client in cognitive-twin
 * to replace the embedded @cognitive-twin/lexique package.
 */

import { LexikonClient, SearchResponse, InferenceResponse } from '@lexikon/client';

/**
 * Lexicon Service for Cognitive Twin
 * Bridges Cognitive Twin's RAG layer with Lexikon's microservice
 */
export class CognitiveTwinLexiconService {
  private lexikon: LexikonClient;

  constructor(
    baseUrl: string = 'http://localhost:8000',
    accessToken: string
  ) {
    this.lexikon = new LexikonClient({
      baseUrl,
      accessToken,
      retryAttempts: 3,
      timeout: 30000,
    });
  }

  /**
   * Layer 1: Anecdotes + Semantic Search
   * Find relevant vocabulary entries by semantic similarity
   */
  async findRelevantVocabulary(query: string, threshold = 0.7): Promise<SearchResponse> {
    console.log(`[Lexikon] Searching vocabulary: "${query}"`);

    const response = await this.lexikon.semanticSearch(query, {
      threshold,
      top_k: 10,
    });

    console.log(`[Lexikon] Found ${response.data?.results.length || 0} matching terms`);
    return response;
  }

  /**
   * Layer 2: Knowledge Base Enrichment
   * Infer related terms to expand context
   */
  async expandVocabularyContext(termId: string): Promise<InferenceResponse> {
    console.log(`[Lexikon] Inferring relations for term: ${termId}`);

    const response = await this.lexikon.inferRelations({
      source_term_id: termId,
      rules: ['transitive', 'symmetric'],
      max_depth: 2,
    });

    const inferredCount = response.data?.inferred_relations.length || 0;
    console.log(`[Lexikon] Inferred ${inferredCount} related terms`);
    return response;
  }

  /**
   * Batch import vocabulary from external sources
   */
  async importExternalVocabulary(
    csvContent: string,
    source: string = 'external'
  ): Promise<void> {
    console.log(`[Lexikon] Importing vocabulary from ${source}`);

    const result = await this.lexikon.importFromCSV(csvContent, 'upsert');

    console.log(`[Lexikon] Import complete:
      - Created: ${result.data?.import_stats.created}
      - Updated: ${result.data?.import_stats.updated}
      - Skipped: ${result.data?.import_stats.skipped}`);
  }

  /**
   * Extract vocabulary from unstructured documents
   */
  async extractVocabularyFromDocument(
    documentContent: string,
    language: 'fr' | 'en' = 'fr'
  ): Promise<void> {
    console.log(`[Lexikon] Extracting vocabulary (language: ${language})`);

    const result = await this.lexikon.extractVocabulary(documentContent, {
      patterns: ['parentheses', 'bold', 'glossary', 'inline'],
      language,
    });

    const terms = result.data?.extracted_terms || [];
    console.log(`[Lexikon] Extracted ${terms.length} terms with patterns:`);
    terms.forEach((term) => {
      console.log(`  - "${term.text}" (${term.pattern}, confidence: ${term.confidence.toFixed(2)})`);
    });
  }

  /**
   * Quality validation workflow
   * Submit terms for human review
   */
  async submitForReview(
    termId: string,
    reviewType: 'relation_quality' | 'term_clarity' | 'embedding_accuracy'
  ): Promise<void> {
    console.log(`[Lexikon] Submitting term ${termId} for ${reviewType} review`);

    const review = await this.lexikon.createReview({
      term_id: termId,
      review_type: reviewType,
    });

    console.log(`[Lexikon] Review created: ${review.id}`);
  }

  /**
   * Get ontology health status
   */
  async checkOntologyHealth(): Promise<void> {
    const health = await this.lexikon.getOntologyHealth();
    const metrics = health.data;

    console.log('[Lexikon] Ontology Health Status:');
    console.log(`  - Embedding Coverage: ${metrics.embedding_coverage_percent.toFixed(1)}%`);
    console.log(`  - Relation Coverage: ${metrics.relation_coverage_percent.toFixed(1)}%`);
    console.log(`  - Avg Confidence: ${metrics.avg_confidence.toFixed(2)}`);
    console.log(`  - Distinct Domains: ${metrics.distinct_domains}`);
  }

  /**
   * Detect vocabulary drift
   */
  async checkForDrift(): Promise<void> {
    const drift = await this.lexikon.detectVocabularyDrift(0.8);
    const result = drift.data;

    console.log(`[Lexikon] Vocabulary Drift Status: ${result.status}`);
    if (result.status === 'drifting') {
      console.log(`  - ${result.isolated_terms_count} isolated terms found`);
      console.log(`  - Threshold: ${result.threshold}`);
    }
  }

  /**
   * Get usage statistics for dashboard
   */
  async getUsageStats(): Promise<void> {
    const usage = await this.lexikon.getUsageMetrics(30);
    const metrics = usage.data;

    console.log('[Lexikon] Usage Metrics (Last 30 Days):');
    console.log(`  - Total Terms: ${metrics.total_terms}`);
    console.log(`  - Total Relations: ${metrics.total_relations}`);
    console.log(`  - Distribution by Level:`);
    Object.entries(metrics.terms_by_level).forEach(([level, count]) => {
      console.log(`    - ${level}: ${count}`);
    });
  }

  /**
   * Set new authentication token
   */
  setAuthToken(accessToken: string, refreshToken?: string): void {
    this.lexikon.setToken(accessToken, refreshToken);
  }
}

// ============================================================================
// Usage Example in Cognitive Twin
// ============================================================================

async function example() {
  // Initialize service
  const lexicon = new CognitiveTwinLexiconService(
    'http://localhost:8000',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  );

  try {
    // 1. Find relevant vocabulary for a query
    console.log('\n=== Finding Relevant Vocabulary ===');
    const searchResult = await lexicon.findRelevantVocabulary('semantic web ontology');

    // 2. Expand context with inferred relations
    console.log('\n=== Expanding Context ===');
    if (searchResult.data?.results[0]) {
      const firstTermId = searchResult.data.results[0].term_id;
      await lexicon.expandVocabularyContext(firstTermId);
    }

    // 3. Extract vocabulary from document
    console.log('\n=== Extracting Vocabulary ===');
    const document = `
      Le Semantic Web (Web de données) est une extension du Web classique.
      Une **Ontologie** est une spécification formelle d'une conceptualisation partagée.
      Knowledge Graph: Un modèle sémantique de large échelle
      Le RAG signifie Retrieval-Augmented Generation
    `;
    await lexicon.extractVocabularyFromDocument(document, 'fr');

    // 4. Check ontology health
    console.log('\n=== Checking Ontology Health ===');
    await lexicon.checkOntologyHealth();

    // 5. Check for drift
    console.log('\n=== Checking for Vocabulary Drift ===');
    await lexicon.checkForDrift();

    // 6. Get usage statistics
    console.log('\n=== Usage Statistics ===');
    await lexicon.getUsageStats();

  } catch (error) {
    console.error('[Error]', error instanceof Error ? error.message : error);
  }
}

// Export for use in cognitive-twin
export { CognitiveTwinLexiconService };

// Uncomment to run example
// example();
