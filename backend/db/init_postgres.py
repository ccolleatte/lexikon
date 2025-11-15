"""
Initialize PostgreSQL database using Alembic migrations.
Run this script after starting PostgreSQL for the first time.
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from db.postgres import engine, Base, init_db


def run_migrations():
    """Run Alembic migrations to create database schema"""
    try:
        # Get alembic.ini path
        alembic_ini = backend_dir / "alembic.ini"

        if not alembic_ini.exists():
            print(f"✗ alembic.ini not found at {alembic_ini}")
            return False

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini))

        print("✓ Running Alembic migrations...")

        # Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        print("✓ Migrations complete!")
        return True

    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        return False


def verify_connection():
    """Verify connection to PostgreSQL"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 AS test")
            if result.scalar() == 1:
                print("✓ Connected to PostgreSQL")
                return True
        return False
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL: {e}")
        return False


def show_table_stats():
    """Show statistics about created tables"""
    try:
        with engine.connect() as conn:
            # Get list of tables
            result = conn.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)

            tables = [row[0] for row in result]

            print("\n--- Table Statistics ---")
            for table in tables:
                # Get row count
                count_result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = count_result.scalar()
                print(f"  {table}: {count} rows")

    except Exception as e:
        print(f"✗ Error getting table stats: {e}")


if __name__ == "__main__":
    print("=== Initializing PostgreSQL Database ===\n")

    # Get database URL from environment
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://lexikon:dev-secret@localhost:5432/lexikon"
    )
    print(f"Database URL: {db_url}\n")

    # Verify connection
    if not verify_connection():
        sys.exit(1)

    # Run migrations
    if not run_migrations():
        sys.exit(1)

    # Show statistics
    show_table_stats()

    print("\n✓ PostgreSQL initialization complete!")
