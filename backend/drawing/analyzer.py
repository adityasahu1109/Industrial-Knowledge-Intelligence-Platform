import re
import json
from core.ollama_client import vision_analyze
from drawing.tiler import tile_image
from drawing.validator import validate_and_deduplicate

def extract_equipment_from_image(base64_image: str) -> list[dict]:
    """
    Sends an image to the vision model to extract equipment, valves, and instruments.
    """
    prompt = """
    Analyze this Piping and Instrumentation Diagram (P&ID) or industrial schematic.
    Identify all major equipment, instruments, and valves.
    Return ONLY a JSON array of objects with the following schema, and absolutely no other text:
    [
        {
            "tag": "P-101", 
            "type": "Pump", 
            "description": "Centrifugal pump"
        },
        {
            "tag": "FCV-205", 
            "type": "Valve", 
            "description": "Diaphragm valve"
        }
    ]
    IMPORTANT: Keep 'description' extremely short (1-3 words max). Do NOT include any measurements, dimensions, specs, or quote symbols in the description.
    Do NOT miss any components. Be exhaustive.
    If you cannot read the image or find no equipment, return [].
    """
    
    tiles = tile_image(base64_image)
    all_components = []
    
    for tile in tiles:
        raw_response = vision_analyze(prompt, tile)
        
        # Extract JSON array from conversational text
        match = re.search(r'\[.*\]', raw_response, re.DOTALL)
        clean_text = match.group(0) if match else raw_response
        
        try:
            data = json.loads(clean_text)
            if isinstance(data, list):
                all_components.extend(data)
        except json.JSONDecodeError:
            print(f"Failed to parse vision model JSON response. Raw output: {raw_response}")
            
    # Validate and deduplicate tags across all tiles
    validated = validate_and_deduplicate(all_components)
    return validated
