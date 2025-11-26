/**
 * Basic usage example of Lexikon Client
 * Demonstrates all SPRINT 2-4 features
 */

import { LexikonClient } from '../src/LexikonClient';

async function main() {
  // Initialize Lexikon client
  const lexikon = new LexikonClient({
    baseUrl: 'http://localhost:8000',
    token: process.env.LEXIKON_JWT_TOKEN || 'your-jwt-token',
    timeout: 30000,
    retryAttempts: 3,
  });

  console.log('Lexikon Client - Basic Usage Examples');
  console.log('='.repeat(50));

  try {
    // 1. Semantic Search (Feature 1)
    console.log('\n1. Semantic Search');
    const searchResults = await lexikon.semanticSearch('machine learning', {
      threshold: 0.6,
      topK: 5,
    });
    console.log(`Found ${searchResults.length} similar terms`);
    searchResults.forEach((term) => {
      console.log(`  - ${term.name} (${(term.similarity * 100).toFixed(1)}%)`);
    });

    // 2. Create Relations (Feature 2)
    console.log('\n2. Create Relation');
    const relation = await lexikon.createRelation(
      'term-123',
      'term-456',
      'broader',
      0.95
    );
    console.log(`Created: ${relation.id}`);

    // 3. Infer Relations (Feature 2)
    console.log('\n3. Infer Relations');
    const inferred = await lexikon.inferRelations('term-123', ['transitive'], 3);
    console.log(`Inferred ${inferred.length} relations`);

    // 4. Extract Vocabulary (Feature 4)
    console.log('\n4. Extract Vocabulary');
    const content = 'The **semantic web** (a web for machines) uses ontologies.';
    const extracted = await lexikon.extractVocabulary(content, [
      'parentheses',
      'bold',
    ]);
    console.log(`Extracted ${extracted.length} terms`);

    // 5. Bulk Import (Feature 3)
    console.log('\n5. Bulk Import');
    const jsonData = JSON.stringify([
      {
        name: 'AI',
        definition: 'Artificial Intelligence',
        domain: 'Technology',
        level: 'expert',
        status: 'validated',
      },
    ]);
    const stats = await lexikon.bulkImport(jsonData, 'json', 'upsert');
    console.log(`Created: ${stats.created}, Updated: ${stats.updated}`);

    // 6. HITL Workflow (Feature 5)
    console.log('\n6. Review Queue');
    const queue = await lexikon.getReviewQueue('pending', 5);
    console.log(`Pending reviews: ${queue.length}`);

    // 7. Analytics (Feature 6)
    console.log('\n7. Ontology Health');
    const health = await lexikon.getOntologyHealth();
    console.log(`Embedding coverage: ${health.embedding_coverage_percent}%`);
    console.log(`Avg confidence: ${health.avg_confidence}`);

    console.log('\nAll examples completed successfully!');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
