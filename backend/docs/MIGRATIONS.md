# Database Migrations Guide

This guide explains how to use Alembic for managing database schema changes in Lexikon.

## Overview

We use **Alembic**, a lightweight database migration tool for SQLAlchemy. It allows us to:
- Version control database schema changes
- Apply/revert migrations in any environment
- Document schema evolution over time
- Support both PostgreSQL (production) and SQLite (development)

## Setup

Alembic is already initialized in the `alembic/` directory.

```bash
cd backend
pip install -r requirements.txt
```

## Directory Structure

```
alembic/
├── versions/              # Migration files
│   └── 7beb871f4454_initial_schema...py   # First migration
├── env.py                 # Migration environment configuration
├── script.py.mako         # Migration template
└── README                 # Alembic README
```

## Common Commands

### 1. Create a New Migration

When you modify SQLAlchemy models, create a migration:

```bash
# Auto-generate from model changes (requires running database)
alembic revision --autogenerate -m "Add new column to users table"

# OR: Manual migration (for non-model changes)
alembic revision -m "Create indexes for performance"
```

**Note:** Auto-generate requires a working database connection (PostgreSQL or SQLite).

For development with SQLite:

```bash
DATABASE_URL="sqlite:///./lexikon.db" alembic revision --autogenerate -m "Migration message"
```

### 2. Apply Migrations (Upgrade)

Apply all pending migrations to bring database up-to-date:

```bash
alembic upgrade head
```

Apply specific number of migrations:

```bash
alembic upgrade +2  # Apply next 2 migrations
```

### 3. Rollback Migrations (Downgrade)

Revert to previous schema version:

```bash
alembic downgrade -1  # Rollback 1 step
alembic downgrade 7beb871f4454  # Rollback to specific migration ID
```

### 4. Check Current Version

```bash
alembic current
```

### 5. View Migration History

```bash
alembic history --verbose
```

## Writing Migrations Manually

When auto-generate doesn't work or for complex changes:

```python
"""Add webhook_url column to users table

Revision ID: abc123def456
Revises: 7beb871f4454
Create Date: 2025-11-20 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = '7beb871f4454'


def upgrade() -> None:
    """Add webhook_url column."""
    op.add_column('users', sa.Column('webhook_url', sa.String(), nullable=True))
    # Create index for performance
    op.create_index('ix_users_webhook_url', 'users', ['webhook_url'])


def downgrade() -> None:
    """Remove webhook_url column."""
    op.drop_index('ix_users_webhook_url', table_name='users')
    op.drop_column('users', 'webhook_url')
```

## Migration Best Practices

### ✅ DO:

- **Small, focused migrations**: One logical change per migration
- **Test upgrades and downgrades**: Always test both directions
- **Include downgrade logic**: Every upgrade should have corresponding downgrade
- **Use meaningful names**: `add_user_email_index` not `update_schema`
- **Add comments**: Document why the change is needed

### ❌ DON'T:

- **Mix multiple changes**: One migration = one purpose
- **Forget downgrade()**: All migrations must be reversible
- **Use raw SQL without checking database**: Use Alembic operations for portability
- **Skip testing**: Test migrations on both SQLite and PostgreSQL

## Database Compatibility

Lexikon supports both SQLite (development) and PostgreSQL (production).

### SQLite-Specific Notes:
- Some operations have limited support (e.g., ENUM types)
- Migrations should use portable operations from `alembic.op`

### PostgreSQL-Specific Notes:
- ENUM types are created with `sa.Enum(...)`
- Indexes and constraints are fully supported

Example that works on both:

```python
# ✅ Good - works on SQLite and PostgreSQL
op.add_column('users', sa.Column('is_verified', sa.Boolean(), default=False))

# ⚠️ PostgreSQL only - use sparingly
adoption_level_enum = sa.Enum('quick-project', 'research-project', 'production-api')
op.add_column('users', sa.Column('adoption_level', adoption_level_enum))
```

## Current Schema

The initial migration (`7beb871f4454`) creates:

### Tables:
1. **users** - User accounts and profiles
2. **oauth_accounts** - OAuth provider credentials
3. **api_keys** - API key storage (hashed)
4. **projects** - User projects
5. **project_members** - Project membership (many-to-many)
6. **terms** - Lexicon terms with full definitions
7. **onboarding_sessions** - Onboarding progress tracking
8. **llm_configs** - User LLM configuration (BYOK)

### Key Indexes:
- `users.email` - For login lookups
- `api_keys.key_hash` - For API key validation
- `terms.name` - For term search

## Production Deployment

### Before Deploying:

1. **Test migrations locally**:
   ```bash
   # On your development database
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```

2. **Backup production database**:
   ```bash
   pg_dump lexikon_prod > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

3. **Dry run** (if available):
   ```bash
   # Some tools allow previewing SQL without applying
   alembic upgrade head --sql
   ```

### Deploying Migrations:

```bash
# In production environment
DATABASE_URL="postgresql://user:pass@host/lexikon" alembic upgrade head
```

### Rollback If Issues:

```bash
DATABASE_URL="postgresql://user:pass@host/lexikon" alembic downgrade -1
```

## Troubleshooting

### "Can't find target database"

**Problem**: Alembic can't connect to database

**Solution**: Set DATABASE_URL or configure `alembic.ini`

```bash
export DATABASE_URL="sqlite:///./lexikon.db"
alembic upgrade head
```

### "No changes detected in models"

**Problem**: Auto-generate found no changes

**Possible causes**:
- Models haven't changed since last migration
- Model imports are missing
- Table is not tracked by SQLAlchemy `Base`

**Solution**: Check `alembic/env.py` imports all models

### "Unique constraint already exists"

**Problem**: Migration tries to create constraint that exists

**Solution**: Check migration is not being applied twice or has duplicate operations

### "Can't drop column - it's referenced"

**Problem**: Column is foreign key, can't drop directly

**Solution**: Drop foreign keys first, then column

```python
op.drop_constraint('fk_name', 'table_name')
op.drop_column('table_name', 'column_name')
```

## See Also

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/index.html)
- [Database Models](./db/postgres.py)
