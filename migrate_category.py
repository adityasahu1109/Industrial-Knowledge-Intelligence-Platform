import sqlite3
import json
import os
import sys

# 1. SQLite Migration
print("Starting SQLite Migration...")
try:
    conn = sqlite3.connect("backend/industrial_knowledge.db")
    c = conn.cursor()
    # Check if category column exists
    c.execute("PRAGMA table_info(documents)")
    columns = [info[1] for info in c.fetchall()]
    if "category" not in columns:
        print("Adding 'category' column to 'documents' table...")
        c.execute("ALTER TABLE documents ADD COLUMN category VARCHAR NOT NULL DEFAULT 'operational'")
        conn.commit()
        print("SQLite Migration Successful.")
    else:
        print("'category' column already exists in SQLite.")
    conn.close()
except Exception as e:
    print(f"SQLite Migration Failed: {e}")

# 2. ChromaDB Migration
print("\nStarting ChromaDB Migration...")
try:
    # Need to add backend to sys.path to import
    sys.path.append(os.path.abspath('backend'))
    from core.database import get_collection
    collection = get_collection()
    
    # Get all existing documents
    results = collection.get()
    
    ids = results["ids"]
    metadatas = results["metadatas"]
    
    if not ids:
        print("ChromaDB is empty, no migration needed.")
        sys.exit(0)
        
    updated_ids = []
    updated_metadatas = []
    
    for doc_id, meta in zip(ids, metadatas):
        if meta and "category" not in meta:
            meta["category"] = "operational"
            updated_ids.append(doc_id)
            updated_metadatas.append(meta)
            
    if updated_ids:
        print(f"Updating metadata for {len(updated_ids)} chunks...")
        collection.update(ids=updated_ids, metadatas=updated_metadatas)
        print("ChromaDB Migration Successful.")
    else:
        print("All chunks already have 'category' metadata.")
except Exception as e:
    print(f"ChromaDB Migration Failed: {e}")
