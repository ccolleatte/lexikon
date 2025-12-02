# Server Root Directory - Multi-Project Environment

This server hosts multiple projects and services.

## Projects

- **lexikon/** - Service Générique d'Ontologies Lexicales (main project)
  - See: `/root/lexikon/README.md`
  - Quickstart: `/root/lexikon/QUICKSTART.md`
  - Deployment: `/root/lexikon/DEPLOYMENT_HOSTINGER.md`

- **chessplorer/** - Chess analysis application
  - Maintained separately
  - Owner: ubuntu:ubuntu

- **n8n_data/** - n8n workflow automation data
  - Workflow engine data directory

## Shared Scripts

- **shared-scripts/cleanup-maintenance.sh** - System maintenance and Docker cleanup script

## System Configuration

- `.bashrc`, `.profile` - Shell configuration
- `.ssh/` - SSH keys and known hosts
- `.git-credentials` - Git authentication
- `.config/`, `.local/` - User configuration and cache

## Quick Commands

```bash
# Navigate to Lexikon project
cd /root/lexikon

# Run Lexikon deployment
bash scripts/deploy.sh

# Check Lexikon health
cd /root/lexikon && bash scripts/health-check.sh

# Run Lexikon tests
cd /root/lexikon && npm run test

# Server maintenance and cleanup
bash /root/shared-scripts/cleanup-maintenance.sh
```

## Directory Structure

```
/root/
├── lexikon/                      # Main project (see lexikon/README.md)
├── chessplorer/                  # Chess application
├── n8n_data/                     # n8n automation data
├── claude-code/                  # Claude Code CLI tool
├── shared-scripts/               # Shared utility scripts
├── README.md                     # This file
└── [System configs]
    ├── .bashrc, .profile
    ├── .ssh/
    ├── .git-credentials
    └── [other system files]
```

## Migration Notes

This server was restructured on 2025-12-02 to organize multiple projects:
- **Lexikon** project moved to `/root/lexikon/` for clarity and isolation
- Generic scripts moved to `/root/shared-scripts/`
- System-level configuration remains at `/root/`

All Lexikon-specific files are now self-contained in `/root/lexikon/` with the following structure:
- Source code: `backend/`, `src/` (frontend)
- Tests: `e2e/` (end-to-end)
- Documentation: `docs/`, `roadmap/`, `user-stories/`, `wireframes/`, `models/`
- Scripts: `scripts/` (deploy, health-check, rollback, validate)
- Configuration: package.json, docker-compose.yml, .env files
- Dependencies: node_modules/, venv/

For more information about the Lexikon project, see `/root/lexikon/README.md`.

Last updated: 2025-12-02
