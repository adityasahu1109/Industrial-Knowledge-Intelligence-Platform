import re
import json
from core.ollama_client import vision_analyze
from drawing.tiler import tile_image

# Regex to validate standard industrial tags
TAG_REGEX = re.compile(r'^[A-Z]{1,4}-?\d{2,4}[A-Z]?$')

def is_valid_tag(tag: str) -> bool:
    return bool(TAG_REGEX.match(tag))

def extract_drawing_data(base64_image: str) -> dict:
    """
    Sends an image to the vision model to extract title block, equipment, and topology.
    Uses tiling, multi-pass extraction, and regex validation.
    """
    
    title_prompt = """
    Analyze this tile of a Piping and Instrumentation Diagram (P&ID) or industrial schematic.
    Extract the title block information. 
    Return ONLY a JSON object exactly like this:
    {
      "drawing_number": "",
      "revision": "",
      "title": "",
      "date": "",
      "unit_area": ""
    }
    If the tile does not contain a title block, leave the fields empty strings. Do not include any other text.
    """
    
    comp_prompt = """
    Analyze this tile of a Piping and Instrumentation Diagram (P&ID) or industrial schematic.
    Identify all equipment, instruments, valves, and their connections.
    Return ONLY a JSON object exactly like this, with NO other text:
    {
      "equipment": ["P-101", "V-205"],
      "instruments": ["FIC-201", "TT-105"],
      "valves": ["HV-201"],
      "connections": [{"from": "P-101", "to": "V-205", "type": "process"}]
    }
    Do not include dimensional lines. Do not use quotes in your tag names inside the strings.
    Use standard tag formats (e.g., P-101).
    If nothing is found, return empty arrays.
    """
    
    tiles = tile_image(base64_image, tile_size=1024, overlap_pct=0.2)
    
    final_data = {
        "title_block": {
            "drawing_number": "",
            "revision": "",
            "title": "",
            "date": "",
            "unit_area": ""
        },
        "components": [],
        "connections": []
    }
    
    all_tags_found = set()
    all_connections = set()
    
    for tile in tiles:
        # Call A: Title block
        raw_title = vision_analyze(title_prompt, tile)
        match_title = re.search(r'\{.*\}', raw_title, re.DOTALL)
        clean_title = match_title.group(0) if match_title else raw_title
        try:
            title_data = json.loads(clean_title)
            # If we found a drawing number, we keep this title block
            if title_data.get("drawing_number") and not final_data["title_block"]["drawing_number"]:
                for k in final_data["title_block"].keys():
                    final_data["title_block"][k] = title_data.get(k, "")
        except json.JSONDecodeError:
            pass

        # Call B: Components & Topology (Run twice for redundancy)
        for pass_num in range(2):
            raw_comp = vision_analyze(comp_prompt, tile)
            match_comp = re.search(r'\{.*\}', raw_comp, re.DOTALL)
            clean_comp = match_comp.group(0) if match_comp else raw_comp
            try:
                comp_data = json.loads(clean_comp)
                
                # Process tags
                for category in ["equipment", "instruments", "valves"]:
                    items = comp_data.get(category, [])
                    if isinstance(items, list):
                        for tag in items:
                            tag_clean = str(tag).strip().upper()
                            if is_valid_tag(tag_clean):
                                if tag_clean not in all_tags_found:
                                    all_tags_found.add(tag_clean)
                                    final_data["components"].append({
                                        "tag": tag_clean,
                                        "type": category[:-1].capitalize() if category.endswith('s') else category.capitalize()
                                    })
                
                # Process connections
                conns = comp_data.get("connections", [])
                if isinstance(conns, list):
                    for conn in conns:
                        f = str(conn.get("from", "")).strip().upper()
                        t = str(conn.get("to", "")).strip().upper()
                        c_type = str(conn.get("type", "process")).strip()
                        
                        if is_valid_tag(f) and is_valid_tag(t):
                            conn_key = f"{f}|{t}|{c_type}"
                            if conn_key not in all_connections:
                                all_connections.add(conn_key)
                                final_data["connections"].append({
                                    "from": f,
                                    "to": t,
                                    "type": c_type
                                })
            except json.JSONDecodeError:
                pass
                
    analysis_prompt = """
    Analyze this Piping and Instrumentation Diagram (P&ID) or industrial schematic.
    Provide a detailed, high-level summary of the entire system shown in the drawing.
    Describe the main process flow, key equipment involved (e.g. pumps feeding into reactors),
    and the general purpose of this system. Keep the description technical, concise, and professional.
    Return ONLY your analysis text, without any conversational filler or JSON formatting.
    """
    
    overall_analysis = vision_analyze(analysis_prompt, base64_image)
    final_data["overall_analysis"] = overall_analysis.strip()
    
    return final_data
