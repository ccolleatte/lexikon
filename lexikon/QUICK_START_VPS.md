# Lexikon VPS Deployment - Quick Start (TL;DR)

For the impatient. Full guide: See `DEPLOYMENT_VPS.md`

## 1. SSH to VPS

```bash
ssh user@your-vps-ip
cd /opt && git clone https://github.com/ccolleatte/lexikon.git && cd lexikon
```

## 2. Generate Secrets (5 min)

```bash
JWT_SECRET=$(openssl rand -hex 32)
API_KEY_SECRET=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 32)
REDIS_PASSWORD=$(openssl rand -hex 32)

echo "Save these:"
echo "JWT_SECRET=$JWT_SECRET"
echo "API_KEY_SECRET=$API_KEY_SECRET"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
```

## 3. Create .env.prod

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Paste your secrets into the file. Key variables:

```
POSTGRES_PASSWORD=[paste here]
REDIS_PASSWORD=[paste here]
JWT_SECRET=[paste here]
API_KEY_SECRET=[paste here]
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com
```

## 4. Create Root .env

```bash
cat > .env << EOF
POSTGRES_PASSWORD=[your-postgres-password]
REDIS_PASSWORD=[your-redis-password]
EOF
```

## 5. Deploy (3 min)

```bash
chmod +x deploy-vps.sh
./deploy-vps.sh production
```

That's it! The script:
- ✓ Builds Docker images
- ✓ Backs up database
- ✓ Runs migrations
- ✓ Starts all services
- ✓ Verifies health

## 6. Configure Nginx

```bash
# Copy nginx config (see DEPLOYMENT_VPS.md for full config)
sudo nano /etc/nginx/sites-available/lexikon

# Enable it
sudo ln -s /etc/nginx/sites-available/lexikon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Setup SSL

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

## 8. Access Your App

Navigate to: `https://your-domain.com`

## Troubleshooting

### Services not healthy

```bash
docker-compose -f docker-compose.prod.yml logs
docker-compose -f docker-compose.prod.yml restart
```

### Migrations failed

```bash
docker-compose -f docker-compose.migrate.yml --env-file .env.prod logs
docker exec -it lexikon-postgres psql -U lexikon -d lexikon -c "\dt"
```

### Nginx 502 errors

```bash
curl http://localhost:8000/health
docker-compose -f docker-compose.prod.yml logs lexikon-backend
```

## Next Steps

- [ ] Test user registration at https://your-domain.com/register
- [ ] Test onboarding flow
- [ ] Test term creation
- [ ] See TEST_USER_JOURNEYS.md for complete testing

## Restart Everything

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## View Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f lexikon-backend
docker-compose -f docker-compose.prod.yml logs -f lexikon-frontend
docker-compose -f docker-compose.prod.yml logs -f postgres
```

## Daily Checks

```bash
# Check all services are healthy
docker-compose -f docker-compose.prod.yml ps

# Check for errors
docker-compose -f docker-compose.prod.yml logs | grep ERROR

# Check disk space
df -h /
```

## Rollback (if needed)

```bash
git checkout [previous-commit]
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
docker-compose -f docker-compose.migrate.yml --env-file .env.prod up --abort-on-container-exit
```

---

**Need more details?** See:
- `DEPLOYMENT_VPS.md` - Full step-by-step guide
- `TEST_USER_JOURNEYS.md` - Complete testing plan
- `DEPLOYMENT.md` - Architecture overview
