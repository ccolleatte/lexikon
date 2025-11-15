"""
Initialize Neo4j database with constraints, indexes, and sample data.
Run this script after starting Neo4j for the first time.
"""

import os
from neo4j import GraphDatabase


def read_cypher_file(filepath: str) -> list[str]:
    """Read Cypher commands from file and split by semicolon"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Remove comments and split by newlines
    statements = []
    current_statement = []

    for line in content.split("\n"):
        # Skip full-line comments
        if line.strip().startswith("//"):
            continue

        # Add line to current statement
        if line.strip():
            current_statement.append(line)

        # If line ends with semicolon, we have a complete statement
        if line.strip().endswith(";"):
            statements.append("\n".join(current_statement))
            current_statement = []

    # Add any remaining statement
    if current_statement:
        statements.append("\n".join(current_statement))

    return [s.strip() for s in statements if s.strip()]


def init_neo4j(uri: str, user: str, password: str):
    """Initialize Neo4j with schema from cypher file"""
    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        # Verify connection
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            if result.single()["test"] != 1:
                raise Exception("Failed to connect to Neo4j")
            print("✓ Connected to Neo4j")

        # Read and execute cypher file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cypher_file = os.path.join(script_dir, "neo4j_init.cypher")

        statements = read_cypher_file(cypher_file)
        print(f"\n✓ Found {len(statements)} Cypher statements to execute")

        with driver.session() as session:
            for i, statement in enumerate(statements, 1):
                # Skip empty statements
                if not statement or statement.startswith("//"):
                    continue

                try:
                    session.run(statement)
                    # Extract first few words for logging
                    first_words = " ".join(statement.split()[:5])
                    print(f"  [{i}/{len(statements)}] ✓ {first_words}...")
                except Exception as e:
                    print(f"  [{i}/{len(statements)}] ✗ Error: {e}")
                    print(f"     Statement: {statement[:100]}...")

        print("\n✓ Neo4j initialization complete!")

        # Show stats
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n) AS label, COUNT(n) AS count
                ORDER BY count DESC
            """)
            print("\n--- Node Statistics ---")
            for record in result:
                labels = record["label"]
                count = record["count"]
                print(f"  {labels[0] if labels else 'Unknown'}: {count}")

    except Exception as e:
        print(f"\n✗ Error initializing Neo4j: {e}")
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    # Get configuration from environment or use defaults
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "dev-secret")

    print("=== Initializing Neo4j Database ===\n")
    print(f"URI: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")
    print()

    init_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
