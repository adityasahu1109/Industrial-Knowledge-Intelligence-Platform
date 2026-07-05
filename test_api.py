import time
import requests
import json
import sys

API_URL = "http://127.0.0.1:8000/api"

queries = [
    "When was P-101 last inspected and what were the findings?",
    "What are the required PPE for pump maintenance?",
    "What was the root cause of the P-101 seal failure on January 15?",
    "Why is the heat transfer coefficient of E-301 declining?",
    "What equipment is interconnected with E-301?"
]

print("Starting query tests...\n")

for i, query in enumerate(queries, 1):
    print("=" * 80)
    print(f"Test Query {i}: {query}")
    print("-" * 80)
    
    response = requests.post(
        f"{API_URL}/chat/query",
        json={"query": query, "mode": "detailed"},
        stream=True
    )
    
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        continue
        
    full_text = ""
    sources = []
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith("data: "):
                try:
                    payload = json.loads(decoded[6:])
                    
                    if "token" in payload and payload["token"]:
                        full_text += payload["token"]
                        sys.stdout.write(payload["token"])
                        sys.stdout.flush()
                        
                    if payload.get("done") and "sources" in payload:
                        sources = payload["sources"]
                except json.JSONDecodeError:
                    pass
    
    print("\n\nSOURCES:")
    if not sources:
        print("  No sources returned.")
    for src in sources:
        print(f"  - {src.get('filename', 'Unknown')} (Page {src.get('page', '?')})")
    print("=" * 80 + "\n")
