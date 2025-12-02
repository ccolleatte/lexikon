#!/bin/bash

# Script de validation - Sprint 1
# Vérifie que tous les fichiers essentiels sont présents et corrects

echo "🔍 Validation Sprint 1 - Lexikon"
echo "=================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUCCESS=0
FAILURES=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $1 - MANQUANT"
        ((FAILURES++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $1/ - MANQUANT"
        ((FAILURES++))
    fi
}

echo "📦 Configuration Files"
echo "----------------------"
check_file "package.json"
check_file "vite.config.js"
check_file "svelte.config.js"
check_file "tailwind.config.js"
check_file "tsconfig.json"
check_file "postcss.config.js"
echo ""

echo "🎨 Frontend Structure"
echo "---------------------"
check_file "src/app.html"
check_file "src/app.css"
check_dir "src/routes"
check_dir "src/lib/components"
check_dir "src/lib/stores"
check_dir "src/lib/utils"
check_dir "src/lib/types"
echo ""

echo "🧩 Components (7 required)"
echo "--------------------------"
check_file "src/lib/components/Button.svelte"
check_file "src/lib/components/Input.svelte"
check_file "src/lib/components/Textarea.svelte"
check_file "src/lib/components/Select.svelte"
check_file "src/lib/components/Progress.svelte"
check_file "src/lib/components/Alert.svelte"
check_file "src/lib/components/Stepper.svelte"
echo ""

echo "📄 Pages (5 required)"
echo "---------------------"
check_file "src/routes/+page.svelte"
check_file "src/routes/+layout.svelte"
check_file "src/routes/onboarding/+page.svelte"
check_file "src/routes/onboarding/profile/+page.svelte"
check_file "src/routes/terms/+page.svelte"
check_file "src/routes/terms/new/+page.svelte"
echo ""

echo "⚙️ Backend Files"
echo "----------------"
check_file "backend/main.py"
check_file "backend/models.py"
check_file "backend/database.py"
check_file "backend/requirements.txt"
check_file "backend/api/onboarding.py"
check_file "backend/api/users.py"
check_file "backend/api/terms.py"
echo ""

echo "📖 Documentation"
echo "----------------"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "TESTING.md"
check_file "backend/README.md"
echo ""

echo "🎯 User Stories"
echo "---------------"
check_file "user-stories/US-001-onboarding-adoption-level.md"
check_file "user-stories/US-002-quick-draft-creation.md"
check_file "user-stories/US-003-onboarding-profile-setup.md"
echo ""

echo "🎨 Wireframes"
echo "-------------"
check_file "wireframes/01-onboarding-adoption-level.html"
check_file "wireframes/02-creation-quick-draft.html"
check_file "wireframes/03-onboarding-profile-setup.html"
echo ""

echo "🎨 Design System"
echo "----------------"
check_file "docs/design/design-tokens.css"
check_file "docs/design/design-tokens.json"
check_file "docs/design/tailwind.config.js"
check_file "docs/design/icons-library.md"
check_file "docs/design/developer-handoff-guide.md"
check_file "docs/backend/api-specifications-sprint1.md"
echo ""

# Summary
echo "=================================="
echo "📊 Résumé"
echo "=================================="
echo -e "${GREEN}Succès: $SUCCESS${NC}"
echo -e "${RED}Échecs: $FAILURES${NC}"
echo ""

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les fichiers Sprint 1 sont présents !${NC}"
    echo ""
    echo "Prochaines étapes :"
    echo "1. Installer les dépendances (voir TESTING.md)"
    echo "2. Lancer les tests (voir TESTING.md)"
    echo "3. Merger vers master"
    exit 0
else
    echo -e "${RED}❌ Certains fichiers sont manquants${NC}"
    echo "Vérifiez l'implémentation Sprint 1"
    exit 1
fi
