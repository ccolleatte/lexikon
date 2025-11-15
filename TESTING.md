# 🧪 Guide de Test - Sprint 1

**Date**: 2025-11-15
**Durée estimée**: 20-30 minutes
**Objectif**: Valider que l'application Sprint 1 fonctionne de bout en bout

---

## ✅ Pré-requis

Avant de commencer, vérifiez que vous avez :

- [ ] **Python 3.10+** installé (`python3 --version`)
- [ ] **Node.js 18+** installé (`node --version`)
- [ ] **npm** installé (`npm --version`)
- [ ] Deux terminaux disponibles

---

## 📦 Phase 1 : Installation des Dépendances (5 min)

### Terminal 1 - Backend

```bash
cd /home/user/lexikon/backend

# Installer les dépendances Python
pip install -r requirements.txt

# Vérifier l'installation
python3 -c "from pydantic import BaseModel; print('✓ Pydantic OK')"
python3 -c "from fastapi import FastAPI; print('✓ FastAPI OK')"
```

**Résultat attendu** :
```
✓ Pydantic OK
✓ FastAPI OK
```

### Terminal 2 - Frontend

```bash
cd /home/user/lexikon

# Installer les dépendances Node
npm install

# Vérifier l'installation
npm list svelte tailwindcss lucide-svelte --depth=0
```

**Résultat attendu** :
```
lexikon@0.1.0
├── svelte@4.x.x
├── tailwindcss@3.x.x
└── lucide-svelte@0.x.x
```

---

## 🚀 Phase 2 : Démarrage des Serveurs (2 min)

### Terminal 1 - Backend

```bash
cd /home/user/lexikon/backend
python3 main.py
```

**Résultat attendu** :
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Vérifications** :
- [ ] Backend démarre sans erreur
- [ ] Port 8000 est utilisé
- [ ] Message "Application startup complete"

**Tester l'API** (dans un 3ème terminal) :
```bash
curl http://localhost:8000/health
# Doit retourner: {"status":"healthy"}

curl http://localhost:8000/
# Doit retourner: {"name":"Lexikon API","version":"0.1.0",...}
```

### Terminal 2 - Frontend

```bash
cd /home/user/lexikon
npm run dev
```

**Résultat attendu** :
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Vérifications** :
- [ ] Frontend démarre sans erreur
- [ ] Port 5173 est utilisé
- [ ] Aucune erreur de compilation TypeScript
- [ ] Aucune erreur Tailwind

---

## 🧪 Phase 3 : Tests Fonctionnels (15 min)

### Test 1 : Homepage (1 min)

1. **Ouvrir** http://localhost:5173/
2. **Vérifier** :
   - [ ] Logo "LEXIKON" visible en haut
   - [ ] Titre "LEXIKON" avec emoji 📚
   - [ ] Sous-titre "Service Générique d'Ontologies Lexicales"
   - [ ] 2 boutons : "Commencer →" et "Mes Ontologies"
   - [ ] 3 feature cards en bas (🚀 Création Rapide, 🤖 IA Agnostique, ✅ Human-in-the-Loop)
   - [ ] Design responsive (tester en redimensionnant la fenêtre)

**Screenshot** : Prendre une capture d'écran de la homepage

---

### Test 2 : US-001 - Sélection Niveau d'Adoption (3 min)

1. **Cliquer** sur "Commencer →"
2. **Vérifier** redirection vers `/onboarding`
3. **Vérifier** affichage :
   - [ ] Header avec logo LEXIKON
   - [ ] Titre "Bienvenue sur Lexikon"
   - [ ] 3 cartes : Projet Rapide, Projet de Recherche, Production/API
   - [ ] Chaque carte affiche : icon, titre, quote, features, badge prix
   - [ ] Bouton "Continuer →" désactivé par défaut

4. **Tester interaction** :
   - [ ] Survoler une carte → bordure change de couleur, ombre apparaît
   - [ ] Cliquer sur "Projet Rapide" → carte sélectionnée (bordure bleue, checkmark)
   - [ ] Bouton "Continuer →" devient actif
   - [ ] Changer de sélection → fonctionne

5. **Ouvrir DevTools** → Console
   - [ ] Aucune erreur JavaScript

6. **Ouvrir DevTools** → Application → Local Storage
   - [ ] Vérifier que `lexikon-onboarding` contient `{"adoptionLevel":"quick-project",...}`

7. **Cliquer** "Continuer →"
   - [ ] Redirection vers `/onboarding/profile`

**Screenshot** : Carte sélectionnée

---

### Test 3 : US-003 - Configuration Profil (4 min)

1. **Vérifier** affichage :
   - [ ] Stepper avec 3 étapes (Adoption ✓, Profil actif, Préférences gris)
   - [ ] Badge "Niveau sélectionné : Projet Rapide" 🚀
   - [ ] Formulaire avec champs : Prénom, Nom, Email (requis)
   - [ ] Champs optionnels : Institution, Domaine, Langue, Pays
   - [ ] Bouton "← Précédent" actif
   - [ ] Bouton "Continuer →" désactivé

2. **Tester validation** :
   - [ ] Taper "M" dans Prénom, Tab → erreur "Minimum 2 caractères"
   - [ ] Taper "Marie" → erreur disparaît
   - [ ] Taper "D" dans Nom, Tab → erreur apparaît
   - [ ] Taper "Dupont" → erreur disparaît
   - [ ] Taper "marie" dans Email, Tab → erreur "email valide"
   - [ ] Taper "marie@test.fr" → erreur disparaît
   - [ ] Bouton "Continuer →" devient actif

3. **Tester champs optionnels** :
   - [ ] Sélectionner "Philosophie" dans Domaine → fonctionne
   - [ ] Langue par défaut = "Français" → OK

4. **Tester navigation arrière** :
   - [ ] Cliquer "← Précédent" → retour à `/onboarding`
   - [ ] Vérifier que "Projet Rapide" reste sélectionné
   - [ ] Cliquer "Continuer" → retour à `/onboarding/profile`
   - [ ] Vérifier que les données du formulaire sont restaurées

5. **Vérifier DevTools → Network** :
   - [ ] Cliquer "Continuer →"
   - [ ] Vérifier requête `POST http://localhost:8000/api/users/profile`
   - [ ] Status: 200 OK
   - [ ] Response contient : `{"success":true,"data":{...}}`

6. **Vérifier redirection** :
   - [ ] Après "Continuer" → redirection vers `/terms`

**Screenshot** : Formulaire rempli

---

### Test 4 : Liste des Termes (1 min)

1. **Vérifier** affichage :
   - [ ] Header avec logo + nom utilisateur (Marie Dupont)
   - [ ] Bouton "+ Nouveau terme"
   - [ ] Empty state : "Aucun terme pour l'instant"
   - [ ] 3 statistiques : "5 min", "3 champs", "∞ termes"

2. **Cliquer** "+ Nouveau terme"
   - [ ] Redirection vers `/terms/new`

---

### Test 5 : US-002 - Création Quick Draft (6 min)

1. **Vérifier** affichage :
   - [ ] Header avec statut auto-save (gris "Auto-save")
   - [ ] Barre de progression "Création de terme" à 0%
   - [ ] Badge "⚡ Mode Rapide"
   - [ ] Banner bleu "Mode création rapide (5 minutes)"
   - [ ] Formulaire : Nom du terme, Définition, Domaine (optionnel)
   - [ ] Boutons : "Créer le terme →" (désactivé), "Enregistrer comme brouillon"

2. **Tester compteurs de caractères** :
   - [ ] Nom du terme : affiche "0/100"
   - [ ] Définition : affiche "0/500"
   - [ ] Taper dans les champs → compteurs s'actualisent

3. **Tester validation Nom** :
   - [ ] Taper "On", Tab → erreur "Minimum 3 caractères"
   - [ ] Taper "Ontologie" → erreur disparaît
   - [ ] Barre de progression passe à 40%

4. **Tester validation Définition** :
   - [ ] Taper "Étude", Tab → erreur "Minimum 50 caractères (actuellement 5)"
   - [ ] Taper une définition de 50+ caractères
   - [ ] Erreur disparaît
   - [ ] Barre de progression passe à 90%

5. **Tester auto-save** :
   - [ ] Attendre 1 seconde après avoir tapé
   - [ ] Statut passe à "Sauvegarde..." (gris)
   - [ ] Puis "Sauvegardé ✓" (vert)
   - [ ] Vérifier DevTools → Local Storage → `lexikon-draft` contient les données

6. **Tester restauration** :
   - [ ] Rafraîchir la page (F5)
   - [ ] Vérifier que les champs sont restaurés avec les valeurs

7. **Tester domaine optionnel** :
   - [ ] Remplir "Philosophie" → barre passe à 100%

8. **Tester soumission** :
   - [ ] Bouton "Créer le terme →" devient actif
   - [ ] Vérifier DevTools → Network
   - [ ] Cliquer "Créer le terme →"
   - [ ] Vérifier requête `POST http://localhost:8000/api/terms`
   - [ ] Status: 201 Created
   - [ ] Response : `{"success":true,"data":{"id":"...","name":"Ontologie",...}}`

9. **Vérifier navigation** :
   - [ ] Redirection vers `/terms?created=true`

**Screenshot** : Formulaire rempli avec progression 100%

---

### Test 6 : Vérification Backend (2 min)

**Ouvrir** http://localhost:8000/docs

1. **Vérifier** :
   - [ ] Swagger UI s'affiche
   - [ ] 4 endpoints visibles :
     - POST /api/onboarding/adoption-level
     - POST /api/users/profile
     - POST /api/terms
     - GET /api/terms

2. **Tester GET /api/terms** :
   - [ ] Cliquer "Try it out" → "Execute"
   - [ ] Response 200
   - [ ] Body contient le terme créé (Ontologie)

3. **Tester création doublon** :
   - [ ] POST /api/terms avec même nom "Ontologie"
   - [ ] Response 400 ou message erreur "terme existe déjà"

---

## 📊 Phase 4 : Checklist Finale (2 min)

### Fonctionnalités Core

- [ ] Onboarding : Sélection niveau d'adoption fonctionne
- [ ] Onboarding : Configuration profil fonctionne
- [ ] Terms : Création Quick Draft fonctionne
- [ ] Auto-save : Sauvegarde localStorage fonctionne
- [ ] Validation : Erreurs affichées correctement
- [ ] API : Backend répond à toutes les requêtes
- [ ] Navigation : Tous les liens fonctionnent
- [ ] Persistence : LocalStorage fonctionne

### Design & UX

- [ ] Design tokens appliqués (couleurs cohérentes)
- [ ] Responsive : Mobile, tablet, desktop
- [ ] Animations : Transitions fluides
- [ ] Focus states : Anneaux bleus visibles
- [ ] Loading states : Spinners affichés

### Performance

- [ ] Homepage charge en < 1s
- [ ] Navigation instantanée
- [ ] Aucun lag lors de la frappe
- [ ] Auto-save ne ralentit pas l'UI

### Accessibilité (Rapide)

- [ ] Navigation au clavier (Tab) fonctionne
- [ ] Focus visible sur tous les éléments
- [ ] Labels présents sur tous les inputs
- [ ] Boutons ont du texte (pas juste des icônes)

---

## 🐛 Bugs Connus / Limitations Sprint 1

**Intentionnels** (Sprint 2) :
- ⚠️ Données perdues au redémarrage backend (in-memory DB)
- ⚠️ Pas d'authentification réelle (tokens factices)
- ⚠️ Pas d'upload d'avatar
- ⚠️ Pas de suggestions IA

**À signaler si trouvés** :
- ❌ Erreurs console JavaScript
- ❌ Requêtes API qui échouent (500 errors)
- ❌ Validation qui ne fonctionne pas
- ❌ Navigation cassée
- ❌ Design incohérent

---

## ✅ Résultat Attendu

**Après ces tests, vous devriez avoir** :
- ✅ Application complète fonctionnelle
- ✅ Flow utilisateur de bout en bout opérationnel
- ✅ Backend API responsive
- ✅ Aucune erreur bloquante
- ✅ Confiance pour merger vers master

---

## 📸 Screenshots à Collecter

1. Homepage
2. Onboarding - Carte sélectionnée
3. Profile - Formulaire rempli
4. Quick Draft - Progression 100%
5. API Docs (Swagger UI)

---

## 🎯 Next Step

Si tous les tests passent :
→ **Passer à Option 2 : Merger vers master** ✅

Si des bugs trouvés :
→ Les documenter et les corriger avant merge

---

**Bonne chance pour les tests ! 🚀**
