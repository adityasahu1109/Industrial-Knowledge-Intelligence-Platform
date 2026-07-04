from neo4j import GraphDatabase
from core.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import sys

class Neo4jClient:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, 
                auth=(NEO4J_USER, NEO4J_PASSWORD),
                max_connection_lifetime=300
            )
        except Exception as e:
            print(f"Failed to initialize Neo4j driver: {e}", file=sys.stderr)
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def test_connection(self) -> bool:
        if not self.driver:
            return False
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Neo4j connection test failed: {e}", file=sys.stderr)
            return False

    def run_query(self, query: str, parameters=None):
        if not self.driver:
            print("Warning: Neo4j driver not initialized, query skipped.")
            return []
            
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# Singleton instance
neo4j_client = Neo4jClient()
