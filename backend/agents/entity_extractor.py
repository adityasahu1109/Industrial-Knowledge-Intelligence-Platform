from core.ollama_client import chat_json
from typing import Dict, Any

ENTITY_EXTRACTION_PROMPT = """You are an industrial data extraction AI.
Analyze the following text and extract highly specific industrial entities and relationships.

STRICT RULES:
1. ONLY extract specific Equipment Tags (e.g., "P-101", "E-301"). DO NOT extract generic words like "Pump" or "System" as entities.
2. Extract specific Maintenance Events (e.g., "Seal Replacement", "Rotor Balancing").
3. Extract specific Dates or Intervals (e.g., "Q1 2024", "6-month").
4. Keep IDs extremely short and standardized (uppercase).
5. For relationships, use standard UPPERCASE types (e.g., MAINTAINED_ON, PART_OF, EXPERIENCED).

Return the result STRICTLY as a JSON object with this exact structure:
{
  "entities": [
    {"id": "SPECIFIC_TAG_OR_EVENT", "label": "Equipment|Event|Date", "properties": {"type": "..."}}
  ],
  "relationships": [
    {"source": "entity_id_1", "target": "entity_id_2", "type": "RELATIONSHIP_TYPE"}
  ]
}

If no highly specific entities exist, return {"entities": [], "relationships": []}.
Output ONLY JSON, no markdown formatting or explanations.
"""

def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extracts entities and relationships from a text chunk using the LLM.
    """
    prompt = f"Text to analyze:\n{text}"
    try:
        result = chat_json(ENTITY_EXTRACTION_PROMPT, prompt)
        return result
    except Exception as e:
        print(f"Entity extraction failed: {e}")
        return {"entities": [], "relationships": []}
