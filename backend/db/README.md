# Lexikon Database Layer

This directory contains the database configuration and models for Lexikon, supporting both PostgreSQL (relational data) and Neo4j (ontology graph).

## Architecture

```
PostgreSQL (Relational)          Neo4j (Graph)
- Users                          - Term nodes
- Projects                       - Domain nodes
- Terms (metadata)               - Relationships:
- API Keys                         * IS_A (hypernymy)
- OAuth Accounts                   * PART_OF (meronymy)
- LLM Configs                      * SYNONYM_OF
                                   * RELATED_TO
```

## Quick Start

### 1. Start databases with Docker Compose

From the project root:

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port `5432`
- Neo4j Browser on port `7474`
- Neo4j Bolt on port `7687`

### 2. Initialize databases

```bash
cd backend
python init_databases.py
```

Or initialize individually:

```bash
# PostgreSQL only
python init_databases.py --postgres-only

# Neo4j only
python init_databases.py --neo4j-only
```

### 3. Verify connections

**PostgreSQL:**
```bash
psql -h localhost -U lexikon -d lexikon
# Password: dev-secret
```

**Neo4j Browser:**
Open http://localhost:7474
- Username: `neo4j`
- Password: `dev-secret`

## Files

### Core Modules

- **`postgres.py`** - SQLAlchemy models and connection
  - User, Project, Term tables
  - OAuth, API Key management
  - LLM configuration storage

- **`neo4j.py`** - Neo4j client wrapper
  - Term node operations
  - Relationship management (IS_A, PART_OF, etc.)
  - Graph traversal and suggestions
  - Analytics and statistics

### Migrations

- **`alembic.ini`** - Alembic configuration
- **`migrations/`** - Database migration scripts
  - `env.py` - Migration environment
  - `script.py.mako` - Migration template
  - `versions/` - Migration versions

### Initialization

- **`init.sql`** - Raw SQL schema (for reference)
- **`neo4j_init.cypher`** - Neo4j constraints and indexes
- **`init_postgres.py`** - PostgreSQL initialization script
- **`init_neo4j.py`** - Neo4j initialization script
- **`../init_databases.py`** - Unified initialization

## PostgreSQL Schema

### Core Tables

**users**
- Authentication and profile data
- Adoption level tracking
- Multi-language support

**projects**
- Project metadata
- Owner and member management
- Visibility settings (public/private)

**terms**
- Term definitions and metadata
- Levels: quick-draft, ready, expert
- Status: draft, ready, validated
- Extended fields (examples, synonyms, citations)

**oauth_accounts**
- Google, GitHub OAuth tokens
- Account linking

**api_keys**
- API key management for production-api tier
- Scopes and rate limiting

**llm_configs**
- User's LLM provider settings (BYOK)
- Encrypted API keys
- Model preferences

### Relationships

```
users 1 ─── * oauth_accounts
users 1 ─── * api_keys
users 1 ─── * projects (owned)
users * ─── * projects (members)
projects 1 ─── * terms
users 1 ─── * terms (created)
```

## Neo4j Schema

### Node Types

**Term**
```cypher
(:Term {
  id: String,        # UUID from PostgreSQL
  name: String,
  definition: String
})
```

**Domain**
```cypher
(:Domain {
  name: String,      # e.g., 'informatique'
  label_fr: String,
  label_en: String
})
```

### Relationship Types

**IS_A** - Hypernymy/Hyponymy
```cypher
(hyponym:Term)-[:IS_A {
  confidence: Float,  # 0.0 - 1.0
  source: String,     # 'user', 'llm', 'import'
  validated: Boolean
}]->(hypernym:Term)
```

**PART_OF** - Meronymy
```cypher
(part:Term)-[:PART_OF {
  confidence: Float,
  source: String,
  validated: Boolean
}]->(whole:Term)
```

**SYNONYM_OF** - Synonymy (bidirectional)
```cypher
(term1:Term)-[:SYNONYM_OF {
  confidence: Float,
  source: String
}]-(term2:Term)
```

**RELATED_TO** - General semantic relation
```cypher
(term1:Term)-[:RELATED_TO {
  relation_type: String,  # Custom type
  confidence: Float,
  source: String
}]->(term2:Term)
```

### Indexes and Constraints

```cypher
# Constraints
CREATE CONSTRAINT term_id_unique FOR (t:Term) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT domain_name_unique FOR (d:Domain) REQUIRE d.name IS UNIQUE;

# Indexes
CREATE INDEX term_name_index FOR (t:Term) ON (t.name);
CREATE INDEX term_definition_fulltext FOR (t:Term) ON (t.definition);
```

## Common Operations

### PostgreSQL with SQLAlchemy

```python
from db.postgres import SessionLocal, User, Term

# Create session
db = SessionLocal()

# Query users
user = db.query(User).filter(User.email == "user@example.com").first()

# Create term
new_term = Term(
    id=str(uuid.uuid4()),
    project_id=project.id,
    name="Ontologie",
    definition="...",
    created_by=user.id
)
db.add(new_term)
db.commit()
```

### Neo4j Graph Operations

```python
from db.neo4j import neo4j_client

# Create term node
neo4j_client.create_term_node(
    term_id="uuid-123",
    name="Ontologie",
    definition="..."
)

# Create IS_A relationship
neo4j_client.create_relationship(
    from_term_id="uuid-123",
    to_term_id="uuid-456",
    rel_type="IS_A",
    properties={"confidence": 0.95, "source": "user", "validated": True}
)

# Find related terms
relations = neo4j_client.get_relationships("uuid-123")
```

## Migrations

### Create new migration

```bash
cd backend
alembic revision --autogenerate -m "Add new field"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

## Environment Variables

Required in `.env` file:

```bash
# PostgreSQL
DATABASE_URL=postgresql://lexikon:dev-secret@localhost:5432/lexikon

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dev-secret
```

## Development vs Production

### Development (current)
- Docker Compose local databases
- Unencrypted connections
- Default passwords

### Production (Sprint 3+)
- Managed databases (e.g., AWS RDS + Neo4j Aura)
- SSL/TLS required
- Secrets from environment
- Connection pooling
- Backup strategies

## Troubleshooting

### PostgreSQL connection failed

```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Connect manually
docker exec -it lexikon-postgres psql -U lexikon -d lexikon
```

### Neo4j connection failed

```bash
# Check container
docker-compose ps

# Check logs
docker-compose logs neo4j

# Connect via browser
open http://localhost:7474
```

### Migration errors

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
python init_databases.py
```

## Performance Tips

### PostgreSQL

- Add indexes on frequently queried fields
- Use connection pooling in production
- Enable query logging for slow queries

### Neo4j

- Create indexes on frequently searched properties
- Use APOC procedures for complex operations
- Limit relationship depth in traversals
- Use `EXPLAIN` to analyze query plans

## Next Steps

After database setup:

1. **Authentication** - Implement JWT and OAuth2
2. **API Integration** - Update endpoints to use real databases
3. **Testing** - Write database integration tests
4. **Migration** - Migrate in-memory data to PostgreSQL
