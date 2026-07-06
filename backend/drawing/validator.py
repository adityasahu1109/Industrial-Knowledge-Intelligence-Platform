import re

# Relaxed regex to catch more variations of tags (e.g. P-1, V100, PUMP-1, T-10A)
# Allows uppercase letters, optional hyphens, and alphanumeric suffixes
TAG_REGEX = re.compile(r'^[A-Z]{1,5}-?[A-Z0-9]{1,5}$')

def validate_and_deduplicate(components: list[dict]) -> list[dict]:
    """
    Deduplicates the extracted tags.
    """
    valid_components = []
    seen_tags = set()
    
    for comp in components:
        tag = comp.get("tag", "")
        if not isinstance(tag, str):
            continue
            
        tag = tag.strip().upper()
        
        # Must have a tag
        if not tag:
            continue
            
        if tag not in seen_tags:
            seen_tags.add(tag)
            valid_components.append({
                "tag": tag,
                "type": str(comp.get("type", "Unknown")).strip(),
                "description": str(comp.get("description", "")).strip()
            })
            
    return valid_components
