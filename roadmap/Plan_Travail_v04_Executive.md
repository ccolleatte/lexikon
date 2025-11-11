# Plan de Travail v0.4 – Service d'Ontologies Lexicales
## Executive Summary avec Éléments Techniques Critiques

**Date** : 2025-11-11
**Statut** : Proposition enrichie post-analyse
**Budget** : €258k (6 mois)
**ROI attendu** : Break-even M18

---

## 1. Vision & Business Case

### 1.1 Problème Adressé
**30-40% d'erreurs sémantiques** dans les réponses LLM dues à l'ambiguïté terminologique.
Impact : €2M/an de révisions manuelles (entreprise moyenne).

### 1.2 Solution Proposée
**Plateforme générique** de création d'ontologies validées humainement, servant de couche sémantique entre humains et IA.

### 1.3 Marché et Positionnement
- **TAM** : €2.3B (2024)
- **SAM** : €450M (PME/Académique)
- **SOM** : €15M (Year 3)
- **Avantage compétitif** : HITL + Open source + API-first

---

## 2. Architecture Technique

### 2.1 Stack Validée

```yaml
Backend:
  - FastAPI (async, OpenAPI)
  - PostgreSQL 15 + pgvector
  - Neo4j Community (après POC)
  - Redis (cache, queues)
  - Celery (tasks async)

Frontend:
  - SvelteKit 2.0 (SSR, performance)
  - TailwindCSS + D3.js
  - TanStack Query

Infrastructure:
  - Docker Compose (dev)
  - Kubernetes (prod)
  - GitHub Actions (CI/CD)

Embeddings:
  - sentence-transformers/all-mpnet-base-v2
  - 768 dimensions
  - pgvector indexing (HNSW)
```

### 2.2 Décisions Critiques à Trancher (Sprint 1)

| Décision | Options | POC requis | Deadline |
|----------|---------|------------|----------|
| **Graph DB** | Neo4j vs PostgreSQL+AGE | Benchmark 100k nœuds | Week 2 |
| **Vector Store** | pgvector vs Weaviate | Test 1M embeddings | Week 3 |
| **Auth** | Auth0 vs Keycloak | Coût vs flexibilité | Week 4 |

---

## 3. Roadmap Réaliste

### Phase 1 : Foundation (8 semaines) → v0.1

**Objectif** : MVP technique avec ontologie SHS pilote

**Livrables** :
- ✅ Schéma DB complet (20+ tables)
- ✅ API REST (15+ endpoints)
- ✅ 300 termes validés avec relations
- ✅ Import/Export JSON
- ✅ Tests coverage > 80%

**Ressources** : 2 devs full-time + 1 expert domaine

**Budget** : €80k

**Go/No-Go** : API latency < 200ms, HITL workflow < 15min/terme

### Phase 2 : Validation (8 semaines) → v0.2

**Objectif** : Interface HITL et second domaine

**Livrables** :
- ✅ Interface web validation
- ✅ Workflow complet (proposition → validation)
- ✅ 2ème domaine actif (Juridique)
- ✅ Recherche sémantique
- ✅ Dashboard métriques

**Ressources** : +1 dev front, +1 UX

**Budget** : €80k

**Go/No-Go** : 500 termes, 10 validateurs actifs, NPS > 30

### Phase 3 : Integration (8 semaines) → v1.0

**Objectif** : Intégration LLM et production-ready

**Livrables** :
- ✅ API enrichissement LLM
- ✅ Benchmark -30% erreurs prouvé
- ✅ Export RDF/SKOS
- ✅ GraphQL API
- ✅ Documentation complète

**Ressources** : +1 ML engineer

**Budget** : €98k

**Go/No-Go** : 1000 req/s, 100 beta users, error reduction verified

---

## 4. Modèle de Données Critique

### 4.1 Tables Essentielles

```sql
-- Cœur ontologique
terms (id, label, domain_id, status, created_at)
definitions (term_id, version, short, long, context)
ontological_relations (source_id, target_id, type_id, strength)
relation_types (id, name, symmetric, transitive, inverse)

-- Validation HITL
validations (term_id, validator_id, decision, score, checklist)
validation_conflicts (term_id, validators[], resolution)

-- IA & Search
term_embeddings (term_id, vector[768], model)
llm_cache (query_hash, enriched_prompt, terms_detected)

-- Métadonnées
domains (id, name, parent_id)
authors (id, name, school)
citations (term_id, quote, source, doi)
```

### 4.2 Performance Cibles

| Métrique | Cible | Mesure |
|----------|-------|---------|
| API latency P95 | < 200ms | Prometheus |
| Search latency P95 | < 500ms | Benchmarks |
| Throughput | > 1000 req/s | k6 load tests |
| DB size @ 10k terms | < 10GB | Monitoring |

---

## 5. Intégration LLM Concrète

### 5.1 Pipeline d'Enrichissement

```python
async def enrich_prompt(prompt: str, domain: str = None):
    # 1. Détection termes (30ms)
    terms = await detect_terms(prompt)  # NER + fuzzy + semantic

    # 2. Construction graphe (50ms)
    graph = await build_context(terms, depth=2)

    # 3. Optimisation tokens (10ms)
    context = optimize_for_tokens(graph, max=2000)

    # 4. Injection (10ms)
    return format_as_jsonld(context)

# Total: < 100ms
```

### 5.2 Protocole Benchmark -30% Erreurs

1. **Dataset** : 100 prompts ambigus annotés
2. **Baseline** : LLM sans ontologie
3. **Test** : LLM avec enrichissement
4. **Évaluation** : 3 experts, blind review
5. **Métrique** : (erreurs_baseline - erreurs_enriched) / erreurs_baseline

---

## 6. Budget et Ressources

### 6.1 Budget 6 Mois

| Poste | Mensuel | Total |
|-------|---------|-------|
| **Salaires** (4-5 FTE) | €40k | €240k |
| **Infrastructure Cloud** | €2k | €12k |
| **Services** (Auth, monitoring) | €1k | €6k |
| **TOTAL** | €43k | **€258k** |

### 6.2 Équipe

| Phase | Backend | Frontend | ML/Data | Domain Expert | DevOps |
|-------|---------|----------|---------|---------------|--------|
| 1 | 2.0 | 0.5 | 0 | 0.5 | 0.5 |
| 2 | 1.5 | 1.0 | 0.5 | 1.0 | 0.2 |
| 3 | 1.0 | 0.5 | 1.0 | 0.5 | 0.5 |

---

## 7. Risques et Mitigation

| Risque | P | I | Mitigation | Plan B |
|--------|---|---|------------|--------|
| **HITL coût prohibitif** | H | H | • Gamification validation<br>• IA pré-remplit 60%<br>• Crowdsourcing | Validation communautaire |
| **Complexité technique** | M | H | • POC Sprint 1<br>• Architecture modulaire<br>• Over-engineering évité | Simplification scope |
| **Adoption lente** | M | H | • Freemium généreux<br>• Import Excel/CSV<br>• Intégrations (Zotero) | Pivot B2B entreprise |
| **Performance scale** | L | H | • Load testing early<br>• Cache agressif<br>• CDN exports | Vertical scaling |
| **Concurrence BigTech** | L | H | • Open source<br>• Privacy-first<br>• Communauté | Niche verticale |

---

## 8. Go-to-Market

### 8.1 Stratégie de Lancement

| Phase | Target | Stratégie | Objectif |
|-------|--------|-----------|----------|
| **Mois 1-3** | 3 labs SHS | Free pilot, white glove | 10 champions |
| **Mois 4-6** | Juridique + Medical | Early bird -50% | 100 users |
| **Mois 7-12** | Entreprises | Freemium | 1000 users |

### 8.2 Modèle de Prix (v1.0+)

| Tier | Prix/mois | Limites | Target |
|------|-----------|---------|--------|
| **Free** | €0 | 100 termes, 1k API | Individuals |
| **Pro** | €49 | 1k termes, 50k API | Academic |
| **Team** | €199 | 10k termes, 500k API | SMB |
| **Enterprise** | Custom | Unlimited, SLA | Corps |

---

## 9. Success Metrics

### 9.1 KPIs par Phase

| Phase | Business | Technical | Quality |
|-------|----------|-----------|---------|
| **v0.1** | 10 early adopters | API < 200ms | 80% validated |
| **v0.2** | 100 MAU | Search < 500ms | NPS > 30 |
| **v1.0** | €10k MRR | 1000 req/s | -30% LLM errors |

### 9.2 North Star Metric
**Termes Validés par Semaine (TVS)**
- Month 1-3: 50 TVS
- Month 4-6: 100 TVS
- Month 7-12: 200 TVS

---

## 10. Actions Immédiates (Semaine 1)

| # | Action | Responsable | Deadline | Critère succès |
|---|--------|-------------|----------|----------------|
| 1 | **POC Neo4j vs PostgreSQL** | Tech Lead | Vendredi | Décision avec benchmarks |
| 2 | **Setup GitHub + CI/CD** | DevOps | Mercredi | Pipeline fonctionnel |
| 3 | **Recruter backend senior** | CEO | Vendredi | 3 candidats shortlist |
| 4 | **Contacter 3 labs SHS** | PO | Jeudi | Meetings schedulés |
| 5 | **Docker Compose env** | Backend | Vendredi | Dev env opérationnel |

---

## Annexes

### A. Décisions en Suspens

- [ ] Neo4j Community vs Enterprise (licensing)
- [ ] Embedding model : local vs API
- [ ] Deployment : AWS vs GCP vs on-premise
- [ ] RGPD compliance strategy

### B. Dépendances Critiques

- PostgreSQL 15 + extensions
- Neo4j 5.15 (si choisi)
- Python 3.11+
- Node.js 20+

### C. Liens Documentation

- [Architecture détaillée](./analyse-critique-opus-v03-p2.md)
- [PRD complet v0.3](./PRD-ontologie-v03.md)
- [Modèle de données](./fiche-terme-v03.json)
- [Roadmap technique 8 sprints](./roadmap-technique-v03.md)

---

**Statut** : Plan exécutable avec budget, ressources et risques identifiés
**Prochaine révision** : Post-POC Sprint 1 (dans 2 semaines)
**Contact** : Claude Opus, Product Strategy Advisor

*Ce document synthétise 500+ pages d'analyse en format exécutif actionnable*