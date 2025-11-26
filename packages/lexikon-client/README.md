# Lexikon Client

TypeScript HTTP client library for Lexikon REST API. Provides complete type-safe access to all 6 SPRINT 2-4 features.

## Installation

```bash
npm install @lexikon/client
```

## Quick Start

```typescript
import { LexikonClient } from '@lexikon/client';

// Initialize client
const client = new LexikonClient({
  baseUrl: 'http://localhost:8000',
  accessToken: 'your-jwt-token'
});

// Feature 1: Semantic Search
const results = await client.semanticSearch('web semantic data', {
  threshold: 0.7,
  top_k: 5
});

// Feature 2: Ontology Reasoning
const inferred = await client.inferRelations({
  source_term_id: 'term-123',
  rules: ['transitive', 'symmetric'],
  max_depth: 3
});

// Feature 3: Bulk Import
const importResult = await client.importFromJSON([
  { name: 'Machine Learning', definition: 'AI subset...' },
  { name: 'Deep Learning', definition: 'ML subset...' }
]);

// Feature 4: Vocabulary Extraction
const extracted = await client.extractVocabulary(`
  Semantic Web (A web of data)
  **Knowledge Graph** - A semantic model
  Ontology: A formal representation
`);

// Feature 5: HITL Workflow
const review = await client.createReview({
  term_id: 'term-123',
  review_type: 'term_clarity'
});

// Feature 6: Analytics
const health = await client.getOntologyHealth();
const drift = await client.detectVocabularyDrift();
```

## Features

### Feature 1: Semantic Search
Search for terms by semantic similarity using embeddings.

```typescript
const results = await client.semanticSearch(query, {
  threshold: 0.5,  // Similarity threshold (0-1)
  top_k: 10        // Number of results
});
```

### Feature 2: Ontology Reasoning
Create relations and infer new relations using transitive, symmetric, equivalence rules.

```typescript
// Create relation
const relation = await client.createRelation({
  source_term_id: 'term-1',
  target_term_id: 'term-2',
  relation_type: 'broader',
  confidence: 0.95
});

// Infer relations
const inferred = await client.inferRelations({
  source_term_id: 'term-1',
  rules: ['transitive', 'symmetric'],
  max_depth: 3
});
```

### Feature 3: Bulk Import
Import terms from JSON, CSV, or RDF/SKOS formats.

```typescript
// From JSON
await client.importFromJSON([
  { name: 'Term 1', definition: 'Def 1', domain: 'Domain' },
  { name: 'Term 2', definition: 'Def 2', level: 'ready' }
], 'upsert');

// From CSV
await client.importFromCSV(`
name,definition,domain,level,status
Machine Learning,AI subset,AI,ready,draft
Deep Learning,ML subset,AI,expert,validated
`, 'upsert');
```

### Feature 4: Vocabulary Extraction
Extract terms from document content using pattern matching.

```typescript
const extracted = await client.extractVocabulary(documentContent, {
  patterns: ['parentheses', 'bold', 'glossary', 'inline'],
  language: 'fr'  // French pattern support
});
```

### Feature 5: HITL Workflow
Manage human-in-the-loop review queue for quality validation.

```typescript
// Create review request
const review = await client.createReview({
  term_id: 'term-123',
  review_type: 'term_clarity'  // or 'relation_quality', 'embedding_accuracy'
});

// Get pending reviews
const queue = await client.getReviewQueue('pending', 20);

// Approve/Reject
await client.approveReview(reviewId, {
  feedback: 'Looks good',
  confidence_score: 0.95
});

// Queue metrics
const metrics = await client.getQueueMetrics();
```

### Feature 6: Analytics & Metrics
Comprehensive ontology health and usage metrics.

```typescript
// Usage statistics
const usage = await client.getUsageMetrics(30);  // Last 30 days

// Ontology health
const health = await client.getOntologyHealth();
// { embedding_coverage_percent, relation_coverage_percent, avg_confidence, ... }

// Growth tracking
const growth = await client.getGrowthMetrics(30);
// { terms_added, relations_added, daily_averages, ... }

// Drift detection
const drift = await client.detectVocabularyDrift(0.8);
// Identifies isolated terms (0 relations)
```

## Authentication

### JWT Bearer Token
```typescript
const client = new LexikonClient({
  baseUrl: 'http://localhost:8000',
  accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  refreshToken: 'refresh-token-for-auto-refresh'
});

// Set new token
client.setToken(newAccessToken, newRefreshToken);
```

### Token Refresh
The client automatically refreshes expired tokens if a `refreshToken` is provided.

## Error Handling

```typescript
import { LexikonClient, LexikonError } from '@lexikon/client';

try {
  const results = await client.semanticSearch('query');
} catch (error) {
  if (error instanceof LexikonError) {
    if (error.isAuthError()) {
      console.log('Authentication failed');
    } else if (error.isNotFoundError()) {
      console.log('Resource not found');
    } else if (error.isValidationError()) {
      console.log('Validation error:', error.details);
    } else {
      console.log('API error:', error.statusCode, error.message);
    }
  }
}
```

## Retry Logic

The client automatically retries failed requests with exponential backoff:

```typescript
const client = new LexikonClient({
  baseUrl: 'http://localhost:8000',
  accessToken: 'token',
  retryAttempts: 3,        // Number of retry attempts
  retryDelay: 1000,        // Initial retry delay (ms)
  timeout: 30000           // Request timeout (ms)
});
```

## Configuration

```typescript
interface ClientConfig {
  baseUrl: string;         // Lexikon API base URL
  accessToken?: string;    // JWT access token
  refreshToken?: string;   // Refresh token for auto-refresh
  retryAttempts?: number;  // Number of retry attempts (default: 3)
  retryDelay?: number;     // Retry delay in ms (default: 1000)
  timeout?: number;        // Request timeout in ms (default: 30000)
}
```

## Integration with Cognitive Twin

The lexikon-client can be consumed by cognitive-twin to replace the embedded `@cognitive-twin/lexique` package:

```typescript
// In cognitive-twin/packages/rag-core/src/services/lexicon.service.ts

import { LexikonClient } from '@lexikon/client';

export class LexiconService {
  private lexikon: LexikonClient;

  constructor(baseUrl: string, accessToken: string) {
    this.lexikon = new LexikonClient({ baseUrl, accessToken });
  }

  async searchVocabulary(query: string) {
    return this.lexikon.semanticSearch(query);
  }

  async getOntologyHealth() {
    return this.lexikon.getOntologyHealth();
  }

  // ... other methods
}
```

## Types

All TypeScript types are exported for type-safe integration:

```typescript
import {
  LexikonClient,
  SearchTermRequest,
  SearchResponse,
  CreateRelationRequest,
  InferenceResponse,
  BulkImportResponse,
  ExtractionResponse,
  ReviewQueueResponse,
  UsageMetrics
} from '@lexikon/client';
```

## License

AGPL-3.0 - See LICENSE file for details

## Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.
