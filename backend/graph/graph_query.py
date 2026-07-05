from graph.neo4j_client import neo4j_client

def get_node_details(node_id: str):
    """
    Fetches detailed information for a specific node (by application id)
    and all its first-degree connections.
    """
    if not neo4j_client.test_connection():
        return None
        
    query = """
    MATCH (n {id: $node_id})
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN 
        labels(n)[0] as label, n.id as name, n as properties,
        type(r) as rel_type, labels(m)[0] as connected_label, m.id as connected_name, m as connected_properties,
        startNode(r) = n as is_outgoing, r.doc_id as doc_id
    """
    
    results = neo4j_client.run_query(query, {"node_id": node_id})
    
    if not results:
        return None
        
    # The first row contains the primary node's properties
    node_data = {
        "id": node_id,
        "label": results[0]["label"],
        "name": results[0]["name"],
        "properties": dict(results[0]["properties"].items()),
        "connections": []
    }
    
    for row in results:
        if row["connected_name"]:
            node_data["connections"].append({
                "id": row["connected_name"],
                "label": row["connected_label"],
                "name": row["connected_name"],
                "type": row["rel_type"],
                "direction": "outgoing" if row["is_outgoing"] else "incoming",
                "doc_id": row["doc_id"]
            })
            
    return node_data

def get_equipment_timeline(equipment_id: str):
    """
    Fetches chronologically sortable events related to an equipment.
    In our schema, Events and Dates are connected to Equipment.
    """
    if not neo4j_client.test_connection():
        return []
        
    # We look for (Event)-[r]-(Equipment) and (Event)-[r]-(Date)
    # This is a simplified timeline extraction based on synthetic docs
    query = """
    MATCH (eq:Equipment {id: $eq_id})-[r1]-(ev:Event)
    OPTIONAL MATCH (ev)-[r2]-(d:Date)
    RETURN 
        ev.id as event_name, 
        type(r1) as relation,
        d.id as date,
        ev.doc_id as doc_id
    """
    
    results = neo4j_client.run_query(query, {"eq_id": equipment_id})
    
    timeline = []
    for row in results:
        timeline.append({
            "event": row["event_name"],
            "relation": row["relation"],
            "date": row["date"] or "Unknown Date",
            "doc_id": row["doc_id"]
        })
        
    return timeline
