#!/bin/bash
# Script de maintenance automatique du serveur
# Créé automatiquement par Claude Code
# Exécution recommandée: hebdomadaire (dimanche 3h00)

LOG_FILE="/var/log/server-cleanup.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo "=== Début de la maintenance: $DATE ===" >> $LOG_FILE

# 1. Nettoyage Docker
echo "[$DATE] Nettoyage des images Docker inutilisées..." >> $LOG_FILE
docker image prune -af >> $LOG_FILE 2>&1

echo "[$DATE] Nettoyage du build cache Docker..." >> $LOG_FILE
docker builder prune -af >> $LOG_FILE 2>&1

echo "[$DATE] Nettoyage des volumes Docker orphelins..." >> $LOG_FILE
docker volume prune -f >> $LOG_FILE 2>&1

echo "[$DATE] Nettoyage général Docker (conteneurs arrêtés, réseaux, etc.)..." >> $LOG_FILE
docker system prune -f >> $LOG_FILE 2>&1

# 2. Nettoyage des logs système
echo "[$DATE] Limitation des logs journald à 500MB..." >> $LOG_FILE
journalctl --vacuum-size=500M >> $LOG_FILE 2>&1

# 3. Nettoyage des caches
echo "[$DATE] Nettoyage du cache npm..." >> $LOG_FILE
npm cache clean --force >> $LOG_FILE 2>&1

echo "[$DATE] Nettoyage du cache pip..." >> $LOG_FILE
pip cache purge >> $LOG_FILE 2>&1

# 4. Mise à jour et nettoyage du système
echo "[$DATE] Nettoyage des packages obsolètes..." >> $LOG_FILE
apt autoremove -y >> $LOG_FILE 2>&1
apt autoclean >> $LOG_FILE 2>&1

# 5. Statistiques finales
echo "[$DATE] Espace disque après nettoyage:" >> $LOG_FILE
df -h / >> $LOG_FILE 2>&1

echo "[$DATE] Utilisation Docker après nettoyage:" >> $LOG_FILE
docker system df >> $LOG_FILE 2>&1

echo "=== Fin de la maintenance: $(date +"%Y-%m-%d %H:%M:%S") ===" >> $LOG_FILE
echo "" >> $LOG_FILE
