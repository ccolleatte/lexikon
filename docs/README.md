# Documentation - Lexikon

Index de toute la documentation du projet Lexikon.

---

## 📚 Documentation par Catégorie

### Tests Automatisés

| Document | Description | Status |
|----------|-------------|--------|
| **[TESTING-STATUS.md](./TESTING-STATUS.md)** | ⭐ Status actuel des tests | ✅ À jour |
| **[TESTING-FRONTEND-AUTH.md](./TESTING-FRONTEND-AUTH.md)** | Tests unitaires (Auth Store, Auth Utils, API) | ✅ 96 tests |
| **[TESTING-COMPONENTS-E2E.md](./TESTING-COMPONENTS-E2E.md)** | Guide complet composants + E2E | ✅ 111 tests |
| **[../e2e/README.md](../e2e/README.md)** | Guide rapide Playwright E2E | ✅ Configuré |

### Tests Manuels

| Document | Description | Status |
|----------|-------------|--------|
| **[TESTING-STRATEGY-AUTH.md](./TESTING-STRATEGY-AUTH.md)** | Stratégie de test auth (29 cas) | ✅ Complet |
| **[../FRONTEND-AUTH-TESTING.md](../FRONTEND-AUTH-TESTING.md)** | Guide manuel de test frontend | ✅ Complet |
| **[../TESTING.md](../TESTING.md)** | Guide de test Sprint 1 | ✅ Sprint 1 |

### Sprint Planning & Progress

| Document | Description | Status |
|----------|-------------|--------|
| **[sprint-2-plan.md](./sprint-2-plan.md)** | Plan Sprint 2 complet | ✅ Planifié |
| **[SPRINT-2-PROGRESS.md](./SPRINT-2-PROGRESS.md)** | Progression Sprint 2 | 🔄 En cours |

### Design & UX

| Document | Description | Status |
|----------|-------------|--------|
| **[design/](./design/)** | Design tokens, couleurs, typographie | ✅ Défini |
| **Wireframes** | (À documenter) | ⏳ À faire |
| **User Stories** | (À documenter) | ⏳ À faire |

---

## 🎯 Documents par Rôle

### Pour les Développeurs

**Premiers pas:**
1. [../README.md](../README.md) - README principal
2. [../QUICKSTART.md](../QUICKSTART.md) - Démarrage rapide
3. [sprint-2-plan.md](./sprint-2-plan.md) - Comprendre Sprint 2

**Développement:**
- [TESTING-STATUS.md](./TESTING-STATUS.md) - Status tests actuels
- [TESTING-FRONTEND-AUTH.md](./TESTING-FRONTEND-AUTH.md) - Lancer tests unitaires
- [../e2e/README.md](../e2e/README.md) - Lancer tests E2E

### Pour les Testeurs/QA

**Tests Automatisés:**
1. [TESTING-STATUS.md](./TESTING-STATUS.md) - Vue d'ensemble
2. [TESTING-COMPONENTS-E2E.md](./TESTING-COMPONENTS-E2E.md) - Guide complet
3. [../e2e/README.md](../e2e/README.md) - Commandes E2E

**Tests Manuels:**
1. [TESTING-STRATEGY-AUTH.md](./TESTING-STRATEGY-AUTH.md) - Stratégie de test
2. [../FRONTEND-AUTH-TESTING.md](../FRONTEND-AUTH-TESTING.md) - Scénarios de test
3. [../TESTING.md](../TESTING.md) - Guide de test manuel

### Pour les Product Owners

**Planning & Progress:**
- [sprint-2-plan.md](./sprint-2-plan.md) - Plan détaillé Sprint 2
- [SPRINT-2-PROGRESS.md](./SPRINT-2-PROGRESS.md) - Progrès actuel
- [TESTING-STATUS.md](./TESTING-STATUS.md) - Status des tests

**Spécifications:**
- (À venir) User Stories
- (À venir) API Specifications
- (À venir) Wireframes

---

## 📊 Status Actuel du Projet

### Sprint 2 - Authentication & Database

**Complété:**
- ✅ Backend: PostgreSQL + Neo4j configurés
- ✅ Backend: JWT authentication
- ✅ Backend: OAuth2 (Google, GitHub)
- ✅ Frontend: Pages Login/Register/Profile
- ✅ Frontend: NavBar avec user menu
- ✅ Frontend: Auth store + utilities
- ✅ Tests: 96 tests unitaires (85% coverage)
- ✅ Tests: 74 tests composants créés
- ✅ Tests: 37 tests E2E créés
- ✅ Tests: Playwright configuré

**En cours:**
- 🔄 Tests E2E: Activation avec backend
- 🔄 Tests composants: Fix compilation Svelte

**À venir:**
- ⏳ Onboarding flow
- ⏳ Term management
- ⏳ CI/CD pipeline

---

## 🔍 Comment Trouver une Information

### "Je veux lancer les tests"

**Tests unitaires:**
```bash
npm test                    # Voir TESTING-FRONTEND-AUTH.md
npm run test:coverage       # Rapport de couverture
```

**Tests E2E:**
```bash
npm run test:e2e            # Voir e2e/README.md
npm run test:e2e:ui         # Mode interactif
```

**Status des tests:**
- Lire [TESTING-STATUS.md](./TESTING-STATUS.md)

### "Je veux comprendre l'architecture"

1. [../README.md](../README.md) - Vue d'ensemble
2. [sprint-2-plan.md](./sprint-2-plan.md) - Architecture Sprint 2
3. [SPRINT-2-PROGRESS.md](./SPRINT-2-PROGRESS.md) - Ce qui est fait

### "Je veux ajouter un test"

**Test unitaire:**
- Lire [TESTING-FRONTEND-AUTH.md](./TESTING-FRONTEND-AUTH.md)
- Exemples dans `src/lib/**/*.test.ts`

**Test composant:**
- Lire [TESTING-COMPONENTS-E2E.md](./TESTING-COMPONENTS-E2E.md)
- Exemples dans `src/routes/**/page.test.ts`
- Exemples dans `src/lib/components/**/*.test.ts`

**Test E2E:**
- Lire [../e2e/README.md](../e2e/README.md)
- Exemples dans `e2e/*.spec.ts`

### "Je veux tester manuellement une feature"

**Authentication:**
- Suivre [TESTING-STRATEGY-AUTH.md](./TESTING-STRATEGY-AUTH.md)
- Ou [../FRONTEND-AUTH-TESTING.md](../FRONTEND-AUTH-TESTING.md)

**Application complète:**
- Suivre [../TESTING.md](../TESTING.md) (Sprint 1)

---

## 📝 Conventions de Documentation

### Nommage des Fichiers
- `UPPERCASE.md` - Guides racine du projet
- `lowercase.md` - Documentation technique
- `CamelCase.md` - Plans et rapports de sprint

### Localisation
- `/docs/` - Documentation technique détaillée
- `/e2e/` - Documentation tests E2E
- Racine `/` - Guides principaux (README, QUICKSTART, TESTING)

### Mise à Jour
- Tous les docs incluent une date de dernière mise à jour
- [TESTING-STATUS.md](./TESTING-STATUS.md) est le document de référence pour le status

---

## 🆘 Support

**Problèmes de tests:**
1. Consulter [TESTING-STATUS.md](./TESTING-STATUS.md) - Section "Limitations Actuelles"
2. Consulter [TESTING-COMPONENTS-E2E.md](./TESTING-COMPONENTS-E2E.md) - Section "Troubleshooting"

**Questions générales:**
- Consulter [../README.md](../README.md)
- Consulter [../QUICKSTART.md](../QUICKSTART.md)

---

**Maintenu par:** Lexikon Development Team
**Dernière mise à jour:** 2025-11-15
