import ollama
import json
import re
from typing import Generator
import sys

CHAT_MODEL = "llama3.1:8b"
VISION_MODEL = "minicpm-v"
EMBED_MODEL = "nomic-embed-text"

def verify_models():
    """Verify that all required models are pulled in Ollama."""
    try:
        models = [m.model for m in ollama.list().models]
        required = [CHAT_MODEL, VISION_MODEL, EMBED_MODEL]
        
        missing = []
        for req in required:
            # simple check since sometimes the tag is returned differently
            if not any(req in m for m in models):
                missing.append(req)
                
        if missing:
            print(f"ERROR: Missing Ollama models: {missing}", file=sys.stderr)
            print("Please run the following commands before starting the backend:", file=sys.stderr)
            for m in missing:
                print(f"  ollama pull {m}", file=sys.stderr)
            # We don't want to hard crash here during dev, but we want a clear error
            print("Backend might fail when these models are invoked.", file=sys.stderr)
        else:
            print(f"Ollama models verified: {required}")
    except Exception as e:
        print(f"ERROR connecting to Ollama: {e}", file=sys.stderr)
        print("Please ensure Ollama is running.", file=sys.stderr)

def chat_stream(system: str, user: str) -> Generator[str, None, None]:
    """Stream tokens from llama3.1:8b."""
    stream = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        stream=True,
        keep_alive=-1,
        options={"temperature": 0.2, "num_ctx": 8192}
    )
    for chunk in stream:
        yield chunk['message']['content']

def chat_json(system: str, user: str) -> dict:
    """Call llama3.1:8b and parse JSON response."""
    resp = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        keep_alive=-1,
        options={"temperature": 0.1}
    )
    raw = resp['message']['content']
    # Strip markdown fences
    clean = re.sub(r'```json|```', '', raw).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from LLM: {e}\nRaw output: {raw}")
        raise e

def embed(text: str) -> list[float]:
    """Generate embedding via nomic-embed-text."""
    resp = ollama.embeddings(model=EMBED_MODEL, prompt=text, keep_alive=-1)
    return resp["embedding"]
