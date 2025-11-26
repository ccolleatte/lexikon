/**
 * RAG Integration Example
 * Shows how to use Lexikon for grounding cognitive-twin RAG pipeline
 */

import { LexikonClient } from '../src/LexikonClient';

/**
 * Use Lexikon semantic search to ground user query in RAG
 */
async function groundQueryWithLexikon(
  lexikon: LexikonClient,
  userQuery: string
): Promise<void> {
  console.log(`\nGrounding query: "${userQuery}"`);

  // Search Lexikon for semantically similar terms
  const results = await lexikon.semanticSearch(userQuery, {
    threshold: 0.65,
    topK: 10,
  });

  console.log(`Found ${results.length} grounding terms:`);
  results.forEach((term, i) => {
    console.log(
      `  ${i + 1}. ${term.name} (similarity: ${(term.similarity * 100).toFixed(1)}%)`
    );
    console.log(`     Definition: ${term.definition || 'N/A'}`);
  });

  // These terms now serve as:
  // - Context for retrieval augmentation
  // - Keywords for knowledge base search
  // - Anchors for anecdote matching
  return results;
}

/**
 * Semantic routing based on ontology
 */
async function semanticRouting(
  lexikon: LexikonClient,
  userQuery: string
): Promise<string> {
  // Get term and its ontology context
  const results = await lexikon.semanticSearch(userQuery, {
    threshold: 0.7,
    topK: 1,
  });

  if (results.length === 0) {
    return 'general';
  }

  // Check its domain/context via relations
  const relations = await lexikon.getRelations(results[0].term_id, 'outgoing');

  // Route based on discovered domain
  if (relations.some((r) => r.relation_type === 'part_of')) {
    return 'specialized';
  }
  return 'general';
}

/**
 * Enhanced context from ontology
 */
async function enhanceContextWithOntology(
  lexikon: LexikonClient,
  primaryTerm: string
): Promise<void> {
  console.log(`\nEnhancing context for: ${primaryTerm}`);

  // Get direct relations
  const relations = await lexikon.getRelations(primaryTerm, 'both');
  console.log(`Direct relations: ${relations.length}`);

  // Infer broader context
  const broader = await lexikon.inferRelations(primaryTerm, ['transitive']);
  console.log(`Inferred context: ${broader.length} terms`);

  // Use for context window expansion in RAG
  const contextTerms = [
    ...relations.map((r) =>
      r.source_term_id === primaryTerm
        ? r.target_term_id
        : r.source_term_id
    ),
    ...broader.map((r) => r.target_term_id),
  ];

  console.log(`Total context terms: ${contextTerms.length}`);
  return contextTerms;
}

async function main() {
  const lexikon = new LexikonClient({
    baseUrl: 'http://localhost:8000',
    token: process.env.LEXIKON_JWT_TOKEN || 'your-token',
  });

  console.log('RAG Integration with Lexikon');
  console.log('='.repeat(50));

  try {
    // Example 1: Ground initial query
    await groundQueryWithLexikon(
      lexikon,
      'How do transformers work in machine learning?'
    );

    // Example 2: Semantic routing
    const route = await semanticRouting(
      lexikon,
      'Tell me about attention mechanisms'
    );
    console.log(`\nSemantic routing result: ${route}`);

    // Example 3: Enhance context
    await enhanceContextWithOntology(lexikon, 'transformer');

    console.log('\nRAG grounding complete!');
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
