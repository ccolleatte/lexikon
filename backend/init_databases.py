#!/usr/bin/env python3
"""
Initialize both PostgreSQL and Neo4j databases for Lexikon.
Run this script after starting both database services.

Usage:
    python init_databases.py [--postgres-only | --neo4j-only]
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db.init_postgres import verify_connection as verify_postgres, run_migrations
from db.init_neo4j import init_neo4j
import os


def main():
    parser = argparse.ArgumentParser(description="Initialize Lexikon databases")
    parser.add_argument(
        "--postgres-only",
        action="store_true",
        help="Initialize only PostgreSQL"
    )
    parser.add_argument(
        "--neo4j-only",
        action="store_true",
        help="Initialize only Neo4j"
    )
    args = parser.parse_args()

    init_postgres = not args.neo4j_only
    init_neo = not args.postgres_only

    print("=" * 60)
    print("   LEXIKON DATABASE INITIALIZATION")
    print("=" * 60)
    print()

    success = True

    # Initialize PostgreSQL
    if init_postgres:
        print("📦 PostgreSQL Setup")
        print("-" * 60)
        try:
            if verify_postgres():
                if run_migrations():
                    print("✓ PostgreSQL initialized successfully\n")
                else:
                    print("✗ PostgreSQL migration failed\n")
                    success = False
            else:
                print("✗ PostgreSQL connection failed\n")
                success = False
        except Exception as e:
            print(f"✗ PostgreSQL error: {e}\n")
            success = False

    # Initialize Neo4j
    if init_neo:
        print("🔗 Neo4j Setup")
        print("-" * 60)
        try:
            NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
            NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "dev-secret")

            init_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
            print("✓ Neo4j initialized successfully\n")
        except Exception as e:
            print(f"✗ Neo4j error: {e}\n")
            success = False

    # Final status
    print("=" * 60)
    if success:
        print("✅ All databases initialized successfully!")
        print()
        print("Next steps:")
        print("  1. Start the backend: cd backend && python main.py")
        print("  2. Start the frontend: cd frontend && npm run dev")
        print("  3. Visit http://localhost:5173")
    else:
        print("❌ Database initialization failed")
        print()
        print("Troubleshooting:")
        print("  1. Ensure Docker Compose is running: docker-compose up -d")
        print("  2. Check logs: docker-compose logs")
        print("  3. Verify .env file has correct credentials")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()
