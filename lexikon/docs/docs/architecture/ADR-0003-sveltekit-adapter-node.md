# ADR-0003: SvelteKit adapter-node for Production SSR Deployment

**Date:** 2025-11-27
**Status:** Accepted
**Deciders:** Lead Developer, DevOps
**Consulted:** Frontend Team
**Informed:** All Development Team

---

## Context

### Background
- **Project:** Lexikon Generic Ontology Service
- **Deployment Target:** Self-hosted Hostinger VPS (1 vCPU, 4GB RAM)
- **Infrastructure:** Docker Compose with PostgreSQL, Redis, FastAPI backend, Nginx reverse proxy
- **SvelteKit Version:** 2.x

### Problem Statement
Initial deployment attempt on November 23, 2025 failed to enable Server-Side Rendering (SSR) functionality.

**Initial Configuration:**
- Used `@sveltejs/adapter-auto` (default SvelteKit adapter)
- Result: Static HTML files generated only
- Output: `.svelte-kit/output/client/` (no `/server/` directory)

**Consequences of Static Rendering:**
- ❌ No server-side rendering (SSR)
- ❌ Dynamic routing broken (`/login`, `/signup`, `/app` routes not functional)
- ❌ Server hooks (`+page.server.ts`) not executed
- ❌ Authentication flow broken (no session management)
- ❌ API integration with backend failed
- ❌ Pages served as static `.html` files

**Impact:** Application was non-functional despite backend being production-ready.

### Decision Driver
The application requires full Server-Side Rendering capabilities to:
1. Handle user authentication and session management
2. Support dynamic routing for protected pages
3. Integrate with FastAPI backend for API calls
4. Implement progressive enhancement
5. Enable proper SEO through server-rendered content

---

## Decision

**Adopt `@sveltejs/adapter-node` for production SvelteKit deployment with full Server-Side Rendering capability on Docker Compose infrastructure.**

### Key Changes Implemented
- ✅ Switched from `@sveltejs/adapter-auto` to `@sveltejs/adapter-node@^5.4.0`
- ✅ Created `Dockerfile.frontend` with multi-stage Node.js build
- ✅ Added `frontend` service to `docker-compose.prod.yml` (port 3000)
- ✅ Configured Nginx reverse proxy to `frontend:3000`
- ✅ Created `build-server.mjs` custom HTTP server entry point
- ✅ Verified `.svelte-kit/output/server/` directory generated with proper SSR runtime

---

## Rationale

### Why adapter-node?

#### 1. **SSR Requirement**
The application architecture requires server-side rendering for:
- **Authentication:** Session state management via `+page.server.ts` hooks
- **Dynamic Routes:** Protected routes redirect to login, accessible routes render properly
- **API Integration:** Server-to-server communication with FastAPI backend (secure credentials)
- **Progressive Enhancement:** Content available even with slow JS delivery

#### 2. **Docker Compatibility**
`adapter-node` generates a Node.js HTTP server compatible with:
- **Containerization:** Runs as standalone Node.js process in Docker
- **Reverse Proxy:** Accepts HTTP on port 3000, Nginx proxies public traffic
- **Multi-Stage Builds:** Production image optimized (reduces footprint)
- **Signal Handling:** Properly handles SIGTERM for graceful shutdowns

#### 3. **Self-Hosted Infrastructure**
Unlike platform adapters (Vercel, Netlify), `adapter-node` provides:
- **Platform-Agnostic:** Works on any Node.js environment (not tied to specific provider)
- **No Vendor Lock-In:** Full control over deployment pipeline
- **Flexibility:** Can customize build process, environment variables, startup scripts
- **Cost Effective:** No platform fees, runs on existing VPS

#### 4. **Production Deployment Pattern**
Following industry standard:
```
Internet (HTTPS via Caddy)
    ↓
Nginx Reverse Proxy (Port 8080/8443)
    ├─→ /api/* → FastAPI Backend (Port 8000)
    ├─→ /monitoring/* → Uptime Kuma (Port 3001)
    └─→ /* → SvelteKit SSR Server (Port 3000)
```

This architecture is standard for production SvelteKit deployments on self-hosted infrastructure.

---

## Consequences

### Positive
✅ **Full SSR Functionality**
- Dynamic routes work properly
- Server hooks execute successfully
- Session management enabled
- Authentication flows functional end-to-end

✅ **Proper Container Isolation**
- Frontend service separate from backend
- Clear separation of concerns
- Independent scaling (if needed)

✅ **Web Standards Support**
- WebSocket support for HMR and potential real-time features
- Progressive enhancement possible
- Proper client-side navigation (SPA behavior with SSR benefits)

✅ **Production Ready**
- Health checks configured
- Graceful shutdown handling
- Error logging and monitoring
- Deployment pipeline well-defined

### Negative
❌ **Additional Container Management**
- One more service to monitor (lexikon-frontend)
- Increased docker-compose complexity slightly
- Health checks must be maintained

❌ **Resource Overhead**
- Node.js runtime adds ~50MB memory footprint
- Slightly more CPU usage than static files served directly
- VPS: 4GB RAM, so ~1.25% overhead (acceptable)

❌ **Deployment Complexity**
- Multi-stage Docker build adds ~2 min to build time
- Frontend build artifacts must be properly handled
- Requires understanding of Node.js server lifecycle

### Mitigations

**Mitigation for Resource Overhead:**
- Multi-stage Docker build minimizes image size
- Base image: `node:18-alpine` (lightweight)
- Only runtime dependencies included in final stage

**Mitigation for Complexity:**
- `Dockerfile.frontend` well-documented
- `build-server.mjs` handles edge cases
- Health checks ensure monitoring
- Deployment script handles all orchestration

**Mitigation for Monitoring:**
- Integrated into `docker-compose.prod.yml`
- Health checks configured (healthcheck section)
- Nginx logs show any routing issues
- Application logs captured in Docker logs

---

## Alternatives Considered

### 1. adapter-auto (Static Mode) - REJECTED ❌
**What it does:** Auto-detects environment, generates static HTML in development

**Why attempted initially:**
- Default SvelteKit adapter
- Zero configuration required
- Simpler deployment model

**Why rejected:**
- ❌ In Docker environment, detects "static" mode and generates HTML only
- ❌ No `/server/` directory created
- ❌ No SSR capabilities
- ❌ Failed to meet authentication requirements
- ❌ **Evidence:** Attempted Nov 23, 2025 - resulted in static pages only

### 2. adapter-static (Explicit Static) - REJECTED ❌
**What it does:** Explicitly generates static HTML for JAMstack deployments

**Configuration:**
- Would require `prerendering` all routes or accepting 404s
- Designed for sites with known routes (blog, docs)
- No server-side logic possible

**Why rejected:**
- ❌ Application requires server-side session handling
- ❌ Dynamic authentication flow not supported
- ❌ Same limitations as adapter-auto static mode
- ❌ Present in dependencies but unused
- ❌ Would require significant architectural redesign

### 3. Platform Adapters (Vercel/Netlify/Cloudflare) - REJECTED ❌
Examples: `@sveltejs/adapter-vercel`, `@sveltejs/adapter-netlify`

**What they do:** Generate platform-specific deployments

**Why rejected:**
- ❌ Vendor lock-in (not portable)
- ❌ Not applicable to self-hosted VPS infrastructure
- ❌ Additional costs
- ❌ Cannot deploy to Hostinger VPS
- ❌ Requires migration if changing providers
- ❌ Project philosophy: self-hosted, open infrastructure

### Comparison Table

| Aspect | adapter-auto | adapter-static | adapter-node | Vercel/Netlify |
|--------|-------------|----------------|-------------|----------------|
| **SSR Support** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Dynamic Routes** | ❌ No | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **Self-Hosted** | ❌ No | ⚠️ Possible | ✅ Yes | ❌ No |
| **Docker Ready** | ❌ No | ⚠️ Via static server | ✅ Yes | ❌ No |
| **Complexity** | ✅ Simple | ✅ Simple | ⚠️ Medium | ⚠️ Medium |
| **Cost** | Free | Free | Free | $$ |

---

## Activation Criteria

### Conditions to Re-evaluate this Decision

#### 1. Migrate to Vercel/Netlify
- **If:** Project requires managed hosting, no longer self-hosted
- **Action:** Switch to `adapter-vercel` or `adapter-netlify`
- **Timeline:** When cost/management outweighs benefits

#### 2. Application Becomes Purely Static
- **If:** No authentication, no server-side logic, pure marketing site
- **Action:** Consider simplifying to `adapter-static`
- **Benefit:** Reduced resource usage
- **Cost:** Would require architectural changes

#### 3. Performance Issues Arise
- **If:** Node.js runtime becomes bottleneck (unlikely at current scale)
- **Action:** Profile with `node --prof`, optimize hot paths
- **Alternative:** Could move to compiled language (not practical)

#### 4. Significant Scale Growth
- **If:** 10,000+ concurrent users
- **Action:** Consider distributed deployment, load balancing
- **Note:** adapter-node remains valid, just add infrastructure

---

## Rollback Plan

**If SSR proves fundamentally problematic:**

### Rollback Steps
1. Revert svelte.config.js to adapter-auto or adapter-static
2. Remove `frontend` service from docker-compose.prod.yml
3. Rebuild frontend: `npm run build`
4. Copy static files to Nginx: `/var/www/lexikon/`
5. Update nginx.conf to serve static files
6. Restart Nginx

### Execution Time
Approximately 2 hours (code changes + testing + deployment)

### Consequences
- ❌ Lose all SSR functionality
- ❌ Break authentication flows
- ❌ Lose dynamic routing
- ❌ Must redesign as static site

### Risk Assessment
**High Risk:** Rollback would break core application features. Not recommended unless adapter-node has insurmountable issues.

**Current Status:** No issues identified in production (Nov 24-27, 2025).

---

## Related Decisions

### ADR-0002: JWT Authentication Strategy
- **Link:** `docs/architecture/ADR-0002-jwt-authentication.md`
- **Relationship:** Requires SSR to implement secure session management
- **Dependency:** Cannot implement without SSR

### Future ADR Candidates
- Docker/Docker Compose infrastructure choices (not yet documented)
- Nginx reverse proxy architecture (not yet documented)
- SvelteKit framework selection vs React/Vue (not yet documented)

---

## Implementation Checklist

- [x] Install `@sveltejs/adapter-node@^5.4.0` in devDependencies
- [x] Update `svelte.config.js` to import adapter-node
- [x] Create `Dockerfile.frontend` with multi-stage build
- [x] Build Node.js runtime stage (FROM node:18-alpine)
- [x] Copy build artifacts and node_modules to runtime
- [x] Add `frontend` service to `docker-compose.prod.yml`
- [x] Configure service: image, ports, networks, depends_on
- [x] Add health check to frontend service
- [x] Update `nginx.conf` location / to proxy to frontend:3000
- [x] Configure proxy headers (Host, X-Real-IP, X-Forwarded-Proto)
- [x] Create `build-server.mjs` custom HTTP server entry point
- [x] Test SSR functionality: routes resolve without .html extensions
- [x] Test authentication flow: login → session → protected routes
- [x] Test API integration: frontend calls backend /api/health
- [x] Verify health checks passing for all containers
- [x] Document in this ADR with rationale and decision context

---

## Review & Approval

**Author:** Lead Developer
**Date:** 2025-11-27

**Reviewed By:** DevOps Team
**Review Date:** 2025-11-27
**Status:** ✅ Approved

**Implementation Verified:** 2025-11-24
**Tested In Production:** 2025-11-24 to 2025-11-27
**Status:** ✅ Stable, No Issues Reported

---

## Supporting Evidence

### Commits Implementing This Decision
- `d79ea67` - feat(frontend): Implement SvelteKit SSR with adapter-node
- `807e6f7` - fix(frontend): Update Dockerfile.frontend for proper SvelteKit SSR build setup
- `fb7ddba` - chore(deps): Install @sveltejs/adapter-node@^5.4.0

### Documentation References
- `DEPLOYMENT_HOSTINGER.md` - Initial deployment guide
- `docs/analyses/REX-2025-11-23-deployment-docker-frontend.md` - Problem analysis
- `docker-compose.prod.yml` - Frontend service configuration
- `Dockerfile.frontend` - Build process

### Production Verification
- ✅ SvelteKit SSR generating proper server directory
- ✅ Frontend container healthy on port 3000
- ✅ Nginx proxying to frontend successfully
- ✅ Dynamic routes functional (/login, /signup, /app)
- ✅ Authentication flow working end-to-end
- ✅ API integration verified (frontend → backend calls successful)

---

**ADR Document Version:** 1.0
**Last Updated:** 2025-11-27
**Maintainers:** DevOps Team, Frontend Team
