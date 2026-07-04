from graph.neo4j_client import neo4j_client
from agents.entity_extractor import extract_entities

def store_entities_in_graph(doc_id: str, text_chunk: str):
    """
    Extracts entities from the text chunk and merges them into Neo4j.
    """
    if not neo4j_client.test_connection():
        print("Skipping graph builder: Neo4j not available.")
        return
        
    result = extract_entities(text_chunk)
    entities = result.get("entities", [])
    relationships = result.get("relationships", [])
    
    if not entities and not relationships:
        return
        
    # Standardize nodes (MERGE)
    for ent in entities:
        ent_id = ent.get("id", "").strip().upper()
        label = ent.get("label", "Entity").strip()
        if not ent_id:
            continue
            
        # Clean label for cypher (alphanumeric only)
        label = ''.join(e for e in label if e.isalnum()) or "Entity"
        
        query = f"""
        MERGE (n:{label} {{id: $id}})
        ON CREATE SET n.created_at = timestamp(), n.doc_id = $doc_id
        """
        neo4j_client.run_query(query, {"id": ent_id, "doc_id": doc_id})
        
    # Standardize relationships (MERGE)
    for rel in relationships:
        src = rel.get("source", "").strip().upper()
        tgt = rel.get("target", "").strip().upper()
        rel_type = rel.get("type", "RELATED_TO").strip().upper()
        
        if not src or not tgt:
            continue
            
        rel_type = ''.join(e for e in rel_type if e.isalnum() or e == '_') or "RELATED_TO"
        
        # We merge relationships between ANY two nodes matching the IDs
        query = f"""
        MATCH (a {{id: $src}}), (b {{id: $tgt}})
        MERGE (a)-[r:{rel_type}]->(b)
        ON CREATE SET r.doc_id = $doc_id
        """
        neo4j_client.run_query(query, {"src": src, "tgt": tgt, "doc_id": doc_id})

def get_graph_data():
    """
    Retrieves a simplified version of the graph for frontend visualization.
    Limits to 200 nodes to prevent UI overload.
    """
    if not neo4j_client.test_connection():
        return {"nodes": [], "links": []}
        
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN 
        id(n) as node_id, labels(n)[0] as label, n.id as name,
        id(m) as target_id, type(r) as rel_type
    LIMIT 200
    """
    
    results = neo4j_client.run_query(query)
    
    nodes = {}
    links = []
    
    for row in results:
        # Add source node
        n_id = str(row['node_id'])
        if n_id not in nodes:
            nodes[n_id] = {"id": n_id, "label": row['label'], "name": row['name']}
            
        # Add relationship and target node if exists
        if row['target_id'] is not None:
            t_id = str(row['target_id'])
            # Since the query might not have pulled the target node's properties directly,
            # this is a simplified view. 
            links.append({
                "source": n_id,
                "target": t_id,
                "type": row['rel_type']
            })
            
    # Need a secondary query to ensure we have all target node details
    if links:
        target_ids = [int(l['target']) for l in links]
        t_query = "MATCH (n) WHERE id(n) IN $ids RETURN id(n) as node_id, labels(n)[0] as label, n.id as name"
        t_results = neo4j_client.run_query(t_query, {"ids": target_ids})
        for row in t_results:
            n_id = str(row['node_id'])
            if n_id not in nodes:
                nodes[n_id] = {"id": n_id, "label": row['label'], "name": row['name']}
                
    return {
        "nodes": list(nodes.values()),
        "links": links
    }
