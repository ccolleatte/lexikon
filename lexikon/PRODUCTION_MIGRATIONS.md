# Database Migrations Guide - Lexikon

**Date:** 2025-11-23
**Tool:** Alembic 1.12.1
**Purpose:** Schema versioning, deployment automation, and rollback capability

---

## 📋 Overview

Lexikon uses **Alembic** for database schema management. This allows:

- ✅ Version control for database schema
- ✅ Automatic tracking of all schema changes
- ✅ Safe deployments with rollback capability
- ✅ Team collaboration on schema changes
- ✅ Production consistency across environments

**Current Migration History:**

```
✓ 7beb871f4454 - Initial schema (users, terms, api_keys, etc.)
✓ b9d0965451a3 - Performance indexes for queries
✓ f36a73221bb3 - Webhooks table and delivery tracking
```

---

## 🚀 Quick Start - Deployment

### Apply All Pending Migrations

In production, migrations are applied automatically during deployment:

```bash
# On your VPS, in /opt/lexikon directory
cd /opt/lexikon/backend

# Apply all pending migrations
alembic upgrade head

# Verify current migration status
alembic current

# View migration history
alembic history --verbose
```

### Example Output

```bash
$ alembic current
f36a73221bb3

$ alembic history --verbose
<base> -> 7beb871f4454 (head), Initial schema (users, terms, api_keys)
7beb871f4454 -> b9d0965451a3, Performance indexes for queries
b9d0965451a3 -> f36a73221bb3, Webhooks table and delivery tracking
```

---

## 💾 Workflow - Creating New Migrations

### When Adding New Models or Schema Changes

**Step 1: Create the model in code**

```python
# backend/models.py
class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

**Step 2: Generate migration automatically**

```bash
cd backend

# Auto-generate migration from models
alembic revision --autogenerate -m "Add my_table model"

# Output: Creating new migration:
# alembic/versions/abc123xyz_add_my_table_model.py
```

**Step 3: Review the generated migration**

```bash
# Check what was generated
cat alembic/versions/abc123xyz_add_my_table_model.py

# Verify:
# ✓ upgrade() has correct CREATE TABLE / ALTER statements
# ✓ downgrade() has inverse operations (DROP TABLE)
# ✓ Foreign keys are correct
# ✓ Indexes are included
```

**Step 4: Test locally**

```bash
# First time - apply migrations
alembic upgrade head

# Test your code works
pytest tests/

# Verify data integrity
docker exec lexikon-postgres psql -U lexikon -c "\d"
```

**Step 5: Test rollback**

```bash
# Rollback one migration
alembic downgrade -1

# Test that code still works without the new table
pytest tests/

# Re-apply
alembic upgrade head
```

**Step 6: Commit**

```bash
git add alembic/versions/abc123xyz_add_my_table_model.py
git commit -m "db(migration): Add my_table model"
```

---

## ⚙️ Configuration

### Environment Setup

The alembic configuration reads DATABASE_URL from environment:

```python
# alembic/env.py (lines 27-30)
if not config.get_section(config.config_ini_section).get("sqlalchemy.url"):
    from db.postgres import DATABASE_URL
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

**Environment Variables Required:**

```bash
# For local testing:
export DATABASE_URL="postgresql://lexikon:password@localhost:5432/lexikon"

# In production (.env.prod):
DATABASE_URL="postgresql://lexikon:PASSWORD@postgres:5432/lexikon"
```

### alembic.ini Configuration

Key settings:

```ini
# Connection string (populated from DATABASE_URL)
sqlalchemy.url =

# File format for auto-generated migrations
sqlalchemy_distinguish_binary = true

# Location of version files
version_locations = alembic/versions

# Encoding for alembic
encoding = utf-8
```

---

## 🔄 Common Operations

### View All Migrations

```bash
alembic history --verbose

# Example output:
# <base> -> 7beb871f4454 (head), Initial schema (users, terms, api_keys)
# 7beb871f4454 -> b9d0965451a3, Performance indexes for queries
# b9d0965451a3 -> f36a73221bb3, Webhooks table and delivery tracking
```

### Check Current Migration Status

```bash
alembic current

# Output: f36a73221bb3 (on head)
```

### Rollback to Previous Version

```bash
# Rollback 1 migration (two-step undo)
alembic downgrade -1

# Rollback to specific migration
alembic downgrade 7beb871f4454

# Rollback all (nuclear option - removes all schema)
alembic downgrade base
```

### Re-apply After Rollback

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade 7beb871f4454
```

---

## 🔍 Migration File Structure

### Auto-generated Migration Example

```python
"""Add my_table model

Revision ID: abc123xyz
Revises: f36a73221bb3
Create Date: 2025-11-23 10:15:30.123456

"""
from alembic import op
import sqlalchemy as sa


revision = 'abc123xyz'
down_revision = 'f36a73221bb3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add my_table."""
    op.create_table(
        'my_table',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop my_table."""
    op.drop_table('my_table')
```

**Key Components:**

- `revision` - Unique ID for this migration (auto-generated)
- `down_revision` - Previous migration ID (forms a chain)
- `upgrade()` - Forward migration (apply changes)
- `downgrade()` - Backward migration (undo changes)

---

## 🐳 Docker Integration

### In docker-compose.prod.yml

Migrations are applied during deployment via the deployment script:

```bash
# deploy.sh (example implementation)
cd /opt/lexikon/backend
alembic upgrade head
```

### Ensuring Dependencies

The backend container waits for postgres to be healthy before applying migrations:

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

This ensures the database is ready before migrations run.

---

## ⚠️ Best Practices

### 1. Always Test Locally First

```bash
# Create new migration
alembic revision --autogenerate -m "my change"

# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### 2. Keep Migrations Small

❌ DON'T: Add 5 tables in one migration
✅ DO: One migration per logical change

### 3. Use Descriptive Names

```bash
# Good
alembic revision --autogenerate -m "Add webhooks table and delivery tracking"

# Bad
alembic revision --autogenerate -m "Update schema"
```

### 4. Write Both upgrade() AND downgrade()

Every migration must be reversible:

```python
def upgrade():
    op.create_table('my_table', ...)

def downgrade():
    op.drop_table('my_table')  # Must be in reverse order!
```

### 5. Test Rollback on Production

After deploying a migration:

```bash
# Verify it works
curl https://your-domain.com/api/health

# Test rollback doesn't break app
alembic downgrade -1

# The app should still work (old schema)
curl https://your-domain.com/api/health

# Re-apply
alembic upgrade head
```

### 6. Never Modify Applied Migrations

❌ DON'T: Edit `alembic/versions/abc123xyz_*.py` after deploying
✅ DO: Create a new migration to fix it

### 7. Handle Data Migrations Carefully

For changing data (not just schema):

```python
def upgrade():
    # 1. Add new column
    op.add_column('users', sa.Column('new_field', sa.String()))

    # 2. Migrate data
    op.execute("UPDATE users SET new_field = 'default'")

    # 3. Make it required
    op.alter_column('users', 'new_field', nullable=False)

def downgrade():
    # Reverse: remove nullable constraint first
    op.alter_column('users', 'new_field', nullable=True)

    # Then drop column
    op.drop_column('users', 'new_field')
```

---

## 🚨 Emergency: Rollback from Production

If a migration breaks production:

```bash
# 1. Check current status
alembic current

# 2. Identify the bad migration
alembic history --verbose

# 3. Rollback to previous version
alembic downgrade -1

# 4. Restart application
docker-compose -f docker-compose.prod.yml restart backend

# 5. Verify service is healthy
curl https://your-domain.com/api/health

# 6. Investigate the issue
docker logs lexikon-backend | tail -100

# 7. Create a new migration to fix it
alembic revision --autogenerate -m "Fix broken migration"
```

---

## 📊 Schema Inspection

### View Current Schema

```bash
# Connect to postgres container
docker exec -it lexikon-postgres psql -U lexikon -d lexikon

# List all tables
\dt

# Describe a table
\d users

# List all indexes
\di

# Exit
\q
```

### Check Migration Table

Alembic tracks applied migrations in `alembic_version` table:

```sql
-- Connect to database
psql -U lexikon -d lexikon

-- Check applied migrations
SELECT * FROM alembic_version;

-- Output:
-- version_num
-- f36a73221bb3
```

---

## 🔗 Related Documentation

- **DEPLOYMENT_HOSTINGER.md** - Production deployment procedures
- **PRODUCTION_OPERATIONS.md** - Day-to-day operations guide
- **backend/alembic/** - Migration files and configuration

---

## 📞 Troubleshooting

### Migration Won't Apply

```bash
# Check syntax errors
python -m py_compile alembic/versions/abc123xyz_*.py

# Try running with verbose output
alembic upgrade head --sql

# Check database connection
psql -U lexikon -d lexikon -c "SELECT 1"
```

### Migration Conflicts

```bash
# If multiple developers created migrations simultaneously:
alembic heads

# Merge branches (requires manual merging)
# Edit down_revision to point to correct parent
```

### Alembic Table Doesn't Exist

```bash
# Initialize tracking table
alembic stamp head

# Now migrations will track correctly
alembic current
```

---

**Last Updated:** 2025-11-23
**Maintained By:** Development Team
**Version:** 1.0

