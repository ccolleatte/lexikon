# 📋 Lexikon - Backlog de Corrections

## ✅ Complétées
- [x] **Correction #1 - French Typography** (2025-11-30)
  - Capitalisation française appliquée à toute l'interface
  - Commit: 47d25c4

---

## 🔄 En Attente (Par Ordre de Priorité)

### Correction #2 - Mot de Passe Oublié (High Priority)
**Status:** Pending
**URL:** https://lexikon.chessplorer.com/forgot-password

**Contexte:**
Implémenter la fonctionnalité complète "mot de passe oublié" (frontend + backend)

**Flux utilisateur:**
1. Utilisateur clique sur "Mot de passe oublié?" depuis la page login
2. Accès à `/forgot-password`
3. Utilisateur entre son adresse e-mail
4. Backend vérifie l'existence de l'e-mail en base de données
5. Si trouvé → Envoyer un e-mail avec lien de réinitialisation
6. Utilisateur clique le lien → Page de réinitialisation du mot de passe
7. Nouvel mot de passe saisi → Mise à jour en base

**Travail à faire:**
- [ ] **Frontend:**
  - [ ] Créer la page `/forgot-password` (form e-mail)
  - [ ] Créer la page `/reset-password/[token]` (form nouveau mot de passe)
  - [ ] Ajouter le lien "Mot de passe oublié?" sur la page login
  - [ ] Messages d'erreur/succès appropriés

- [ ] **Backend:**
  - [ ] Endpoint POST `/auth/forgot-password` (accepte email)
  - [ ] Endpoint POST `/auth/reset-password` (accepte token + nouveau password)
  - [ ] Générer token sécurisé pour réinitialisation (ex: JWT avec expiration)
  - [ ] Service d'envoi d'e-mail (configuration SMTP)
  - [ ] Template d'e-mail pour le lien de réinitialisation
  - [ ] Validation du token à la réinitialisation

**Points clés:**
- Token d'expiration limité (ex: 1h)
- Sécuriser l'endpoint (rate limiting)
- Vérifier que l'utilisateur n'abuse pas du service
- Test: vérifier que les e-mails sont bien envoyés

---

### Correction #3 - Google OAuth Integration (High Priority - Backlog)
**Status:** Backlog (Tokens limités - reporter pour prochaine session)

**Contexte:**
Implémenter l'authentification Google fonctionnelle (actuellement placeholder)

**Travail à faire:**
- [ ] Créer les credentials Google OAuth (Google Cloud Console)
- [ ] Configurer les URI de redirection
- [ ] Implémenter le flux OAuth côté frontend
- [ ] Créer/mettre à jour utilisateur en base au login Google
- [ ] Gérer les erreurs et edge cases

---

### Correction #4 - Google OAuth Flow (High Priority - Next Session)
**Status:** Backlog (À faire après Correction #2 et #3)
**URL:** Login/Register buttons "Continuer avec Google"

**Contexte:**
Implémenter la fonctionnalité complète "Continuer avec Google" (frontend + backend OAuth flow)

**Flux utilisateur:**
1. Utilisateur clique sur "Continuer avec Google" sur login ou register
2. Redirection vers Google OAuth consent screen
3. Utilisateur autorise l'app
4. Google retourne un authorization code
5. Backend traite le code → crée/met à jour l'utilisateur
6. Frontend reçoit JWT + infos utilisateur
7. Redirection vers `/terms` ou onboarding si premier login

**Travail à faire:**
- [ ] **Frontend:**
  - [ ] Implémenter le bouton "Continuer avec Google" (utiliser @react-oauth/google ou équivalent Svelte)
  - [ ] Gérer le callback du popup/redirect Google
  - [ ] Passer le token Google au backend
  - [ ] Gérer les erreurs d'authentification
  - [ ] Redirection post-auth

- [ ] **Backend:**
  - [ ] Endpoint POST `/auth/google/callback` (accepte Google token)
  - [ ] Vérifier le token Google (validation avec Google API)
  - [ ] Créer/mettre à jour utilisateur en base (lookup par email Google)
  - [ ] Générer JWT pour la session
  - [ ] Gérer le cas première connexion (onboarding?)
  - [ ] Gérer les erreurs (token invalide, email non trouvé, etc.)

- [ ] **Configuration:**
  - [ ] Ajouter Google Client ID à `.env.prod`
  - [ ] Tester en local et en production

**Points clés:**
- Sécuriser la validation du token Google (ne pas faire confiance au client)
- Rate limiting sur l'endpoint OAuth
- Gérer les redirects correctement (popup vs redirect)
- Test avec différents navigateurs

---

## 📝 Notes Session Actuelle

**Date:** 2025-11-30
**Commits:**
- 47d25c4: fix(i18n) - French typography corrections
- 25a5e80: docs(oauth) - GitHub OAuth config template
- 0c2f222: fix(deployment) - Uptime Kuma port configuration
- ab9c0a2: docs(reconciliation) - Security feature parity

**Services Status:** ✅ All healthy
- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:3000
- Postgres: 127.0.0.1:5434
- Redis: 127.0.0.1:6379
- Nginx: 0.0.0.0:8080/8443

---

## 🚀 Prochaine Session

**Format recommandé:**
1. Commencer par Correction #2 (Mot de passe oublié) - C'est une feature complète mais faisable en une session
2. Valider au fil de l'eau (1 à 1)
3. Déployer et tester en live
4. Puis passer à Correction #3 (Google OAuth) si tokens restants

**Estimation tokens:**
- Mot de passe oublié: ~40-50K tokens (front + back)
- Google OAuth: ~30-40K tokens

