from PIL import Image
import os
import math

Image.MAX_IMAGE_PIXELS = None

TILE_SIZE = 256
OVERLAP = 0
FORMAT = "jpeg"
MAX_LEVEL = 14  # Optional: auf 14 begrenzen

input_file = "mosaic_result.jpg"
output_dir = "output_files"
dzi_filename = "output.dzi"

# Bild laden
image = Image.open(input_file)
width, height = image.size

max_dim = max(width, height)
max_level = math.ceil(math.log2(max_dim))
if max_level > MAX_LEVEL:
    max_level = MAX_LEVEL

print(f"Generiere Deep Zoom Tiles (max Level: {max_level})...")

for level in range(max_level + 1):
    scale = 2 ** (max_level - level)
    level_width = math.ceil(width / scale)
    level_height = math.ceil(height / scale)
    level_img = image.resize((level_width, level_height), Image.BILINEAR)

    cols = math.ceil(level_width / TILE_SIZE)
    rows = math.ceil(level_height / TILE_SIZE)
    level_dir = os.path.join(output_dir, str(level))
    os.makedirs(level_dir, exist_ok=True)

    for row in range(rows):
        for col in range(cols):
            left = col * TILE_SIZE
            upper = row * TILE_SIZE
            right = min(left + TILE_SIZE, level_width)
            lower = min(upper + TILE_SIZE, level_height)
            tile = level_img.crop((left, upper, right, lower))
            tile_path = os.path.join(level_dir, f"{col}_{row}.{FORMAT}")
            tile.save(tile_path, FORMAT, quality=80)
    print(f"  → Ebene {level} mit {cols}x{rows} Tiles gespeichert.")

# DZI-Datei schreiben
dzi_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<Image TileSize="{TILE_SIZE}" Overlap="{OVERLAP}" Format="{FORMAT}" xmlns="http://schemas.microsoft.com/deepzoom/2008">
  <Size Width="{width}" Height="{height}"/>
</Image>
"""
with open(dzi_filename, "w") as f:
    f.write(dzi_template)

print("Fertig! Öffne das Mosaik mit OpenSeadragon über 'output.dzi'")