from PIL import Image
import io
import base64

def tile_image(base64_image: str, tile_size: int = 1024, overlap_pct: float = 0.2) -> list[str]:
    """
    Splits a base64 encoded image into smaller tiles with overlap.
    Returns a list of base64 encoded strings for each tile.
    """
    image_data = base64.b64decode(base64_image)
    img = Image.open(io.BytesIO(image_data))
    
    width, height = img.size
    
    # If image is smaller than tile size, just return the whole image
    if width <= tile_size and height <= tile_size:
        return [base64_image]
        
    tiles = []
    step = int(tile_size * (1.0 - overlap_pct))
    
    for y in range(0, height, step):
        for x in range(0, width, step):
            box = (x, y, min(x + tile_size, width), min(y + tile_size, height))
            tile = img.crop(box)
            
            buf = io.BytesIO()
            tile.save(buf, format="PNG")
            tiles.append(base64.b64encode(buf.getvalue()).decode('utf-8'))
            
            if x + tile_size >= width:
                break
        if y + tile_size >= height:
            break
            
    return tiles
