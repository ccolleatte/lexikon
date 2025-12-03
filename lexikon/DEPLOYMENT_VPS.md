# Lexikon Deployment on VPS - Complete Guide

## Overview

This guide walks through deploying Lexikon on a VPS with PostgreSQL, Redis, and the complete application stack using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned
- Domain name (for frontend URL configuration)
- OpenSSL (to generate secrets)

## Step 1: Clone Repository

```bash
cd /opt  # or your preferred directory
git clone https://github.com/ccolleatte/lexikon.git
cd lexikon
```

## Step 2: Generate Secrets

Generate all required secrets securely:

```bash
# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)
echo "JWT_SECRET=$JWT_SECRET"

# Generate API Key secret
API_KEY_SECRET=$(openssl rand -hex 32)
echo "API_KEY_SECRET=$API_KEY_SECRET"

# Generate PostgreSQL password
POSTGRES_PASSWORD=$(openssl rand -hex 32)
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"

# Generate Redis password
REDIS_PASSWORD=$(openssl rand -hex 32)
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
```

## Step 3: Create .env.prod File

```bash
cp .env.prod.example .env.prod
nano .env.prod  # Edit with your values
```

**Required values to set:**

```bash
# Database
POSTGRES_DB=lexikon
POSTGRES_USER=lexikon
POSTGRES_PASSWORD=[generated-password]
DATABASE_URL=postgresql://lexikon:[generated-password]@postgres:5432/lexikon

# Redis
REDIS_PASSWORD=[generated-password]

# JWT & API Security
JWT_SECRET=[generated-secret]
API_KEY_SECRET=[generated-secret]

# Application
ENVIRONMENT=production
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# Optional: OAuth (leave empty if not using)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

**IMPORTANT: Never commit .env.prod to git!**

```bash
# Verify .env.prod is in .gitignore
grep "\.env\.prod" .gitignore
```

## Step 4: Prepare Environment Files

Copy root .env for Docker Compose:

```bash
cat > .env << EOF
POSTGRES_PASSWORD=[same-as-.env.prod]
REDIS_PASSWORD=[same-as-.env.prod]
EOF
```

## Step 5: Build Docker Images

```bash
# Build backend and frontend images
docker-compose -f docker-compose.prod.yml build

# This builds:
# - lexikon:backend (FastAPI + Uvicorn)
# - lexikon:frontend (SvelteKit)
```

## Step 6: Run Database Migrations

```bash
# Run Alembic migrations to initialize schema
docker-compose -f docker-compose.migrate.yml --env-file .env.prod up --abort-on-container-exit

# Expected output:
# Alembic - INFO  alembic.migration - Running upgrade  -> 7beb871f4454...
# Alembic - INFO  alembic.migration - Running upgrade 7beb871f4454 -> b9d0965451a3...
# (continues for all migrations)
```

**What this does:**
1. Starts PostgreSQL
2. Runs Alembic migrations (creates users, terms, oauth_accounts, etc. tables)
3. Exits

## Step 7: Start All Services

```bash
# Start the complete stack
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Verify all services started:
docker-compose -f docker-compose.prod.yml ps

# Expected output:
# NAME                STATUS
# lexikon-postgres    healthy
# lexikon-redis       healthy
# lexikon-backend     healthy
# lexikon-frontend    healthy
# lexikon-uptime-kuma running
```

## Step 8: Verify Services

### Check Logs

```bash
# Backend logs
docker-compose -f docker-compose.prod.yml logs -f lexikon-backend

# Frontend logs
docker-compose -f docker-compose.prod.yml logs -f lexikon-frontend

# Database logs
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Test API Health

```bash
# From inside VPS (port 8000 is only localhost)
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy"}
```

### Test Frontend

```bash
# Check frontend is running
curl -I http://localhost:3000

# Expected response:
# HTTP/1.1 200 OK
```

## Step 9: Configure Nginx (Reverse Proxy)

Create nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/lexikon
```

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # API endpoints → Backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }

    # OAuth callbacks → Backend
    location /oauth/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check → Backend
    location /health {
        proxy_pass http://backend;
    }

    # Everything else → Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable nginx site:

```bash
sudo ln -s /etc/nginx/sites-available/lexikon /etc/nginx/sites-enabled/
sudo nginx -t  # Test config
sudo systemctl restart nginx
```

## Step 10: Setup SSL/TLS

Using Let's Encrypt (free):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
# Follow prompts to verify domain ownership
```

## Step 11: Monitor Services

```bash
# Watch real-time logs
docker-compose -f docker-compose.prod.yml logs -f

# Check container health
docker-compose -f docker-compose.prod.yml ps

# Check disk space
du -sh ./lexikon_postgres_data ./lexikon_redis_data

# Monitor memory/CPU
docker stats
```

## Step 12: Access Application

Navigate to: `https://your-domain.com`

Expected:
- Frontend loads successfully
- Can navigate to `/register` and `/login`
- Can create an account
- Can start onboarding flow

## Troubleshooting

### Services won't start

```bash
# Check logs for errors
docker-compose -f docker-compose.prod.yml logs

# Verify .env.prod has all required variables
cat .env.prod | grep -E "PASSWORD|SECRET|URL|ORIGINS"

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Database migration fails

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.migrate.yml logs postgres

# Manually check database
docker exec -it lexikon-postgres psql -U lexikon -d lexikon -c "\dt"

# Re-run migrations
docker-compose -f docker-compose.migrate.yml --env-file .env.prod up --abort-on-container-exit
```

### Backend returns 502 Bad Gateway

```bash
# Check backend health
curl http://localhost:8000/health

# Check backend logs
docker-compose -f docker-compose.prod.yml logs lexikon-backend

# Check if JWT_SECRET is set
docker-compose -f docker-compose.prod.yml exec lexikon-backend env | grep JWT
```

### Frontend can't connect to API

```bash
# Verify CORS configuration
curl -H "Origin: https://your-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     http://localhost:8000/api/auth/login -v

# Check frontend environment
docker-compose -f docker-compose.prod.yml exec lexikon-frontend env | grep BACKEND
```

## Maintenance

### Daily

```bash
# Monitor logs for errors
docker-compose -f docker-compose.prod.yml logs --tail=100

# Check disk usage
df -h | grep /
```

### Weekly

```bash
# Backup database
docker exec lexikon-postgres pg_dump -U lexikon lexikon > lexikon_$(date +%Y%m%d).sql

# Check system updates
sudo apt update && apt list --upgradable

# Review uptime-kuma dashboard
# Navigate to: https://your-domain.com:3005
```

### Monthly

```bash
# Update Docker images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Renew SSL certificate (if using certbot)
sudo certbot renew --dry-run
```

## Rollback Procedure

If something breaks:

```bash
# Stop all services (keep data)
docker-compose -f docker-compose.prod.yml down

# Go back to previous git commit
git checkout [previous-commit-hash]

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations (idempotent - safe to run again)
docker-compose -f docker-compose.migrate.yml --env-file .env.prod up --abort-on-container-exit
```

## User Testing Workflow

Once deployed:

### 1. Test Registration

```bash
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "language": "en"
  }'
```

### 2. Test Onboarding Flow

1. Navigate to `/register`
2. Fill form and submit
3. Should redirect to `/onboarding` (adoption level selection)
4. Select "Quick Project"
5. Should redirect to `/onboarding/profile`
6. Fill profile and submit
7. Should redirect to `/terms`

### 3. Test Term Creation

1. Click "Create Term"
2. Fill: Name, Definition, Domain (optional)
3. Click "Create"
4. Should appear in `/terms` list

## Production Checklist

- [ ] Secrets generated and stored securely
- [ ] .env.prod created (never committed)
- [ ] All Docker images built
- [ ] Database migrations ran successfully
- [ ] All services healthy (docker ps)
- [ ] nginx configured and restarted
- [ ] SSL/TLS certificate installed
- [ ] Frontend loads at https://your-domain.com
- [ ] API responds at https://your-domain.com/api/health
- [ ] Registration/Login flow tested
- [ ] Onboarding flow tested
- [ ] Term creation tested
- [ ] Logs monitored for errors
- [ ] Database backup plan in place
- [ ] Monitoring alerts configured (uptime-kuma)

## Next Steps

- Configure OAuth (Google, GitHub) if desired
- Set up automated backups
- Configure email service for verification emails
- Monitor performance metrics
- Review security logs regularly
