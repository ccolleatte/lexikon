#!/bin/bash
set -e

# Lexikon VPS Deployment Script
# Automated deployment with safety checks

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on VPS (not local)
if [ "$1" == "--local" ]; then
  log_info "Running in LOCAL mode (for testing)"
  COMPOSE_FILE="docker-compose.prod.yml"
elif [ -z "$1" ]; then
  log_error "Usage: ./deploy-vps.sh <production|staging> [--skip-backup]"
  log_info "Example: ./deploy-vps.sh production"
  exit 1
else
  ENVIRONMENT=$1
  COMPOSE_FILE="docker-compose.prod.yml"
fi

log_info "Lexikon VPS Deployment Script"
log_info "Environment: ${ENVIRONMENT:-LOCAL}"
log_info "========================================="

# 1. Check prerequisites
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
  log_error "Docker is not installed"
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  log_error "Docker Compose is not installed"
  exit 1
fi

if [ ! -f ".env.prod" ]; then
  log_error ".env.prod file not found"
  log_info "Create .env.prod from .env.prod.example with your secrets"
  exit 1
fi

if [ ! -f ".env" ]; then
  log_warn ".env root file not found, creating from .env.prod"
  grep -E "POSTGRES_PASSWORD|REDIS_PASSWORD" .env.prod > .env
fi

log_info "✓ Prerequisites check passed"

# 2. Backup database (unless --skip-backup)
if [ "$2" != "--skip-backup" ] && [ -n "$ENVIRONMENT" ]; then
  log_info "Creating database backup..."

  BACKUP_DIR="./backups"
  mkdir -p "$BACKUP_DIR"

  BACKUP_FILE="$BACKUP_DIR/lexikon_$(date +%Y%m%d_%H%M%S).sql"

  # Check if postgres container is running
  if docker ps | grep -q lexikon-postgres; then
    docker exec lexikon-postgres pg_dump -U lexikon lexikon > "$BACKUP_FILE" || {
      log_error "Database backup failed"
      exit 1
    }
    log_info "✓ Backup created: $BACKUP_FILE"
  else
    log_warn "PostgreSQL not running, skipping backup"
  fi
fi

# 3. Git status check
log_info "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
  log_warn "Uncommitted changes detected:"
  git status --short
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# 4. Pull latest code
log_info "Pulling latest code..."
git fetch origin || log_warn "Git fetch failed, continuing"
CURRENT=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master)

if [ "$CURRENT" != "$REMOTE" ]; then
  log_warn "Local branch is behind origin/master"
  read -p "Update to latest? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git pull origin master || {
      log_error "Git pull failed"
      exit 1
    }
    log_info "✓ Updated to latest commit"
  fi
fi

# 5. Build images
log_info "Building Docker images..."
docker-compose -f "$COMPOSE_FILE" build || {
  log_error "Docker build failed"
  exit 1
}
log_info "✓ Docker images built successfully"

# 6. Stop old services (graceful)
log_info "Stopping old services..."
docker-compose -f "$COMPOSE_FILE" down || log_warn "Services not running"
log_info "✓ Services stopped"

# 7. Run migrations
log_info "Running database migrations..."
docker-compose -f docker-compose.migrate.yml --env-file .env.prod up --abort-on-container-exit || {
  log_error "Database migration failed"
  log_error "Rolling back..."
  docker-compose -f "$COMPOSE_FILE" down
  exit 1
}
log_info "✓ Database migrations completed"

# 8. Start new services
log_info "Starting all services..."
docker-compose -f "$COMPOSE_FILE" --env-file .env.prod up -d || {
  log_error "Services failed to start"
  exit 1
}
log_info "✓ Services started"

# 9. Wait for services to be healthy
log_info "Waiting for services to be healthy (max 60s)..."
MAX_ATTEMPTS=12
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  POSTGRES_HEALTH=$(docker inspect lexikon-postgres --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
  BACKEND_HEALTH=$(docker inspect lexikon-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
  FRONTEND_HEALTH=$(docker inspect lexikon-frontend --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")

  log_info "Status - PostgreSQL: $POSTGRES_HEALTH, Backend: $BACKEND_HEALTH, Frontend: $FRONTEND_HEALTH"

  if [ "$POSTGRES_HEALTH" == "healthy" ] && [ "$BACKEND_HEALTH" == "healthy" ] && [ "$FRONTEND_HEALTH" == "healthy" ]; then
    log_info "✓ All services healthy"
    break
  fi

  ATTEMPT=$((ATTEMPT + 1))
  sleep 5
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
  log_error "Services did not become healthy in time"
  log_info "Checking logs..."
  docker-compose -f "$COMPOSE_FILE" logs
  exit 1
fi

# 10. Health checks
log_info "Running health checks..."

# Test API
API_RESPONSE=$(curl -s http://localhost:8000/health || echo "FAILED")
if [[ $API_RESPONSE == *"healthy"* ]]; then
  log_info "✓ API is responding"
else
  log_error "API health check failed: $API_RESPONSE"
  exit 1
fi

# Test Frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" == "200" ]; then
  log_info "✓ Frontend is responding"
else
  log_error "Frontend returned status $FRONTEND_STATUS"
  exit 1
fi

# 11. Summary
log_info "========================================="
log_info "✓ Deployment successful!"
log_info "========================================="
log_info ""
log_info "Access your application:"
log_info "  Frontend: https://your-domain.com"
log_info "  API: https://your-domain.com/api/health"
log_info "  Uptime Kuma: https://your-domain.com:3005"
log_info ""
log_info "View logs:"
log_info "  docker-compose -f $COMPOSE_FILE logs -f"
log_info ""
log_info "If there are any issues, check:"
log_info "  1. .env.prod configuration"
log_info "  2. Docker logs: docker-compose logs"
log_info "  3. Recent backup: ls -lh backups/"
log_info ""
