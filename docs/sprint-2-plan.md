# Sprint 2 - Plan d'Exécution

**Durée estimée:** 2-3 semaines
**Objectif:** Transformer le MVP Sprint 1 en application production-ready avec persistence réelle, authentification, et intelligence artificielle.

## Vue d'ensemble

Sprint 2 apporte les fonctionnalités critiques pour passer d'un prototype fonctionnel à une application professionnelle capable de gérer de vrais utilisateurs et projets complexes.

## Features principales (6)

### 1. Database Layer - PostgreSQL + Neo4j
**Priorité:** CRITIQUE (foundation pour tout le reste)
**Durée estimée:** 3-4 jours

**PostgreSQL** - Données relationnelles:
- Tables: `users`, `terms`, `projects`, `sessions`, `api_keys`
- Relations: user ↔ projects, projects ↔ terms
- Indexes: email (unique), term names par projet
- Migrations: Alembic pour versioning

**Neo4j** - Graphe ontologique:
- Nodes: `Term`, `Concept`, `Domain`
- Relationships: `IS_A`, `PART_OF`, `RELATED_TO`, `SYNONYM_OF`
- Properties: confidence scores, sources, validation status
- Cypher queries pour découverte de relations

**Migration depuis in-memory:**
- Script de migration des données existantes
- Dual-mode: support simultané in-memory + DB pendant transition
- Rollback plan si problèmes

**Livrables:**
```
backend/
├── db/
│   ├── postgres.py          # PostgreSQL connection, models SQLAlchemy
│   ├── neo4j.py             # Neo4j driver, Cypher helpers
│   ├── migrations/          # Alembic migrations
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       └── 002_add_api_keys.py
│   └── init.sql             # Initial schema SQL
└── requirements.txt         # + psycopg2-binary, neo4j-driver, alembic
```

---

### 2. Authentication & Authorization
**Priorité:** CRITIQUE
**Durée estimée:** 2-3 jours

**JWT Authentication:**
- Token generation avec python-jose
- Refresh tokens (7 jours) + access tokens (1 heure)
- Middleware de validation sur routes protégées
- Password hashing avec bcrypt

**OAuth2 Providers:**
- Google OAuth2
- GitHub OAuth2
- Stratégie: Authlib pour gestion uniforme
- Link accounts: merge Google + email/password

**API Keys (pour adoption "production-api"):**
- Génération de clés API persistantes
- Rate limiting par clé
- Scopes: read-only vs read-write

**Livrables:**
```
backend/
├── auth/
│   ├── jwt.py               # Token generation, validation
│   ├── oauth.py             # Google + GitHub OAuth flows
│   ├── middleware.py        # Route protection
│   └── api_keys.py          # API key management
└── requirements.txt         # + python-jose, passlib, authlib

frontend/
└── src/
    ├── lib/
    │   ├── stores/auth.ts   # Auth state management
    │   └── utils/auth.ts    # Login/logout helpers
    └── routes/
        ├── login/+page.svelte
        ├── register/+page.svelte
        └── oauth/callback/+page.svelte
```

---

### 3. AI Relation Suggestions
**Priorité:** HAUTE (différentiateur clé)
**Durée estimée:** 3-4 jours

**LLM Integration - BYOK (Bring Your Own Key):**
- Support multi-providers: OpenAI, Anthropic, Mistral, Ollama (local)
- Configuration par utilisateur stockée chiffrée
- Fallback gratuit: modèles légers via Hugging Face Inference API

**Relation Discovery:**
- Prompt engineering pour extraction de relations:
  - Synonymes
  - Hyponymes/Hyperonymes (IS_A)
  - Méronymie (PART_OF)
  - Relations domaine-spécifiques
- Scoring de confiance (0.0-1.0)
- Batch processing pour performance

**Human-in-the-Loop Validation:**
- UI pour review des suggestions
- Accept/Reject/Edit workflow
- Feedback loop pour améliorer prompts

**Livrables:**
```
backend/
├── ai/
│   ├── providers/
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── mistral.py
│   │   └── ollama.py
│   ├── relation_suggester.py  # Core logic
│   ├── prompts.py             # Prompt templates
│   └── confidence.py          # Scoring algorithms
└── api/
    └── relations.py           # POST /api/relations/suggest

frontend/
└── src/routes/
    └── terms/[id]/
        └── relations/+page.svelte  # Validation UI
```

---

### 4. Import / Export
**Priorité:** MOYENNE
**Durée estimée:** 2-3 jours

**Import Formats:**
- CSV (simple: term, definition, domain)
- JSON-LD (Linked Data standard)
- RDF/Turtle (ontologies existantes)
- Custom JSON (backup/restore)

**Export Formats:**
- CSV (compatible Excel)
- JSON-LD (publication Linked Data)
- RDF/XML (interopérabilité)
- Graphviz DOT (visualisation)

**Validation:**
- Schema validation avant import
- Duplicate detection
- Conflict resolution UI

**Livrables:**
```
backend/
├── importers/
│   ├── csv_importer.py
│   ├── jsonld_importer.py
│   └── rdf_importer.py
├── exporters/
│   ├── csv_exporter.py
│   ├── jsonld_exporter.py
│   └── rdf_exporter.py
└── api/
    ├── import.py              # POST /api/projects/{id}/import
    └── export.py              # GET /api/projects/{id}/export?format=csv

frontend/
└── src/routes/
    └── projects/[id]/
        ├── import/+page.svelte
        └── export/+page.svelte
```

---

### 5. Projects & Collaboration
**Priorité:** MOYENNE
**Durée estimée:** 2 jours

**Multi-Project Support:**
- Create/list/archive projects
- Switch between projects
- Project-level settings (language, domain, visibility)

**Team Collaboration:**
- Invite users by email
- Roles: Owner, Editor, Reviewer, Viewer
- Activity log par projet
- Comments sur termes

**Livrables:**
```
backend/
├── db/postgres.py           # + projects, project_members tables
└── api/
    ├── projects.py
    └── members.py

frontend/
└── src/routes/
    ├── projects/+page.svelte
    ├── projects/[id]/+page.svelte
    └── projects/[id]/settings/+page.svelte
```

---

### 6. Advanced Term Management
**Priorité:** MOYENNE
**Durée estimée:** 2 jours

**Enhanced Creation Flow:**
- Level 2 (Ready): Add examples, synonyms, related terms
- Level 3 (Expert): Add formal definition, citations, metadata

**Search & Filter:**
- Full-text search sur name + definition
- Filter par domain, status, level
- Sort par date, alphabétique, usage

**Bulk Operations:**
- Bulk status change (draft → ready)
- Bulk delete
- Bulk export

**Livrables:**
```
frontend/
└── src/routes/
    └── terms/
        ├── new/ready/+page.svelte       # Level 2
        ├── new/expert/+page.svelte      # Level 3
        └── search/+page.svelte          # Advanced search
```

---

## Timeline - 3 semaines

### Semaine 1: Fondations (Database + Auth)
**Jours 1-2:** PostgreSQL + Neo4j setup
- Schemas, models SQLAlchemy, Cypher queries
- Migration scripts
- Tests de connexion

**Jours 3-4:** Authentication complète
- JWT implementation
- OAuth2 Google + GitHub
- Frontend login/register flows

**Jour 5:** API Keys + Middleware
- Génération de clés
- Protection des routes
- Tests end-to-end auth

### Semaine 2: Intelligence & Import/Export
**Jours 1-3:** AI Relations
- LLM provider abstraction
- Relation suggestion algorithm
- Validation UI

**Jours 4-5:** Import/Export
- CSV + JSON-LD support
- Validation + error handling
- Tests avec datasets réels

### Semaine 3: Collaboration & Polish
**Jours 1-2:** Projects & Teams
- Multi-project backend
- Invitation system
- Project switcher UI

**Jours 3-4:** Advanced Term Management
- Level 2/3 creation flows
- Search functionality
- Bulk operations

**Jour 5:** Testing, Documentation, Deployment
- End-to-end tests
- Update documentation
- Deployment guide (Docker Compose)

---

## Dépendances techniques nouvelles

### Backend (requirements.txt)
```
# Existing
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# NEW Sprint 2
# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
neo4j==5.14.1

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
authlib==1.3.0
python-multipart==0.0.6

# AI
openai==1.3.5
anthropic==0.7.1
mistralai==0.0.11
httpx==0.25.1  # For Ollama

# Import/Export
rdflib==7.0.0
pandas==2.1.3
```

### Frontend (package.json)
```json
{
  "dependencies": {
    // Existing...

    // NEW Sprint 2
    "@auth/sveltekit": "^0.5.0",  // SvelteKit Auth
    "date-fns": "^2.30.0",         // Date formatting
    "chart.js": "^4.4.0",          // Visualisations
    "svelte-chartjs": "^3.1.0"
  }
}
```

---

## Infrastructure & DevOps

### Docker Compose
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: lexikon
      POSTGRES_USER: lexikon
      POSTGRES_PASSWORD: dev-secret
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  neo4j:
    image: neo4j:5.14-community
    environment:
      NEO4J_AUTH: neo4j/dev-secret
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://lexikon:dev-secret@postgres:5432/lexikon
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: dev-secret
      JWT_SECRET: dev-jwt-secret-change-in-prod
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - neo4j

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  postgres_data:
  neo4j_data:
```

---

## Testing Strategy

### Backend Tests
- Unit tests: pytest pour chaque module
- Integration tests: TestClient FastAPI
- Database tests: fixtures avec DB temporaire
- E2E tests: Playwright pour flows complets

### Frontend Tests
- Component tests: Vitest + Testing Library
- E2E tests: Playwright
- Accessibility: axe-core

---

## Migration Plan (Sprint 1 → Sprint 2)

### Backward Compatibility
1. **Dual Mode:** Backend supporte simultanément in-memory + DB
2. **Feature Flags:** Environment variable `USE_DATABASE=true/false`
3. **Data Migration:** Script pour copier données in-memory → PostgreSQL
4. **Deprecation:** Warning si in-memory mode après Sprint 2

### Rollback Strategy
- Git tags pour chaque feature
- Database snapshots avant migrations
- Feature flags permettent disable AI/Import si bugs

---

## Risques & Mitigation

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Neo4j learning curve | Planning underestimat | Start avec queries simples, complexifier progressivement |
| LLM API costs | Budget dépassé | BYOK + rate limiting strict |
| OAuth callback complexité | Auth delays | Tester OAuth en premier jour auth |
| Import data corruption | Perte de données | Validation stricte + dry-run mode |
| Performance avec graphe | Slowdowns | Indexing Neo4j + caching |

---

## Success Metrics

- [ ] Users peuvent s'authentifier via email + Google + GitHub
- [ ] PostgreSQL stocke 1000+ termes sans ralentissement
- [ ] Neo4j suggère relations avec >70% precision
- [ ] Import CSV de 500 lignes en <5 secondes
- [ ] Export JSON-LD valide selon schema.org
- [ ] Multi-projet: switch en <100ms
- [ ] Tests E2E passent à 100%
- [ ] Documentation complète pour déploiement production

---

## Après Sprint 2

**Sprint 3 potentiel:**
- Visualisation graphe interactive (D3.js, Cytoscape)
- API publique avec documentation OpenAPI
- Webhooks pour intégrations externes
- Mobile app (React Native)
- Advanced analytics dashboard
