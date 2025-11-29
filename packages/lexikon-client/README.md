# @cognitive-twin/lexikon-client

Type-safe HTTP client for **Lexikon v0.5.0** REST APIs, enabling cognitive-twin to consume all advanced ontology/vocabulary management features.

## Features

Covers all SPRINT 2-4 features:

- **Feature 1: Semantic Search** - Vector-based term similarity search
- **Feature 2: Ontology Reasoning** - Graph-based relation inference  
- **Feature 3: Bulk Import** - Multi-format vocabulary import
- **Feature 4: Vocabulary Extraction** - Pattern-based term extraction
- **Feature 5: HITL Workflow** - Human-in-the-loop review queue
- **Feature 6: Analytics & Metrics** - Ontology health monitoring

## Quick Start

```typescript
import { LexikonClient } from '@cognitive-twin/lexikon-client';

const lexikon = new LexikonClient({
  baseUrl: 'http://localhost:8000',
  token: 'jwt-token'
});

// Semantic search
const results = await lexikon.semanticSearch('query', { threshold: 0.7 });

// Create relations
await lexikon.createRelation('term-1', 'term-2', 'broader');

// Extract vocabulary
const terms = await lexikon.extractVocabulary(content, ['parentheses']);

// Get metrics
const health = await lexikon.getOntologyHealth();
```

## Installation

```bash
npm install @cognitive-twin/lexikon-client
```

## License

AGPL-3.0
