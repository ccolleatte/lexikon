"""
Neo4j graph database for ontology relationships.
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import os

# Neo4j connection from environment
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "dev-secret")


class Neo4jClient:
    """Neo4j client wrapper for ontology operations"""

    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()

    def verify_connectivity(self):
        """Verify connection to Neo4j"""
        with self.driver.session() as session:
            result = session.run("RETURN 1 AS test")
            return result.single()["test"] == 1

    # Term operations
    def create_term_node(self, term_id: str, name: str, definition: str, properties: Dict[str, Any] = None):
        """Create a Term node in the graph"""
        with self.driver.session() as session:
            query = """
            CREATE (t:Term {
                id: $term_id,
                name: $name,
                definition: $definition
            })
            SET t += $properties
            RETURN t
            """
            result = session.run(
                query,
                term_id=term_id,
                name=name,
                definition=definition,
                properties=properties or {},
            )
            return result.single()

    def get_term_node(self, term_id: str) -> Optional[Dict[str, Any]]:
        """Get a Term node by ID"""
        with self.driver.session() as session:
            query = "MATCH (t:Term {id: $term_id}) RETURN t"
            result = session.run(query, term_id=term_id)
            record = result.single()
            return dict(record["t"]) if record else None

    def delete_term_node(self, term_id: str):
        """Delete a Term node and all its relationships"""
        with self.driver.session() as session:
            query = "MATCH (t:Term {id: $term_id}) DETACH DELETE t"
            session.run(query, term_id=term_id)

    # Relationship operations
    def create_relationship(
        self,
        from_term_id: str,
        to_term_id: str,
        rel_type: str,
        properties: Dict[str, Any] = None,
    ):
        """
        Create a relationship between two terms.

        Args:
            from_term_id: Source term ID
            to_term_id: Target term ID
            rel_type: Relationship type (IS_A, PART_OF, RELATED_TO, SYNONYM_OF)
            properties: Optional properties (confidence, source, validated, etc.)
        """
        with self.driver.session() as session:
            query = f"""
            MATCH (a:Term {{id: $from_id}})
            MATCH (b:Term {{id: $to_id}})
            CREATE (a)-[r:{rel_type}]->(b)
            SET r += $properties
            RETURN r
            """
            result = session.run(
                query,
                from_id=from_term_id,
                to_id=to_term_id,
                properties=properties or {},
            )
            return result.single()

    def get_relationships(self, term_id: str, rel_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all relationships for a term.

        Args:
            term_id: Term ID
            rel_type: Optional filter by relationship type
        """
        with self.driver.session() as session:
            if rel_type:
                query = f"""
                MATCH (t:Term {{id: $term_id}})-[r:{rel_type}]-(other:Term)
                RETURN type(r) AS rel_type, properties(r) AS props, other
                """
            else:
                query = """
                MATCH (t:Term {id: $term_id})-[r]-(other:Term)
                RETURN type(r) AS rel_type, properties(r) AS props, other
                """

            result = session.run(query, term_id=term_id)
            relationships = []
            for record in result:
                relationships.append({
                    "type": record["rel_type"],
                    "properties": dict(record["props"]) if record["props"] else {},
                    "term": dict(record["other"]),
                })
            return relationships

    def delete_relationship(self, from_term_id: str, to_term_id: str, rel_type: str):
        """Delete a specific relationship between two terms"""
        with self.driver.session() as session:
            query = f"""
            MATCH (a:Term {{id: $from_id}})-[r:{rel_type}]->(b:Term {{id: $to_id}})
            DELETE r
            """
            session.run(query, from_id=from_term_id, to_id=to_term_id)

    # Discovery & suggestions
    def find_potential_relations(self, term_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Find potential related terms using graph traversal.
        Useful for suggesting relations based on existing graph structure.
        """
        with self.driver.session() as session:
            query = """
            MATCH path = (t:Term {id: $term_id})-[*1..%d]-(other:Term)
            WHERE t <> other
            WITH other,
                 COUNT(DISTINCT path) AS path_count,
                 MIN(LENGTH(path)) AS min_distance
            RETURN other, path_count, min_distance
            ORDER BY path_count DESC, min_distance ASC
            LIMIT 20
            """ % max_depth

            result = session.run(query, term_id=term_id)
            suggestions = []
            for record in result:
                suggestions.append({
                    "term": dict(record["other"]),
                    "path_count": record["path_count"],
                    "distance": record["min_distance"],
                })
            return suggestions

    def find_synonyms(self, term_id: str) -> List[Dict[str, Any]]:
        """Find all synonyms of a term"""
        return self.get_relationships(term_id, rel_type="SYNONYM_OF")

    def find_hypernyms(self, term_id: str) -> List[Dict[str, Any]]:
        """Find all hypernyms (IS_A relationship) of a term"""
        with self.driver.session() as session:
            query = """
            MATCH (t:Term {id: $term_id})-[:IS_A]->(parent:Term)
            RETURN parent
            """
            result = session.run(query, term_id=term_id)
            return [dict(record["parent"]) for record in result]

    def find_hyponyms(self, term_id: str) -> List[Dict[str, Any]]:
        """Find all hyponyms (reverse IS_A) of a term"""
        with self.driver.session() as session:
            query = """
            MATCH (child:Term)-[:IS_A]->(t:Term {id: $term_id})
            RETURN child
            """
            result = session.run(query, term_id=term_id)
            return [dict(record["child"]) for record in result]

    def find_shortest_path(self, from_term_id: str, to_term_id: str) -> Optional[List[Dict[str, Any]]]:
        """Find shortest path between two terms"""
        with self.driver.session() as session:
            query = """
            MATCH path = shortestPath((a:Term {id: $from_id})-[*]-(b:Term {id: $to_id}))
            RETURN [node IN nodes(path) | node] AS nodes,
                   [rel IN relationships(path) | type(rel)] AS rel_types
            """
            result = session.run(query, from_id=from_term_id, to_id=to_term_id)
            record = result.single()
            if not record:
                return None

            return {
                "nodes": [dict(node) for node in record["nodes"]],
                "relationships": record["rel_types"],
            }

    # Bulk operations
    def bulk_create_terms(self, terms: List[Dict[str, Any]]):
        """Create multiple term nodes at once"""
        with self.driver.session() as session:
            query = """
            UNWIND $terms AS term
            CREATE (t:Term {
                id: term.id,
                name: term.name,
                definition: term.definition
            })
            SET t += term.properties
            """
            session.run(query, terms=terms)

    def bulk_create_relationships(self, relationships: List[Dict[str, Any]]):
        """
        Create multiple relationships at once.

        Each relationship should have: from_id, to_id, rel_type, properties
        """
        with self.driver.session() as session:
            query = """
            UNWIND $rels AS rel
            MATCH (a:Term {id: rel.from_id})
            MATCH (b:Term {id: rel.to_id})
            CALL apoc.create.relationship(a, rel.rel_type, rel.properties, b) YIELD rel AS r
            RETURN count(r)
            """
            # Note: This requires APOC plugin. For vanilla Neo4j, we'd need to loop.
            # Fallback for vanilla:
            for rel in relationships:
                self.create_relationship(
                    rel["from_id"],
                    rel["to_id"],
                    rel["rel_type"],
                    rel.get("properties", {}),
                )

    # Statistics & analytics
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the ontology graph"""
        with self.driver.session() as session:
            query = """
            MATCH (t:Term)
            OPTIONAL MATCH (t)-[r]-()
            RETURN COUNT(DISTINCT t) AS term_count,
                   COUNT(r) AS relationship_count,
                   COUNT(DISTINCT type(r)) AS unique_rel_types
            """
            result = session.run(query)
            record = result.single()
            return {
                "term_count": record["term_count"],
                "relationship_count": record["relationship_count"],
                "unique_rel_types": record["unique_rel_types"],
            }

    def get_term_degree(self, term_id: str) -> int:
        """Get the number of relationships a term has"""
        with self.driver.session() as session:
            query = """
            MATCH (t:Term {id: $term_id})-[r]-()
            RETURN COUNT(r) AS degree
            """
            result = session.run(query, term_id=term_id)
            record = result.single()
            return record["degree"] if record else 0


# Global client instance
neo4j_client = Neo4jClient()


# Helper functions for FastAPI
def get_neo4j() -> Neo4jClient:
    """Dependency for FastAPI routes"""
    return neo4j_client


def close_neo4j():
    """Cleanup function"""
    neo4j_client.close()
