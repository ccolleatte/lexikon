// Lexikon Neo4j Initialization Script
// This script creates indexes and constraints for the ontology graph

// Create constraints (unique IDs)
CREATE CONSTRAINT term_id_unique IF NOT EXISTS
FOR (t:Term) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT domain_name_unique IF NOT EXISTS
FOR (d:Domain) REQUIRE d.name IS UNIQUE;

// Create indexes for performance
CREATE INDEX term_name_index IF NOT EXISTS
FOR (t:Term) ON (t.name);

CREATE INDEX term_definition_fulltext IF NOT EXISTS
FOR (t:Term) ON (t.definition);

// Sample relationship types (for documentation)
// - IS_A: Hypernym/Hyponym (e.g., "Dog IS_A Animal")
// - PART_OF: Meronymy (e.g., "Wheel PART_OF Car")
// - RELATED_TO: General semantic relation
// - SYNONYM_OF: Synonymy (bidirectional)
// - ANTONYM_OF: Antonymy
// - DOMAIN_OF: Term belongs to domain

// Example: Create a few domain nodes for common domains
MERGE (d:Domain {name: 'philosophie'})
  SET d.label_fr = 'Philosophie',
      d.label_en = 'Philosophy';

MERGE (d:Domain {name: 'informatique'})
  SET d.label_fr = 'Informatique',
      d.label_en = 'Computer Science';

MERGE (d:Domain {name: 'linguistique'})
  SET d.label_fr = 'Linguistique',
      d.label_en = 'Linguistics';

MERGE (d:Domain {name: 'data-science'})
  SET d.label_fr = 'Science des Données',
      d.label_en = 'Data Science';

MERGE (d:Domain {name: 'sociologie'})
  SET d.label_fr = 'Sociologie',
      d.label_en = 'Sociology';

MERGE (d:Domain {name: 'psychologie'})
  SET d.label_fr = 'Psychologie',
      d.label_en = 'Psychology';
