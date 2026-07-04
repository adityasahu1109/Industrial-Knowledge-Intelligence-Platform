from core.ollama_client import chat_json
from typing import Dict, Any

ENTITY_EXTRACTION_PROMPT = """You are an industrial data extraction AI.
Analyze the following text and extract relevant industrial entities and relationships.
Focus on:
1. Equipment Tags (e.g., P-101, E-301, V-205)
2. Equipment Types (e.g., Pump, Heat Exchanger, Valve)
3. Maintenance Events (e.g., inspection, seal replacement, failure)
4. Dates or Intervals (e.g., Q1 2024, 6-month, 30 days)

Return the result STRICTLY as a JSON object with this exact structure:
{
  "entities": [
    {"id": "entity_name_or_tag", "label": "Equipment|Event|Date", "properties": {"type": "..."}}
  ],
  "relationships": [
    {"source": "entity_id_1", "target": "entity_id_2", "type": "INVOLVES|OCCURRED_ON|PART_OF"}
  ]
}

If no relevant entities exist, return {"entities": [], "relationships": []}.
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
