#!/bin/bash
##############################################################################
# Lexikon VPS Setup - Run this directly on your VPS
#
# Usage on VPS:
#   cd /opt/lexikon
#   # Paste the commands below into your terminal
#
# These commands will:
# 1. Download the post-deploy-check.sh script
# 2. Make it executable
# 3. Copy it to /opt/lexikon/
# 4. Add it to crontab for automation (optional)
##############################################################################

set -e

REPO_DIR="/opt/lexikon"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 LEXIKON VPS CHECKLIST SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Option 1: Copy script from git repository
if [ -d "$REPO_DIR/.git" ]; then
    echo "✅ Git repository found at $REPO_DIR"
    echo "Updating repository to get latest scripts..."
    cd "$REPO_DIR"
    git fetch origin
    git pull origin develop

    if [ -f "post-deploy-check.sh" ]; then
        chmod +x post-deploy-check.sh
        echo "✅ post-deploy-check.sh is ready"
    else
        echo "❌ post-deploy-check.sh not found in repository"
        exit 1
    fi
else
    echo "❌ Git repository not found at $REPO_DIR"
    echo "Please ensure lexikon is cloned to /opt/lexikon"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Next steps:"
echo ""
echo "1️⃣  After running ./deploy.sh, verify deployment:"
echo "    cd /opt/lexikon"
echo "    ./post-deploy-check.sh"
echo ""
echo "2️⃣  Expected output: All checks should be GREEN ✅"
echo ""
echo "3️⃣  If any RED ❌, rollback immediately:"
echo "    ./rollback.sh"
echo ""
